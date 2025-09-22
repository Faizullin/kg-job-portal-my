# Django imports
from django.urls import path

# Local imports
from .api.views import (
    OrderApiView, OrderDetailApiView, OrderCreateApiView,
    MyOrdersView, MyBidsView, OrderBidsView,
    BidApiView, BidCreateApiView, BidDetailApiView,
    BidAcceptApiView, BidRejectApiView, BidWithdrawApiView,
    OrderAssignmentApiView, OrderAssignmentDetailApiView,
    MyAssignmentsView, MyOrderAssignmentsView
)

app_name = 'orders'

urlpatterns = [
    # Orders (Admin)
    path('api/v1/orders/', OrderApiView.as_view(), name='orders'),
    path('api/v1/orders/create/', OrderCreateApiView.as_view(), name='order-create'),
    path('api/v1/orders/<int:pk>/', OrderDetailApiView.as_view(), name='order-detail'),
    
    # My Orders (User-specific)
    path('api/v1/orders/my/', MyOrdersView.as_view(), name='my-orders'),
    
    # Bids (Admin)
    path('api/v1/orders/bids/', BidApiView.as_view(), name='bids'),
    path('api/v1/orders/<int:order_id>/bids/', BidCreateApiView.as_view(), name='bid-create'),
    path('api/v1/orders/bids/<int:pk>/', BidDetailApiView.as_view(), name='bid-detail'),
    
    # My Bids (User-specific)
    path('api/v1/orders/my-bids/', MyBidsView.as_view(), name='my-bids'),
    path('api/v1/orders/my-orders/bids/', OrderBidsView.as_view(), name='my-order-bids'),
    
    # Bid Actions
    path('api/v1/orders/bids/<int:bid_id>/accept/', BidAcceptApiView.as_view(), name='bid-accept'),
    path('api/v1/orders/bids/<int:bid_id>/reject/', BidRejectApiView.as_view(), name='bid-reject'),
    path('api/v1/orders/bids/<int:bid_id>/withdraw/', BidWithdrawApiView.as_view(), name='bid-withdraw'),
    
    # Order Assignments (Admin)
    path('api/v1/orders/assignments/', OrderAssignmentApiView.as_view(), name='order-assignments'),
    path('api/v1/orders/assignments/<int:pk>/', OrderAssignmentDetailApiView.as_view(), name='order-assignment-detail'),
    
    # My Assignments (User-specific)
    path('api/v1/orders/my-assignments/', MyAssignmentsView.as_view(), name='my-assignments'),
    path('api/v1/orders/my-orders/assignments/', MyOrderAssignmentsView.as_view(), name='my-order-assignments'),
]
