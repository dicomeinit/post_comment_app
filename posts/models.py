from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    auto_reply_enabled = models.BooleanField(default=False)
    reply_delay_minutes = models.IntegerField(default=5)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    blocked = models.BooleanField(default=False)
    is_auto_reply = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]
