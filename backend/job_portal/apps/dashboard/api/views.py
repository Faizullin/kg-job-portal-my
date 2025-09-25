from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, F, Count
from drf_spectacular.utils import extend_schema, OpenApiResponse
from utils.exceptions import StandardizedViewMixin
from utils.permissions import HasServiceProviderProfile

from job_portal.apps.core.models import ServiceCategory
from job_portal.apps.users.models import ServiceProviderProfile
from job_portal.apps.orders.models import Order
from job_portal.apps.reviews.models import Review


class ClientDashboardApiView(StandardizedViewMixin, APIView):
    """Client dashboard API - provides data specific to clients."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get client dashboard data",
        description="Retrieve dashboard data specific to clients including top providers, service categories, and recent orders.",
        responses={
            200: OpenApiResponse(description="Client dashboard data retrieved successfully"),
            401: OpenApiResponse(description="Authentication required"),
            500: OpenApiResponse(description="Internal server error")
        },
        tags=["Dashboard"],
        operation_id="client_dashboard"
    )
    def get(self, request):
        """Get client dashboard data."""
        try:
            user = request.user
            
            # Get featured service categories
            featured_categories = ServiceCategory.objects.filter(
                featured=True,
                is_active=True
            ).order_by('sort_order')[:6]
            
            # Get top service providers
            top_providers = ServiceProviderProfile.objects.filter(
                is_available=True,
                is_top_master=True
            ).select_related('user_profile__user').prefetch_related('statistics')[:10]
            
            # Get client's recent orders
            client_profile = getattr(user, 'job_portal_profile', None)
            recent_orders = []
            if client_profile and hasattr(client_profile, 'client_profile'):
                recent_orders = Order.objects.filter(
                    client=client_profile.client_profile
            ).order_by('-created_at')[:5]
            
            # Get platform statistics
            stats = self.get_client_stats()
            
            response_data = {
                'user_info': {
                    'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                    'location': 'Алматы',  # TODO: Get from user profile
                },
                'featured_categories': self.serialize_categories(featured_categories),
                'top_providers': self.serialize_providers(top_providers),
                'recent_orders': self.serialize_orders(recent_orders),
                'platform_stats': stats,
                'action_cards': [
                    {
                        'title': 'Найти специалиста',
                        'description': 'Выберите мастера из 1000+',
                        'icon': 'users',
                        'color': 'blue',
                        'href': '/service-providers'
                    },
                    {
                        'title': 'Все услуги',
                        'description': 'Изучите все категории',
                        'icon': 'settings',
                        'color': 'green',
                        'href': '/search'
                    },
                    {
                        'title': 'Создать заявку',
                        'description': 'Опишите что вам требуется выполнить',
                        'icon': 'plus',
                        'color': 'yellow',
                        'href': '/orders/create'
                    }
                ]
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to load client dashboard data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_stats(self):
        """Get client-specific platform statistics."""
        try:
            total_providers = ServiceProviderProfile.objects.filter(is_available=True).count()
            total_categories = ServiceCategory.objects.filter(is_active=True).count()
            avg_rating = Review.objects.aggregate(avg_rating=Avg('overall_rating'))['avg_rating'] or 0
            
            return {
                'total_providers': total_providers,
                'total_categories': total_categories,
                'average_rating': round(float(avg_rating), 2),
                'response_time': '2 часа'
            }
        except Exception:
            return {
                'total_providers': 0,
                'total_categories': 0,
                'average_rating': 0.0,
                'response_time': '2 часа'
            }
    
    def serialize_providers(self, providers):
        """Serialize service providers."""
        return [
            {
                'id': provider.id,
                'name': f"{provider.user_profile.user.first_name} {provider.user_profile.user.last_name}".strip() or provider.user_profile.user.username,
                'profession': provider.profession.name if provider.profession else 'Специалист',
                'rating': provider.statistics.average_rating if hasattr(provider, 'statistics') else 0.0,
                'reviews_count': provider.statistics.total_reviews if hasattr(provider, 'statistics') else 0,
                'hourly_rate': f"{provider.hourly_rate}₸/час" if provider.hourly_rate else "Цена договорная",
                'is_online': provider.is_online,
                'avatar': provider.user_profile.user.photo_url,
                'location': provider.current_location or 'Бишкек',
            }
            for provider in providers
        ]
    
    def serialize_orders(self, orders):
        """Serialize orders."""
        return [
            {
                'id': order.id,
                'title': order.title,
                'status': order.status,
                'created_at': order.created_at,
                'estimated_price': str(order.estimated_price) if order.estimated_price else None,
            }
            for order in orders
        ]
    
    def serialize_categories(self, categories):
        """Serialize service categories."""
        return [
            {
                'id': category.id,
                'name': category.name,
                'icon': category.icon,
                'color': category.color,
                'description': category.description
            }
            for category in categories
        ]
    

class ProviderDashboardApiView(StandardizedViewMixin, APIView):
    """Provider dashboard API - provides data specific to service providers."""
    permission_classes = [IsAuthenticated, HasServiceProviderProfile]
    
    @extend_schema(
        summary="Get provider dashboard data",
        description="Retrieve dashboard data specific to service providers including statistics, portfolio, reviews, and professional information.",
        responses={
            200: OpenApiResponse(description="Provider dashboard data retrieved successfully"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Service provider profile required"),
            500: OpenApiResponse(description="Internal server error")
        },
        tags=["Dashboard"],
        operation_id="provider_dashboard"
    )
    def get(self, request):
        """Get provider dashboard data."""
        try:
            user = request.user
            provider_profile = user.job_portal_profile.service_provider_profile
            
            # Get provider statistics
            stats = self.get_provider_stats(provider_profile)
            
            # Get recent reviews
            recent_reviews = Review.objects.filter(
                order__service_provider=provider_profile
            ).select_related('order__client__user_profile__user').order_by('-created_at')[:5]
            
            # Get portfolio items (if exists)
            portfolio = []  # TODO: Implement portfolio model
            
            # Get skills
            skills = []  # TODO: Implement skills model
            
            # Get certificates
            certificates = []  # TODO: Implement certificates model
            
            # Get professional information
            professional_info = {
                'work_experience': provider_profile.work_experience or '',
                'education': provider_profile.education or '',
                'education_years': provider_profile.education_years or '',
                'languages': provider_profile.languages.split(',') if provider_profile.languages else [],
                'about': provider_profile.about or '',
            }
            
            response_data = {
                'provider_info': {
                    'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                    'profession': provider_profile.profession.name if provider_profile.profession else 'Специалист',
                    'is_top_master': provider_profile.is_top_master,
                    'is_verified': provider_profile.is_verified,
                    'avatar': user.photo_url,
                    'location': provider_profile.current_location or 'Бишкек',
                    'is_online': provider_profile.is_online,
                },
                'statistics': stats,
                'recent_reviews': self.serialize_reviews(recent_reviews),
                'portfolio': portfolio,
                'skills': skills,
                'certificates': certificates,
                'professional_info': professional_info,
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to load provider dashboard data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_provider_stats(self, provider_profile):
        """Get provider-specific statistics."""
        try:
            # Get total orders
            total_orders = Order.objects.filter(service_provider=provider_profile).count()
            
            # Get total reviews
            total_reviews = Review.objects.filter(order__service_provider=provider_profile).count()
            
            # Get average rating (not used in response but calculated for future use)
            # avg_rating = Review.objects.filter(
            #     order__service_provider=provider_profile
            # ).aggregate(avg_rating=Avg('overall_rating'))['avg_rating'] or 0
            
            # Get on-time percentage
            completed_orders = Order.objects.filter(
                service_provider=provider_profile,
                status='completed'
            ).count()
            
            on_time_orders = Order.objects.filter(
                service_provider=provider_profile,
                status='completed',
                completed_at__lte=F('deadline')
            ).count()
            
            on_time_percentage = (on_time_orders / completed_orders * 100) if completed_orders > 0 else 0
            
            # Get repeat customer percentage
            unique_clients = Order.objects.filter(
                service_provider=provider_profile
            ).values('client').distinct().count()
            
            repeat_clients = Order.objects.filter(
                service_provider=provider_profile
            ).values('client').annotate(
                order_count=Count('id')
            ).filter(order_count__gt=1).count()
            
            repeat_customer_percentage = (repeat_clients / unique_clients * 100) if unique_clients > 0 else 0
            
            return {
                'total_orders': total_orders,
                'total_reviews': total_reviews,
                'on_time_percentage': round(on_time_percentage, 1),
                'repeat_customer_percentage': round(repeat_customer_percentage, 1),
                'completed_jobs': completed_orders,
                'hourly_rate': f"{provider_profile.hourly_rate}₸/час" if provider_profile.hourly_rate else "Цена договорная",
                'response_time': provider_profile.response_time or "24 часа",
            }
        except Exception:
            return {
                'total_orders': 0,
                'total_reviews': 0,
                'on_time_percentage': 0.0,
                'repeat_customer_percentage': 0.0,
                'completed_jobs': 0,
                'hourly_rate': "Цена договорная",
                'response_time': "24 часа",
            }
    
    def serialize_reviews(self, reviews):
        """Serialize reviews."""
        return [
            {
                'id': review.id,
                'client_name': f"{review.order.client.user_profile.user.first_name} {review.order.client.user_profile.user.last_name}".strip() or review.order.client.user_profile.user.username,
                'rating': review.overall_rating,
                'comment': review.comment,
                'created_at': review.created_at,
                'client_avatar': review.order.client.user_profile.user.photo_url,
            }
            for review in reviews
        ]