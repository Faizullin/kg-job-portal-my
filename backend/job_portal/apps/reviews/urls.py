from django.urls import path
from .api.views import (
    ReviewApiView, ReviewDetailApiView, ProviderReviewsApiView,
    OrderReviewsApiView, ReviewAnalyticsApiView, AppFeedbackApiView
)

app_name = 'reviews'

urlpatterns = [
    # Reviews
    path('api/v1/reviews/', ReviewApiView.as_view(), name='reviews'),
    path('api/v1/reviews/<int:pk>/', ReviewDetailApiView.as_view(), name='review-detail'),
    
    # Provider-specific reviews
    path('api/v1/reviews/provider/<int:provider_id>/', ProviderReviewsApiView.as_view(), name='provider-reviews'),
    
    # Order-specific reviews
    path('api/v1/reviews/order/<int:order_id>/', OrderReviewsApiView.as_view(), name='order-reviews'),
    
    # Review analytics
    path('api/v1/reviews/analytics/', ReviewAnalyticsApiView.as_view(), name='review-analytics'),
    
    # TODO: rename url to app prefix
    # App Feedback
    path('api/v1/reviews/feedback/', AppFeedbackApiView.as_view(), name='app-feedback'),
]
