from django.urls import path

from .api.views import (
    AddReviewForJobDoneAPIView,
    DeleteReviewForJobDoneAPIView,
    EditReviewForJobDoneAPIView,
    MyReviewsListAPIView,
)

app_name = "reviews"

urlpatterns = [
    path("api/v1/jobs/<int:job_id>/reviews/", AddReviewForJobDoneAPIView.as_view(), name="review-create"),
    path("api/v1/reviews/my/", MyReviewsListAPIView.as_view(), name="my-reviews"),
    path("api/v1/reviews/<int:pk>/", EditReviewForJobDoneAPIView.as_view(), name="review-update"),
    path("api/v1/reviews/<int:pk>/delete/", DeleteReviewForJobDoneAPIView.as_view(), name="review-delete"),
]
