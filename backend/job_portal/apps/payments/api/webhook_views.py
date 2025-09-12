import hashlib
import hmac

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.decorators import GroupRequiredMixin, LogActionMixin, RateLimitMixin

from ..models import Payment, StripeWebhookEvent
from .serializers import (
    StripeWebhookEventSerializer,
    WebhookResponseSerializer,
    WebhookRetryResponseSerializer,
)


class StripeWebhookView(GroupRequiredMixin, RateLimitMixin, LogActionMixin, View):
    """Handle Stripe webhook events."""

    # Rate limiting configuration for webhooks
    max_requests = 1000
    window = 3600  # 1 hour

    # Permission groups for webhook access
    group_required = "Payment Managers"

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Process Stripe webhook events."""
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

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

        except ValueError:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
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
            # Get webhook secret from settings
            webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
            if not webhook_secret:
                return False

            # Verify signature
            expected_sig = hmac.new(
                webhook_secret.encode("utf-8"), payload, hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_sig, sig_header)

        except Exception:
            return False

    def _process_event(self, event):
        """Process Stripe webhook event."""
        try:
            # Create webhook event record
            webhook_event = StripeWebhookEvent.objects.create(
                stripe_event_id=event["id"],
                event_type=event["type"],
                event_data=event["data"],
            )

            # Process based on event type
            if event["type"] == "payment_intent.succeeded":
                return self._handle_payment_succeeded(event["data"]["object"])
            elif event["type"] == "payment_intent.payment_failed":
                return self._handle_payment_failed(event["data"]["object"])
            elif event["type"] == "charge.refunded":
                return self._handle_refund(event["data"]["object"])
            else:
                # Mark as processed for other event types
                webhook_event.processed = True
                webhook_event.processed_at = timezone.now()
                webhook_event.save()
                return True

        except Exception as e:
            # Log error
            if "webhook_event" in locals():
                webhook_event.error_message = str(e)
                webhook_event.save()
            print(f"Error processing webhook: {str(e)}")
            return False

    def _handle_payment_succeeded(self, payment_intent):
        """Handle successful payment."""
        try:
            # Find payment by Stripe payment intent ID
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent["id"],
            )

            # Update payment status
            payment.status = "completed"
            payment.processed_at = timezone.now()
            payment.save()

            # Update invoice
            invoice = payment.invoice
            invoice.status = "paid"
            invoice.paid_amount = payment.amount
            invoice.paid_date = timezone.now()
            invoice.save()

            # Mark webhook as processed
            webhook_event = StripeWebhookEvent.objects.get(
                stripe_event_id=payment_intent["id"]
            )
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            return True

        except Payment.DoesNotExist:
            print(f"Payment not found for intent: {payment_intent['id']}")
            return False
        except Exception as e:
            print(f"Error handling payment success: {str(e)}")
            return False

    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment."""
        try:
            # Find payment by Stripe payment intent ID
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent["id"],
            )

            # Update payment status
            payment.status = "failed"
            payment.failed_at = timezone.now()
            payment.error_message = payment_intent.get("last_payment_error", {}).get(
                "message", "Payment failed"
            )
            payment.save()

            # Mark webhook as processed
            webhook_event = StripeWebhookEvent.objects.get(
                stripe_event_id=payment_intent["id"]
            )
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            return True

        except Payment.DoesNotExist:
            print(f"Payment not found for intent: {payment_intent['id']}")
            return False
        except Exception as e:
            print(f"Error handling payment failure: {str(e)}")
            return False

    def _handle_refund(self, charge):
        """Handle refund."""
        try:
            # Find payment by Stripe charge ID
            payment = Payment.objects.get(
                stripe_charge_id=charge["id"],
            )

            # Update payment status
            payment.status = "refunded"
            payment.refund_amount = (
                charge["amount_refunded"] / 100
            )  # Convert from cents
            payment.refunded_at = timezone.now()
            payment.save()

            # Mark webhook as processed
            webhook_event = StripeWebhookEvent.objects.get(stripe_event_id=charge["id"])
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            return True

        except Payment.DoesNotExist:
            print(f"Payment not found for charge: {charge['id']}")
            return False
        except Exception as e:
            print(f"Error handling refund: {str(e)}")
            return False


# Simplified webhook handler for DRF
class StripeWebhookAPIView(APIView):
    """API view for Stripe webhook handling."""
    permission_classes = [AllowAny]
    serializer_class = WebhookResponseSerializer
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.stripe_webhook(request)
    
    def stripe_webhook(self, request):
        """Simple Stripe webhook handler."""
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            # Verify webhook signature
            webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
            if not webhook_secret:
                return Response({"error": "Webhook secret not configured"}, status=400)

            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

            # Create webhook event record
            webhook_event = StripeWebhookEvent.objects.create(
                stripe_event_id=event["id"],
                event_type=event["type"],
                event_data=event["data"],
            )

            # Mark as processed (basic handling)
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            response_data = {"status": "success"}
            serializer = WebhookResponseSerializer(response_data)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


# Keep the function-based view for backward compatibility
@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt
def stripe_webhook(request):
    """Simple Stripe webhook handler - function-based version."""
    view = StripeWebhookAPIView()
    return view.stripe_webhook(request)


class WebhookEventsAPIView(APIView):
    """API view for listing webhook events."""
    permission_classes = [AllowAny]
    serializer_class = StripeWebhookEventSerializer
    
    def get(self, request, *args, **kwargs):
        """List webhook events."""
        events = StripeWebhookEvent.objects.all().order_by("-created_at")[:50]
        serializer = StripeWebhookEventSerializer(events, many=True)
        return Response(serializer.data)


# Keep the function-based view for backward compatibility
@api_view(["GET"])
@permission_classes([AllowAny])
def webhook_events(request):
    """List webhook events - function-based version."""
    view = WebhookEventsAPIView()
    return view.get(request)


class RetryWebhookAPIView(APIView):
    """API view for retrying webhook events."""
    permission_classes = [AllowAny]
    serializer_class = WebhookRetryResponseSerializer
    
    def post(self, request, event_id, *args, **kwargs):
        """Retry processing a webhook event."""
        try:
            event = StripeWebhookEvent.objects.get(id=event_id)
            event.processed = False
            event.error_message = ""
            event.save()

            # Process the event again
            webhook_view = StripeWebhookView()
            success = webhook_view._process_event(
                {
                    "id": event.stripe_event_id,
                    "type": event.event_type,
                    "data": event.event_data,
                }
            )

            if success:
                response_data = {"status": "success"}
                serializer = WebhookRetryResponseSerializer(response_data)
                return Response(serializer.data)
            else:
                response_data = {"status": "failed"}
                serializer = WebhookRetryResponseSerializer(response_data)
                return Response(serializer.data, status=500)

        except StripeWebhookEvent.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# Keep the function-based view for backward compatibility
@api_view(["POST"])
@permission_classes([AllowAny])
def retry_webhook(request, event_id):
    """Retry processing a webhook event - function-based version."""
    view = RetryWebhookAPIView()
    return view.post(request, event_id)
