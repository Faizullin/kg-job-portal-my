import stripe
import json
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from utils.decorators import GroupRequiredMixin, RateLimitMixin, LogActionMixin
from ..models import StripeWebhookEvent, Payment, PaymentMethod, Invoice
from .serializers import PaymentSerializer


class StripeWebhookView(GroupRequiredMixin, RateLimitMixin, LogActionMixin, View):
    """Handle Stripe webhook events."""
    
    # Rate limiting configuration for webhooks
    max_requests = 1000
    window = 3600  # 1 hour
    
    # Permission groups for webhook access
    group_required = 'Payment Managers'
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Process Stripe webhook events."""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            # Verify webhook signature
            if not self._verify_signature(payload, sig_header):
                return HttpResponse(status=400)
            
            # Parse event
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Process event
            success = self._process_event(event)
            
            if success:
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=500)
                
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)
        except Exception as e:
            # Log error and return 500
            print(f"Webhook error: {str(e)}")
            return HttpResponse(status=500)
    
    def _verify_signature(self, payload, sig_header):
        """Verify Stripe webhook signature."""
        if not sig_header:
            return False
        
        try:
            # Get webhook secret from settings or database
            webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
            if not webhook_secret:
                # Try to get from database
                from ..models import PaymentProvider
                try:
                    stripe_provider = PaymentProvider.objects.get(name='stripe', is_active=True)
                    webhook_secret = stripe_provider.webhook_secret
                except PaymentProvider.DoesNotExist:
                    return False
            
            # Verify signature
            expected_sig = hmac.new(
                webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_sig, sig_header)
            
        except Exception:
            return False
    
    def _process_event(self, event):
        """Process Stripe webhook event."""
        try:
            # Log event
            webhook_event = StripeWebhookEvent.objects.create(
                stripe_event_id=event['id'],
                event_type=event['type'],
                event_data=event['data']
            )
            
            # Process based on event type
            if event['type'] == 'payment_intent.succeeded':
                return self._handle_payment_succeeded(event['data']['object'])
            elif event['type'] == 'payment_intent.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            elif event['type'] == 'charge.refunded':
                return self._handle_refund_processed(event['data']['object'])
            elif event['type'] == 'customer.subscription.created':
                return self._handle_subscription_created(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                return self._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event['data']['object'])
            else:
                # Log unhandled event type
                webhook_event.error_message = f"Unhandled event type: {event['type']}"
                webhook_event.save()
                return True  # Don't fail for unhandled events
            
        except Exception as e:
            # Log error
            if 'webhook_event' in locals():
                webhook_event.error_message = str(e)
                webhook_event.retry_count += 1
                webhook_event.save()
            return False
    
    def _handle_payment_succeeded(self, payment_intent):
        """Handle successful payment."""
        try:
            # Find payment by payment_intent_id
            payment = Payment.objects.filter(
                payment_id=payment_intent['id']
            ).first()
            
            if payment:
                # Update payment status
                payment.status = 'completed'
                payment.processed_at = timezone.now()
                payment.processor_response = payment_intent
                payment.save()
                
                # Update invoice status
                invoice = payment.invoice
                invoice.status = 'paid'
                invoice.paid_amount = payment.amount
                invoice.paid_date = timezone.now()
                invoice.save()
                
                # Mark webhook as processed
                webhook_event = StripeWebhookEvent.objects.get(
                    stripe_event_id=payment_intent['id']
                )
                webhook_event.processed = True
                webhook_event.processed_at = timezone.now()
                webhook_event.save()
                
                return True
            else:
                # Payment not found - log error
                print(f"Payment not found for payment_intent: {payment_intent['id']}")
                return False
                
        except Exception as e:
            print(f"Error handling payment succeeded: {str(e)}")
            return False
    
    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment."""
        try:
            payment = Payment.objects.filter(
                payment_id=payment_intent['id']
            ).first()
            
            if payment:
                payment.status = 'failed'
                payment.failed_at = timezone.now()
                payment.error_message = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
                payment.processor_response = payment_intent
                payment.save()
                
                # Mark webhook as processed
                webhook_event = StripeWebhookEvent.objects.get(
                    stripe_event_id=payment_intent['id']
                )
                webhook_event.processed = True
                webhook_event.processed_at = timezone.now()
                webhook_event.save()
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error handling payment failed: {str(e)}")
            return False
    
    def _handle_refund_processed(self, charge):
        """Handle refund processed."""
        try:
            # Find payment by charge ID
            payment = Payment.objects.filter(
                transaction_id=charge['id']
            ).first()
            
            if payment:
                payment.status = 'refunded'
                payment.refund_amount = charge['amount_refunded'] / 100  # Convert from cents
                payment.refunded_at = timezone.now()
                payment.processor_response = charge
                payment.save()
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error handling refund: {str(e)}")
            return False
    
    def _handle_subscription_created(self, subscription):
        """Handle subscription created."""
        # For now, just log it
        return True
    
    def _handle_subscription_updated(self, subscription):
        """Handle subscription updated."""
        # For now, just log it
        return True
    
    def _handle_subscription_deleted(self, subscription):
        """Handle subscription deleted."""
        # For now, just log it
        return True


@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Alternative webhook endpoint using DRF."""
    # Note: This bypasses the permission mixins for external webhook calls
    # but still applies rate limiting and security headers
    return StripeWebhookView.as_view()(request)


@api_view(['GET'])
def webhook_events(request):
    """Get webhook events for debugging."""
    from ..models import StripeWebhookEvent
    from utils.permissions import has_group
    
    # Check permissions manually for function-based view
    if not has_group(request.user, 'Payment Managers'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to access this resource.")

    events = StripeWebhookEvent.objects.all().order_by('-created_at')[:50]

    data = []
    for event in events:
        data.append({
            'id': event.id,
            'stripe_event_id': event.stripe_event_id,
            'event_type': event.event_type,
            'processed': event.processed,
            'processed_at': event.processed_at,
            'error_message': event.error_message,
            'retry_count': event.retry_count,
            'created_at': event.created_at
        })

    return Response(data)


@api_view(['POST'])
def retry_webhook(request, event_id):
    """Retry processing a failed webhook event."""
    from utils.permissions import has_group
    
    # Check permissions manually for function-based view
    if not has_group(request.user, 'Payment Managers'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to access this resource.")
    
    try:
        event = StripeWebhookEvent.objects.get(id=event_id)

        # Reset error state
        event.error_message = ''
        event.retry_count += 1
        event.save()

        # Reprocess event
        success = StripeWebhookView()._process_event({
            'id': event.stripe_event_id,
            'type': event.event_type,
            'data': event.event_data
        })

        if success:
            return Response({'message': 'Webhook reprocessed successfully'})
        else:
            return Response({'error': 'Failed to reprocess webhook'}, status=500)

    except StripeWebhookEvent.DoesNotExist:
        return Response({'error': 'Webhook event not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
