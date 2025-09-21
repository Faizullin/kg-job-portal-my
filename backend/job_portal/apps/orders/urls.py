# Django imports
from django.urls import path

# Local imports
from .api.views import (
    OrderApiView, OrderDetailApiView, OrderCreateApiView,
    BidApiView, BidCreateApiView, BidDetailApiView,
    BidAcceptApiView, BidRejectApiView, BidWithdrawApiView,
    OrderAssignmentApiView, OrderAssignmentDetailApiView
)

app_name = 'orders'

urlpatterns = [
    # Orders
    path('api/v1/orders/', OrderApiView.as_view(), name='orders'),
    path('api/v1/orders/create/', OrderCreateApiView.as_view(), name='order-create'),
    path('api/v1/orders/<int:pk>/', OrderDetailApiView.as_view(), name='order-detail'),
    
    # Bids
    path('api/v1/orders/bids/', BidApiView.as_view(), name='bids'),
    path('api/v1/orders/<int:order_id>/bids/', BidCreateApiView.as_view(), name='bid-create'),
    path('api/v1/orders/bids/<int:pk>/', BidDetailApiView.as_view(), name='bid-detail'),
    
    # Bid Actions
    path('api/v1/orders/bids/<int:bid_id>/accept/', BidAcceptApiView.as_view(), name='bid-accept'),
    path('api/v1/orders/bids/<int:bid_id>/reject/', BidRejectApiView.as_view(), name='bid-reject'),
    path('api/v1/orders/bids/<int:bid_id>/withdraw/', BidWithdrawApiView.as_view(), name='bid-withdraw'),
    
    # Order Assignments
    path('api/v1/orders/assignments/', OrderAssignmentApiView.as_view(), name='order-assignments'),
    path('api/v1/orders/assignments/<int:pk>/', OrderAssignmentDetailApiView.as_view(), name='order-assignment-detail'),
]
