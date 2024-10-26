from threading import Timer
from typing import List

from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth as AuthBearer

from .models import Comment, Post
from .schemas import (
    CommentResponseSchema,
    ContentSchema,
    DateRangeQuery,
    PostResponseSchema,
    PostSchema,
)
from .utils import auto_reply
from .validators import check_for_profanity, validate_and_parse_date

router = Router(tags=["posts"])


@router.get("", auth=AuthBearer(), response=List[PostSchema])
def get_posts(request):
    posts = Post.objects.filter(author=request.auth)
    return posts


@router.post("", auth=AuthBearer(), response=PostResponseSchema)
def create_post(request, payload: PostSchema):
    if check_for_profanity(payload.content):
        raise HttpError(400, "Content contains inappropriate language")

    post = Post.objects.create(
        author=request.auth,
        title=payload.title,
        content=payload.content,
        auto_reply_enabled=payload.auto_reply_enabled,
        reply_delay_minutes=payload.reply_delay_minutes,
    )

    if payload.auto_reply_enabled:
        Timer(payload.reply_delay_minutes * 60, auto_reply, args=(request, post.id)).start()

    return PostResponseSchema.from_model(post)


@router.get("{post_id}", auth=AuthBearer(), response=PostResponseSchema)
def get_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    return PostResponseSchema(
        post_id=post.id,
        author=request.auth,
        title=post.title,
        content=post.content,
        auto_reply_enabled=post.auto_reply_enabled,
        reply_delay_minutes=post.reply_delay_minutes,
    )


@router.put("{post_id}/", auth=AuthBearer(), response=PostResponseSchema)
def update_post(request, post_id: int, payload: PostSchema):
    post = get_object_or_404(Post, id=post_id, author=request.auth)
    post.title = payload.title
    post.content = payload.content
    post.auto_reply_enabled = payload.auto_reply_enabled
    post.reply_delay_minutes = payload.reply_delay_minutes
    post.save()
    return PostResponseSchema(
        post_id=post.id,
        author=request.auth,
        title=post.title,
        content=post.content,
        auto_reply_enabled=post.auto_reply_enabled,
        reply_delay_minutes=post.reply_delay_minutes,
    )


@router.delete("{post_id}/", auth=AuthBearer())
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id, author=request.auth)
    post.delete()
    return {"status": "OK"}


@router.post("{post_id}/comments", auth=AuthBearer(), response=CommentResponseSchema)
def add_comment(request, post_id: int, payload: ContentSchema):
    post = get_object_or_404(Post, id=post_id)
    if check_for_profanity(payload.content):
        raise HttpError(400, "Content contains inappropriate language")
    comment = Comment.objects.create(post=post, author=request.auth, content=payload.content)
    return CommentResponseSchema.from_model(comment)


@router.get("{post_id}/comments", auth=AuthBearer(), response=List[CommentResponseSchema])
def get_comments(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().select_related("author")

    serialized_comments = [CommentResponseSchema.from_model(comment) for comment in comments]
    return serialized_comments


@router.delete("{post_id}/comments/{comment_id}", auth=AuthBearer())
def delete_comment(request, post_id: int, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id, author=request.auth)
    comment.delete()
    return {"status": "OK"}


@router.get("analytics/comments_daily_breakdown", response={200: dict}, auth=AuthBearer())
def comments_daily_breakdown(request, filters: DateRangeQuery = Query(...)):
    date_from = validate_and_parse_date(filters.date_from)
    date_to = validate_and_parse_date(filters.date_to)
    comments = Comment.objects.filter(created_at__date__range=(date_from, date_to))

    daily_stats = (
        comments.extra({"day": "date(created_at)"})
        .values("day")
        .annotate(
            total_comments=Count("id"),
            blocked_comments=Count("id", filter=Q(blocked=True)),
        )
        .order_by("day")
    )

    return JsonResponse({"daily_breakdown": list(daily_stats)}, status=200)
