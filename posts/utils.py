from django.shortcuts import get_object_or_404

from .ai_model import get_model
from .models import Comment, Post


def generate_auto_reply(post_content: str, comment_content: str) -> str:
    prompt = f"Generate a relevant reply for a comment '{comment_content}' on the post '{post_content}'."
    response = get_model().generate_content(prompt)
    return response.text


def auto_reply(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    for comment in comments:
        reply_content = generate_auto_reply(post.content, comment.content)
        Comment.objects.create(post=post, author=request.auth, content=reply_content, is_auto_reply=True)
