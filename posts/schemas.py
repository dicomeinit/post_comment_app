from ninja import Field, Schema

from users.schemas import UserSchema

from .models import Comment, Post


class ContentSchema(Schema):
    content: str


class PostSchema(Schema):
    title: str
    content: str
    auto_reply_enabled: bool = False
    reply_delay_minutes: int = 0


class CommentSchema(Schema):
    content: str


class AutoReplySchema(Schema):
    reply_delay_minutes: int


class DateRangeQuery(Schema):
    date_from: str = Field(None, description="Start date in YYYY-MM-DD format")
    date_to: str = Field(None, description="End date in YYYY-MM-DD format")


class PostResponseSchema(Schema):
    post_id: int
    author: UserSchema
    title: str
    content: str
    auto_reply_enabled: bool = False
    reply_delay_minutes: int = 0

    @classmethod
    def from_model(cls, post: Post):
        return cls(
            post_id=post.id,
            author=UserSchema(id=post.author.id, username=post.author.username),
            title=post.title,
            content=post.content,
            auto_reply_enabled=post.auto_reply_enabled,
            reply_delay_minutes=post.reply_delay_minutes,
        )


class CommentResponseSchema(Schema):
    comment_id: int
    post_id: int
    author: UserSchema
    content: str
    created_at: str
    blocked: bool
    is_auto_reply: bool

    @classmethod
    def from_model(cls, comment: Comment):
        return cls(
            comment_id=comment.id,
            post_id=comment.post.id,
            author=UserSchema(id=comment.author.id, username=comment.author.username),
            content=comment.content,
            created_at=comment.created_at.isoformat(),
            blocked=comment.blocked,
            is_auto_reply=comment.is_auto_reply,
        )
