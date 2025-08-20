from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from . import views
from .api import views as api_views

# from .editor_v2.urls import urlpatterns as editor_v2_urls
from .editor_v3.urls import urlpatterns as editor_v3_urls

router = DefaultRouter()
router.register(
    r"api/v1/lms/resources/posts", api_views.ResourcesPostViewSet, basename="post"
)
router.register(
    r"api/v1/lms/resources/categories",
    api_views.ResourcesCategoryViewSet,
    basename="category",
)

urlpatterns = [
    path("", include(router.urls)),
    re_path(
        r"api/v1/lms/resources/protected-media/(?P<path>.*)$",
        views.ProtectedMediaLoadView.as_view(),
    ),
] + editor_v3_urls
