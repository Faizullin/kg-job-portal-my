from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import views as api_views

router = DefaultRouter()
router.register(
    r"api/v1/lms/resources/editor-v3/template-components", api_views.TemplateComponentApiViewSet,
    basename="template-component"
)
router.register(
    r"api/v1/lms/resources/editor-v3/vimeo-components", 
    api_views.VimeoUrlCacheApiViewSet,
    basename="vimeo-component"
)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "api/v1/lms/resources/editor-v3/action/",
        api_views.ResourcesLessonEditActionAPIView.as_view(),
        name="resources-lesson-edit-action"
    ),
    path('api/v1/lms/resources/editor-v3/attachments/', api_views.MediaLibAttachmentListApiView.as_view(),
         name='media-lib-attachment-list'),
    path('api/v1/lms/resources/editor-v3/attachments/<int:pk>/',
         api_views.MediaLibAttachmentDetailDestroyApiView.as_view(),
         name='media-lib-attachment-detail-destroy'),
    path('api/v1/lms/resources/editor-v3/attachments/upload/',
         api_views.MediaLibAttachmentUploadApiView.as_view(),
         name='media-lib-attachment-upload'),
]
