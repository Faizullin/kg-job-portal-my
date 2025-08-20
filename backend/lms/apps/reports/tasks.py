import json
import time

from django.contrib.auth import get_user_model
from django.utils import timezone

from lms.apps.posts.models import Post
from lms.apps.reports.lesson_page_element_component_use import (
    collect as collect_lesson_page,
)
from lms.apps.reports.storage_files_use import collect as collect_storage_files

UserModel = get_user_model()


def lesson_page_element_component_use(record_name, user):
    context = {
        "name": record_name,
        "timestamp": {
            "start": timezone.now().isoformat(),
        },
    }
    start = time.time()
    result = collect_lesson_page()
    end = time.time()
    context["data"] = result
    context["timestamp"]["end"] = timezone.now().isoformat()
    context["timestamp"]["duration"] = end - start
    post_obj = Post.objects.create(
        title=f"Report for {record_name} [{start}]",
        content=json.dumps(context),
        post_type="report",
        author=user,
    )
    post_obj.title = f"Report for {record_name} [#{post_obj.id}]"
    post_obj.save()
    return post_obj


def storage_files_use(record_name, user):
    context = {
        "name": record_name,
        "timestamp": {
            "start": timezone.now().isoformat(),
        },
    }
    start = time.time()
    result = collect_storage_files()
    end = time.time()
    context["data"] = result
    context["timestamp"]["end"] = timezone.now().isoformat()
    context["timestamp"]["duration"] = end - start
    post_obj = Post.objects.create(
        title=f"Report for {record_name} [{start}]",
        content=json.dumps(context),
        post_type="report",
        author=user,
    )
    post_obj.title = f"Report for {record_name} [#{post_obj.id}]"
    post_obj.save()
    return post_obj


def start_recording(record_name: str, user_id: int):
    user = UserModel.objects.get(id=user_id)
    func_map = {
        "lesson_page_element_component_use": lesson_page_element_component_use,
        "storage_files_use": storage_files_use,
    }
    if record_name in func_map:
        return func_map[record_name](record_name, user)
    raise ValueError(f"Unknown report name: {record_name}")
