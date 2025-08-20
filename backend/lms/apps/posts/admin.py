from django.contrib import admin

from lms.apps.core.utils.admin import BaseAdmin
from .models import Post, Category, Tag


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = ('title', 'slug', 'publication_status',)
    list_filter = ("publication_status", 'category')
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)


# @admin.register(PostComment)
# class PostCommentAdmin(BaseAdmin):
#     list_display = ('title', 'message',)
#     search_fields = ['message']


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ('title', 'slug',)
    search_fields = ['title', ]


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    list_display = ('title',)
    search_fields = ['title', ]
