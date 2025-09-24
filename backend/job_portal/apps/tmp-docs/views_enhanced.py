from django.db.models import Avg, Count, Q, F, Prefetch
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from utils.exceptions import StandardizedViewMixin
from utils.pagination import CustomPagination

from ..models import ServiceProviderProfile, ClientProfile, UserProfile
from ..models_enhanced import (
    PricingStructure, ProfessionalInformation, ProviderLanguage, 
    Certificate, WorkPortfolio, AvailabilityStatus, UserPreference,
    RecommendationEngine, StatisticsAggregation, Language
)
from job_portal.apps.orders.models import Order
from job_portal.apps.reviews.models import Review
from job_portal.apps.analytics.models import UserActivity
from .serializers import ServiceProviderSerializer


class ProviderStatisticsApiView(StandardizedViewMixin, APIView):
    """Get aggregated statistics for provider listings."""
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        # Get current statistics
        stats = StatisticsAggregation.objects.filter(
            date=timezone.now().date()
        ).first()
        
        if not stats:
            # Calculate real-time statistics if not cached
            stats_data = self._calculate_real_time_stats()
        else:
            stats_data = {
                'total_providers': stats.total_providers,
                'active_providers': stats.active_providers,
                'average_rating': float(stats.average_provider_rating),
                'total_reviews': stats.total_reviews,
            }
        
        return Response(stats_data)
    
    def _calculate_real_time_stats(self):
        """Calculate real-time statistics."""
        providers = ServiceProviderProfile.objects.filter(is_available=True)
        
        return {
            'total_providers': providers.count(),
            'active_providers': providers.filter(
                availability_status__status='available'
            ).count(),
            'average_rating': float(providers.aggregate(
                avg=Avg('average_rating')
            )['avg'] or 0),
            'total_reviews': Review.objects.count(),
        }


class ProviderDetailEnhancedApiView(StandardizedViewMixin, generics.RetrieveAPIView):
    """Enhanced provider detail view with all related information."""
    serializer_class = ServiceProviderSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return ServiceProviderProfile.objects.filter(
            is_available=True
        ).select_related(
            'user_profile__user',
            'professional_info',
            'availability_status'
        ).prefetch_related(
            'pricing_structures__service_subcategory',
            'languages__language',
            'certificates',
            'portfolio_items',
            'reviews_received__reviewer'
        )
    
    def retrieve(self, request, *args, **kwargs):
        provider = self.get_object()
        
        # Get pricing information
        pricing_data = []
        for pricing in provider.pricing_structures.all():
            pricing_data.append({
                'service': pricing.service_subcategory.name,
                'hourly_rate': pricing.hourly_rate,
                'daily_rate': pricing.daily_rate,
                'per_order_rate': pricing.per_order_rate,
                'currency': pricing.currency,
                'is_negotiable': pricing.is_negotiable,
            })
        
        # Get professional information
        professional_info = {}
        if hasattr(provider, 'professional_info'):
            prof_info = provider.professional_info
            professional_info = {
                'years_of_experience': prof_info.years_of_experience,
                'education_level': prof_info.get_education_level_display(),
                'education_institution': prof_info.education_institution,
                'education_field': prof_info.education_field,
                'specializations': prof_info.specializations,
            }
        
        # Get languages
        languages = []
        for provider_lang in provider.languages.all():
            languages.append({
                'name': provider_lang.language.name,
                'proficiency': provider_lang.get_proficiency_level_display(),
            })
        
        # Get certificates
        certificates = []
        for cert in provider.certificates.all():
            certificates.append({
                'name': cert.name,
                'issuing_organization': cert.issuing_organization,
                'issue_date': cert.issue_date,
                'expiry_date': cert.expiry_date,
                'is_verified': cert.is_verified,
            })
        
        # Get portfolio
        portfolio = []
        for item in provider.portfolio_items.filter(is_public=True)[:3]:
            portfolio.append({
                'title': item.title,
                'description': item.description,
                'image_url': item.image_url or (item.image.url if item.image else None),
                'completion_date': item.completion_date,
                'client_feedback': item.client_feedback,
            })
        
        # Get availability status
        availability = {}
        if hasattr(provider, 'availability_status'):
            avail = provider.availability_status
            availability = {
                'status': avail.get_status_display(),
                'current_location': avail.current_location,
                'working_hours': {
                    'start': avail.working_hours_start,
                    'end': avail.working_hours_end,
                    'days': avail.working_days,
                },
            }
        
        # Get performance statistics
        performance_stats = {
            'completed_orders': provider.assignments.count(),
            'total_reviews': provider.total_reviews,
            'average_rating': float(provider.average_rating),
            'positive_reviews_percentage': self._calculate_positive_reviews_percentage(provider),
            'repeat_customers_percentage': self._calculate_repeat_customers_percentage(provider),
        }
        
        # Serialize main provider data
        serializer = self.get_serializer(provider)
        provider_data = serializer.data
        
        # Add enhanced data
        provider_data.update({
            'pricing': pricing_data,
            'professional_info': professional_info,
            'languages': languages,
            'certificates': certificates,
            'portfolio': portfolio,
            'availability': availability,
            'performance_stats': performance_stats,
        })
        
        return Response(provider_data)
    
    def _calculate_positive_reviews_percentage(self, provider):
        """Calculate percentage of positive reviews (4+ stars)."""
        positive_reviews = provider.reviews_received.filter(overall_rating__gte=4).count()
        total_reviews = provider.reviews_received.count()
        return round((positive_reviews / total_reviews * 100) if total_reviews > 0 else 0, 1)
    
    def _calculate_repeat_customers_percentage(self, provider):
        """Calculate percentage of repeat customers."""
        # This would require more complex logic to track repeat customers
        # For now, return a placeholder
        return 45.0


class RecommendationsApiView(StandardizedViewMixin, APIView):
    """Personalized recommendations for users."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        recommendation_type = request.query_params.get('type', 'all')
        
        # Get user preferences
        user_prefs = UserPreference.objects.filter(user=user).first()
        
        recommendations = []
        
        if recommendation_type in ['all', 'providers']:
            provider_recs = self._get_provider_recommendations(user, user_prefs)
            recommendations.extend(provider_recs)
        
        if recommendation_type in ['all', 'services']:
            service_recs = self._get_service_recommendations(user, user_prefs)
            recommendations.extend(service_recs)
        
        if recommendation_type in ['all', 'trending']:
            trending_recs = self._get_trending_recommendations(user)
            recommendations.extend(trending_recs)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return Response({
            'recommendations': recommendations[:10],  # Top 10 recommendations
            'user_preferences': self._get_user_preferences_summary(user_prefs),
        })
    
    def _get_provider_recommendations(self, user, user_prefs):
        """Get personalized provider recommendations."""
        recommendations = []
        
        # Get providers based on user preferences
        providers = ServiceProviderProfile.objects.filter(
            is_available=True,
            is_verified_provider=True
        ).select_related('user_profile__user')
        
        # Apply filters based on preferences
        if user_prefs:
            if user_prefs.preferred_categories.exists():
                providers = providers.filter(
                    services_offered__category__in=user_prefs.preferred_categories.all()
                )
            
            if user_prefs.min_rating_preference:
                providers = providers.filter(
                    average_rating__gte=user_prefs.min_rating_preference
                )
            
            if user_prefs.prefer_verified_providers:
                providers = providers.filter(is_verified_provider=True)
        
        # Score providers based on various factors
        for provider in providers[:20]:  # Limit to top 20 for scoring
            score = self._calculate_provider_score(provider, user, user_prefs)
            
            if score > 0.3:  # Only include providers with decent scores
                recommendations.append({
                    'type': 'provider',
                    'id': provider.id,
                    'title': provider.business_name or f"{provider.user_profile.user.first_name} {provider.user_profile.user.last_name}",
                    'description': provider.business_description,
                    'rating': float(provider.average_rating),
                    'reviews_count': provider.total_reviews,
                    'confidence_score': score,
                    'reason': self._get_provider_recommendation_reason(provider, user_prefs),
                })
        
        return recommendations
    
    def _get_service_recommendations(self, user, user_prefs):
        """Get personalized service category recommendations."""
        recommendations = []
        
        # Get user's order history
        user_orders = Order.objects.filter(
            client__user_profile__user=user
        ).select_related('service_subcategory__category')
        
        # Find popular categories among user's orders
        category_counts = {}
        for order in user_orders:
            category = order.service_subcategory.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Recommend similar categories
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            recommendations.append({
                'type': 'service_category',
                'id': category.id,
                'title': category.name,
                'description': f"Based on your {count} previous orders",
                'confidence_score': min(0.8, count * 0.2),
                'reason': f"You've used this service {count} times",
            })
        
        return recommendations
    
    def _get_trending_recommendations(self, user):
        """Get trending/popular recommendations."""
        recommendations = []
        
        # Get trending service categories (most orders in last 30 days)
        trending_categories = Order.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('service_subcategory__category').annotate(
            order_count=Count('id')
        ).order_by('-order_count')[:5]
        
        for trend in trending_categories:
            category_id = trend['service_subcategory__category']
            order_count = trend['order_count']
            
            recommendations.append({
                'type': 'trending_service',
                'id': category_id,
                'title': f"Trending Service Category",
                'description': f"{order_count} orders in the last 30 days",
                'confidence_score': min(0.7, order_count * 0.01),
                'reason': "Popular choice among users",
            })
        
        return recommendations
    
    def _calculate_provider_score(self, provider, user, user_prefs):
        """Calculate recommendation score for a provider."""
        score = 0.0
        
        # Base score from rating
        score += float(provider.average_rating) * 0.2
        
        # Bonus for verified providers
        if provider.is_verified_provider:
            score += 0.1
        
        # Bonus for high review count
        if provider.total_reviews > 10:
            score += 0.1
        
        # Location bonus (if user has location preferences)
        if user_prefs and user_prefs.preferred_cities:
            if provider.user_profile.city in user_prefs.preferred_cities:
                score += 0.2
        
        # Service category bonus
        if user_prefs and user_prefs.preferred_categories.exists():
            if provider.services_offered.filter(
                category__in=user_prefs.preferred_categories.all()
            ).exists():
                score += 0.2
        
        return min(1.0, score)
    
    def _get_provider_recommendation_reason(self, provider, user_prefs):
        """Get human-readable reason for provider recommendation."""
        reasons = []
        
        if provider.is_verified_provider:
            reasons.append("Verified provider")
        
        if provider.average_rating >= 4.5:
            reasons.append("Highly rated")
        
        if provider.total_reviews > 20:
            reasons.append("Many reviews")
        
        if user_prefs and provider.user_profile.city in user_prefs.preferred_cities:
            reasons.append("In your preferred location")
        
        return ", ".join(reasons) if reasons else "Good match for you"
    
    def _get_user_preferences_summary(self, user_prefs):
        """Get summary of user preferences."""
        if not user_prefs:
            return {"message": "No preferences set yet"}
        
        return {
            "preferred_categories": [cat.name for cat in user_prefs.preferred_categories.all()],
            "preferred_cities": user_prefs.preferred_cities,
            "min_rating_preference": float(user_prefs.min_rating_preference),
            "prefer_verified": user_prefs.prefer_verified_providers,
        }


class DashboardStatisticsApiView(StandardizedViewMixin, APIView):
    """Dashboard statistics for mobile app."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Get user-specific statistics
        user_stats = self._get_user_statistics(user)
        
        # Get global statistics
        global_stats = self._get_global_statistics()
        
        # Get personalized recommendations
        recommendations = self._get_quick_recommendations(user)
        
        return Response({
            'user_statistics': user_stats,
            'global_statistics': global_stats,
            'recommendations': recommendations,
        })
    
    def _get_user_statistics(self, user):
        """Get user-specific statistics."""
        stats = {}
        
        # Check if user is a client
        try:
            client_profile = user.job_portal_profile.client_profile
            stats['client'] = {
                'total_orders': client_profile.total_orders,
                'completed_orders': client_profile.completed_orders,
                'cancelled_orders': client_profile.cancelled_orders,
                'favorite_providers_count': client_profile.favorite_providers.count(),
            }
        except:
            stats['client'] = None
        
        # Check if user is a service provider
        try:
            provider_profile = user.job_portal_profile.service_provider_profile
            stats['provider'] = {
                'average_rating': float(provider_profile.average_rating),
                'total_reviews': provider_profile.total_reviews,
                'completed_orders': provider_profile.assignments.count(),
                'is_available': provider_profile.is_available,
                'is_verified': provider_profile.is_verified_provider,
            }
        except:
            stats['provider'] = None
        
        return stats
    
    def _get_global_statistics(self):
        """Get global platform statistics."""
        # Try to get cached statistics first
        stats = StatisticsAggregation.objects.filter(
            date=timezone.now().date()
        ).first()
        
        if stats:
            return {
                'total_providers': stats.total_providers,
                'active_providers': stats.active_providers,
                'total_clients': stats.total_clients,
                'total_orders': stats.total_orders,
                'completed_orders': stats.completed_orders,
                'average_rating': float(stats.average_provider_rating),
                'total_reviews': stats.total_reviews,
            }
        
        # Calculate real-time if not cached
        return {
            'total_providers': ServiceProviderProfile.objects.filter(is_available=True).count(),
            'active_providers': ServiceProviderProfile.objects.filter(
                is_available=True,
                availability_status__status='available'
            ).count(),
            'total_clients': ClientProfile.objects.count(),
            'total_orders': Order.objects.count(),
            'completed_orders': Order.objects.filter(status='completed').count(),
            'average_rating': float(ServiceProviderProfile.objects.aggregate(
                avg=Avg('average_rating')
            )['avg'] or 0),
            'total_reviews': Review.objects.count(),
        }
    
    def _get_quick_recommendations(self, user):
        """Get quick recommendations for dashboard."""
        # Get top 3 recommendations
        recommendations = RecommendationEngine.objects.filter(
            user=user,
            is_dismissed=False
        ).order_by('-confidence_score')[:3]
        
        return [
            {
                'type': rec.recommendation_type,
                'title': rec.reason,
                'confidence': float(rec.confidence_score),
            }
            for rec in recommendations
        ]


class ServiceProviderSearchEnhancedApiView(StandardizedViewMixin, generics.ListAPIView):
    """Enhanced search for service providers with advanced filtering."""
    serializer_class = ServiceProviderSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_verified_provider', 'is_available']
    search_fields = [
        'business_name', 
        'user_profile__user__first_name', 
        'user_profile__user__last_name',
        'business_description',
        'services_offered__name',
        'services_offered__category__name'
    ]
    ordering_fields = ['average_rating', 'total_reviews', 'created_at']
    ordering = ['-average_rating', '-total_reviews']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        """Enhanced queryset with all related data."""
        queryset = ServiceProviderProfile.objects.filter(
            is_available=True
        ).select_related(
            'user_profile__user',
            'professional_info',
            'availability_status'
        ).prefetch_related(
            'pricing_structures__service_subcategory',
            'languages__language',
            'certificates',
            'portfolio_items',
            'services_offered__category',
            'service_areas'
        )
        
        # Apply additional filters
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(user_profile__city__iexact=city)
        
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(average_rating__gte=min_rating)
        
        service_category = self.request.query_params.get('service_category')
        if service_category:
            queryset = queryset.filter(services_offered__category_id=service_category)
        
        max_distance = self.request.query_params.get('max_distance')
        if max_distance:
            # This would require geolocation filtering
            # For now, just filter by city
            pass
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Enhanced list response with statistics."""
        queryset = self.get_queryset()
        
        # Get statistics for the filtered results
        stats = {
            'total_providers': queryset.count(),
            'average_rating': float(queryset.aggregate(avg=Avg('average_rating'))['avg'] or 0),
            'verified_providers': queryset.filter(is_verified_provider=True).count(),
            'total_reviews': queryset.aggregate(total=Count('reviews_received'))['total'] or 0,
        }
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'results': serializer.data,
                'statistics': stats,
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'statistics': stats,
        })
