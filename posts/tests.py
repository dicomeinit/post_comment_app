from datetime import timedelta
from unittest.mock import ANY, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from ninja.testing.client import TestClient
from ninja_jwt.tokens import RefreshToken

from .models import Comment, Post
from .routes import router


class CommonPostAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        username = "testuser"
        password = "#StrongPass1"
        cls.username = username
        cls.password = password
        cls.user = User.objects.create_user(username=username, password=password)
        cls.client = TestClient(router_or_app=router)
        cls.post_url = "/api/posts/"
        cls.post = Post.objects.create(author=cls.user, title="Test Post", content="Test Content")
        refresh = RefreshToken.for_user(cls.user)
        cls.access_token = str(refresh.access_token)


class PostAPITestCase(CommonPostAPITestCase):
    def test_get_posts(self):
        """Tests retrieving all posts created by the logged-in user."""
        Post.objects.create(author=self.user, title="Second Post", content="Another test content")

        response = self.client.get(
            self.post_url,
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertEqual(len(response_data), 2)
        post_titles = {post["title"] for post in response_data}

        self.assertIn("Test Post", post_titles)
        self.assertIn("Second Post", post_titles)

    def test_create_post_without_profanity_and_auto_reply(self):
        """Tests creating a post without profanity and with auto-reply disabled."""
        response = self.client.post(
            self.post_url,
            {
                "title": "New Post",
                "content": "New Content",
                "auto_reply_enabled": False,
                "reply_delay_minutes": 0,
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, 200, response.json())

        response_data = response.json()
        self.assertEqual(response_data["title"], "New Post")
        self.assertEqual(response_data["content"], "New Content")
        self.assertEqual(response_data["auto_reply_enabled"], False)
        self.assertEqual(response_data["reply_delay_minutes"], 0)
        self.assertIn("author", response_data)
        self.assertIn("post_id", response_data)

        post = Post.objects.get(id=response_data["post_id"])
        self.assertEqual(post.title, "New Post")
        self.assertEqual(post.content, "New Content")
        self.assertFalse(post.auto_reply_enabled)
        self.assertEqual(post.reply_delay_minutes, 0)

    def test_create_post_with_auto_reply_enabled(self):
        """Tests creating a post with auto-reply enabled."""
        with patch("posts.routes.Timer") as mock_timer:
            response = self.client.post(
                self.post_url,
                {
                    "title": "Auto-reply Post",
                    "content": "This is a test post",
                    "auto_reply_enabled": True,
                    "reply_delay_minutes": 1,
                },
                content_type="application/json",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("post_id", response.json())
            post_id = response.json()["post_id"]

            post = Post.objects.get(id=post_id)
            self.assertTrue(post.auto_reply_enabled)
            self.assertEqual(post.reply_delay_minutes, 1)

            mock_timer.assert_called_once_with(1 * 60, ANY, args=(ANY, post.id))

    @patch("posts.validators.check_for_profanity")
    def test_create_post_with_profanity(self, mock_check_for_profanity):
        """Test post creation fails when profanity is detected."""
        mock_check_for_profanity.return_value = True

        response = self.client.post(
            self.post_url,
            {
                "title": "New Post",
                "content": "This contains profanity",
                "auto_reply_enabled": False,
                "reply_delay_minutes": 0,
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_get_post(self):
        """Test retrieving a post by ID."""
        response = self.client.get(
            f"{self.post_url}{self.post.id}",
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.post.title)

    def test_update_post(self):
        """Test updating a post's title and content."""
        response = self.client.put(
            f"{self.post_url}{self.post.id}/",
            {"title": "Updated Post", "content": "Updated Content"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Post")

    def test_delete_post(self):
        """Test deleting a post."""
        response = self.client.delete(
            f"{self.post_url}{self.post.id}/",
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())


class CommentAPITestCase(CommonPostAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.comment_url = f"/api/posts/{cls.post.id}/comments"

    def test_add_comment_without_profanity(self):
        """Tests adding a comment without profanity to a post."""
        response = self.client.post(
            self.comment_url,
            {"content": "This is a clean comment"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertIn("comment_id", response_data)
        self.assertIn("post_id", response_data)
        self.assertIn("author", response_data)
        self.assertIn("content", response_data)
        self.assertIn("created_at", response_data)
        self.assertIn("blocked", response_data)
        self.assertIn("is_auto_reply", response_data)

        self.assertEqual(response_data["content"], "This is a clean comment")
        self.assertFalse(response_data["blocked"])
        self.assertFalse(response_data["is_auto_reply"])

    @patch("posts.validators.check_for_profanity")
    def test_add_comment_with_profanity(self, mock_check_for_profanity):
        """Tests adding a comment with profanity and expects it to be blocked."""
        mock_check_for_profanity.return_value = True

        response = self.client.post(
            self.comment_url,
            {"content": "fuck"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_get_comments(self):
        """Tests retrieving comments for a specific post."""
        Comment.objects.create(post=self.post, author=self.user, content="Test Comment")

        response = self.client.get(
            self.comment_url,
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 1)

        self.assertEqual(response_data[0]["content"], "Test Comment")

    def test_delete_comment(self):
        """Tests deleting a comment."""
        comment = Comment.objects.create(post=self.post, author=self.user, content="Test Comment")
        response = self.client.delete(
            f"{self.comment_url}/{comment.id}",
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())


class CommentProfanityTestCase(CommonPostAPITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.comment_url = "/api/posts/{post_id}/comments"

    @patch("posts.ai_model.get_model")
    def test_add_comment_with_profanity(self, mock_generate_content):
        mock_generate_content.return_value.text = "Yes"
        response = self.client.post(
            self.comment_url.format(post_id=self.post.id),
            {"content": "fuck"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    @patch("posts.ai_model.get_model")
    def test_add_comment_without_profanity(self, mock_generate_content):
        mock_generate_content.return_value.text = "No"

        response = self.client.post(
            self.comment_url.format(post_id=self.post.id),
            {"content": "This is a nice comment."},
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("comment_id", response.json())


class CommentsAnalyticsTestCase(CommonPostAPITestCase):
    def test_comments_daily_breakdown(self):
        """Tests retrieving a daily breakdown of comments on posts."""
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content="Test Comment 1",
            created_at=timezone.now() - timedelta(days=5),
            blocked=False,
        )
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content="Test Comment 2",
            created_at=timezone.now() - timedelta(days=2),
            blocked=True,
        )

        date_from = (timezone.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        date_to = timezone.now().strftime("%Y-%m-%d")

        response = self.client.get(
            f"/api/posts/analytics/comments_daily_breakdown?date_from={date_from}&date_to={date_to}",
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("daily_breakdown", data)
        breakdown = data["daily_breakdown"]
        self.assertGreater(len(breakdown), 0)
        for day_data in breakdown:
            self.assertIn("day", day_data)
            self.assertIn("total_comments", day_data)
            self.assertIn("blocked_comments", day_data)
