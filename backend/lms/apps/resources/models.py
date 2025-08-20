from lms.apps.core.utils.abstract_models import (
    AbstractTimestampedModel,
    models,
    get_truncated_name,
)
from lms.apps.posts.models import Post
from django.utils.translation import gettext_lazy as _
import requests
from django.utils.dateparse import parse_datetime
from django.conf import settings


class TemplateComponent(AbstractTimestampedModel):
    """Template for page components"""

    title = models.CharField(
        max_length=100,
        verbose_name="Title",
        help_text="Title of the component template",
    )
    content = models.TextField(
        verbose_name="Content",
        help_text="Template content for the component",
    )
    component_type = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    posts = models.ManyToManyField(
        Post,
        verbose_name="Posts",
        help_text="Posts that use this component template",
        related_name="component_templates",
        blank=True,
    )

    class Meta:
        verbose_name = "Component Template"
        verbose_name_plural = "Component Templates"

    def __str__(self):
        return f"{get_truncated_name(self.title)} [#{self.pk}]"


class VimeoUrlCacheModel(AbstractTimestampedModel):
    vimeo_link = models.URLField(verbose_name="Link", max_length=1024)
    playable_video_link = models.URLField(verbose_name="Playable Link", max_length=1024)
    expire_time = models.DateTimeField(verbose_name="Expiration time")

    class Meta:
        verbose_name = "Vimeo Link Cache"
        verbose_name_plural = "Vimeo Link Caches"


def get_video_data_from_vimeo(video_id):
    url = f"https://api.vimeo.com/videos/{video_id}?fields=play"
    headers = {"Authorization": "Bearer " + settings.VIMEO_ACCESS_TOKEN}
    response = requests.get(url, headers=headers)
    response_json = response.json()
    response.raise_for_status()  # Ensure we raise an error for bad responses
    if not response_json.get("play", False):
        raise ValueError("No playable video found in the response")
    return response_json


def get_video_link_from_vimeo(vimeo_link):
    """
    Get playable video link from Vimeo, caching the result.
    If the link is cached and not expired, return the cached link.
    Otherwise, fetch the video data from Vimeo and cache it.
    """
    vimeo_id = vimeo_link.split("/")[-1]
    new_response_json = get_video_data_from_vimeo(vimeo_id)
    progressive = new_response_json["play"]["progressive"]
    video = [video for video in progressive if video["rendition"] == "1080p"][0]
    expire_time = parse_datetime(video["link_expiration_time"])
    print("updated to ", {"link": video["link"], "expire_time": expire_time} )
    return {"link": video["link"], "expire_time": expire_time}
