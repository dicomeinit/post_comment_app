from django.contrib import admin

from .models import Comment, Post


class PostAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "title",
        "content",
        "created_at",
        "auto_reply_enabled",
        "reply_delay_minutes",
    ]
    search_fields = ["title"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "content", "created_at", "blocked"]
    search_fields = ["content"]


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
