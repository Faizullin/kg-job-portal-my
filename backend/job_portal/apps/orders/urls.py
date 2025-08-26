from django.urls import path
from .api.views import (
    OrderApiView, OrderDetailApiView, OrderCreateApiView, OrderAddonApiView,
    OrderPhotoApiView, BidApiView, BidCreateApiView, OrderDisputeApiView,
    OrderDisputeCreateApiView, OrderDisputeDetailApiView
)

app_name = 'orders'

urlpatterns = [
    # Orders
    path('api/v1/orders/', OrderApiView.as_view(), name='orders'),
    path('api/v1/orders/create/', OrderCreateApiView.as_view(), name='order-create'),
    path('api/v1/orders/<int:pk>/', OrderDetailApiView.as_view(), name='order-detail'),
    
    # Order Add-ons
    path('api/v1/orders/addons/', OrderAddonApiView.as_view(), name='order-addons'),
    
    # Order Photos
    path('api/v1/orders/photos/', OrderPhotoApiView.as_view(), name='order-photos'),
    
    # Bids
    path('api/v1/orders/bids/', BidApiView.as_view(), name='bids'),
    path('api/v1/orders/<int:order_id>/bids/', BidCreateApiView.as_view(), name='bid-create'),
    
    # Order Disputes
    path('api/v1/orders/disputes/', OrderDisputeApiView.as_view(), name='order-disputes'),
    path('api/v1/orders/<int:order_id>/disputes/', OrderDisputeCreateApiView.as_view(), name='order-dispute-create'),
    path('api/v1/orders/disputes/<int:pk>/', OrderDisputeDetailApiView.as_view(), name='order-dispute-detail'),
]
