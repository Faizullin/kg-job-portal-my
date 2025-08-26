from django.urls import path
from .api.views import (
    PaymentApiView, PaymentDetailApiView, PaymentCreateApiView, PaymentMethodApiView,
    PaymentMethodDetailApiView, PaymentMethodCreateApiView,
    InvoiceApiView, InvoiceDetailApiView, InvoiceCreateApiView
)
from .api.webhook_views import (
    StripeWebhookView, stripe_webhook, webhook_events, retry_webhook
)

app_name = 'payments'

urlpatterns = [
    # Payments
    path('api/v1/payments/', PaymentApiView.as_view(), name='payments'),
    path('api/v1/payments/create/', PaymentCreateApiView.as_view(), name='payment-create'),
    path('api/v1/payments/<int:pk>/', PaymentDetailApiView.as_view(), name='payment-detail'),
    
    # Payment Methods
    path('api/v1/payments/methods/', PaymentMethodApiView.as_view(), name='payment-methods'),
    path('api/v1/payments/methods/create/', PaymentMethodCreateApiView.as_view(), name='payment-method-create'),
    path('api/v1/payments/methods/<int:pk>/', PaymentMethodDetailApiView.as_view(), name='payment-method-detail'),
    
    # Invoices
    path('api/v1/payments/invoices/', InvoiceApiView.as_view(), name='invoices'),
    path('api/v1/payments/invoices/create/', InvoiceCreateApiView.as_view(), name='invoice-create'),
    path('api/v1/payments/invoices/<int:pk>/', InvoiceDetailApiView.as_view(), name='invoice-detail'),
    
    # Stripe Webhooks
    path('api/v1/payments/webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('api/v1/payments/webhooks/stripe/drf/', stripe_webhook, name='stripe-webhook-drf'),
    
    # Webhook Management
    path('api/v1/payments/webhooks/events/', webhook_events, name='webhook-events'),
    path('api/v1/payments/webhooks/events/<int:event_id>/retry/', retry_webhook, name='retry-webhook'),
]
