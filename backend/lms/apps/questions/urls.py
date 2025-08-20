from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import views as api_views

router = DefaultRouter()
router.register(
    r"api/v1/lms/questions/questions", api_views.QuestionViewSet, basename="question"
)

urlpatterns = [
    path("", include(router.urls)),
    path("api/v1/lms/questions/user-submit/", api_views.QuestionPublicUserSubmitApiView.as_view(), name="question-public-user-submit-api"),
]
