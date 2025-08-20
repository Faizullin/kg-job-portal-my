from django.contrib import admin

from lms.apps.core.utils.admin import BaseAdmin
from .models import TemplateComponent, VimeoUrlCacheModel


@admin.register(TemplateComponent)
class TemplateComponentAdmin(BaseAdmin):
    list_display = ("title", "component_type", "is_active", "created_at", "updated_at")
    search_fields = [
        "title",
    ]


@admin.register(VimeoUrlCacheModel)
class VimeoUrlCacheModelAdmin(BaseAdmin):
    list_display = ("vimeo_link", "created_at", "updated_at")
    search_fields = ["vimeo_link"]
    list_filter = ("created_at",)
