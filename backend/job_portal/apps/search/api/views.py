from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.gis.geos import Point

from utils.permissions import AbstractIsAuthenticatedOrReadOnly
from orders.models import Order
from users.models import ServiceProviderProfile
from core.models import ServiceCategory, ServiceSubcategory


class GlobalSearchApiView(generics.ListAPIView):
    """Simple global search across all content types."""
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')
        
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = {}
        
        if search_type in ['all', 'orders']:
            results['orders'] = self.search_orders(query, request)
        
        if search_type in ['all', 'providers']:
            results['providers'] = self.search_providers(query, request)
        
        if search_type in ['all', 'services']:
            results['services'] = self.search_services(query, request)
        
        return Response({
            'query': query,
            'search_type': search_type,
            'results': results
        })
    
    def search_orders(self, query, request):
        """Search for available orders (job vacancies)."""
        orders = Order.objects.filter(
            status__in=['published', 'bidding'],
            is_deleted=False
        )
        
        # Text search
        if query:
            orders = orders.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(city__icontains=query)
            )
        
        # Apply filters
        city = request.query_params.get('city')
        if city:
            orders = orders.filter(city__iexact=city)
        
        service_category = request.query_params.get('service_category')
        if service_category:
            orders = orders.filter(service_subcategory__category_id=service_category)
        
        min_budget = request.query_params.get('min_budget')
        if min_budget:
            orders = orders.filter(budget_max__gte=float(min_budget))
        
        max_budget = request.query_params.get('max_budget')
        if max_budget:
            orders = orders.filter(budget_min__lte=float(max_budget))
        
        urgency = request.query_params.get('urgency')
        if urgency:
            orders = orders.filter(urgency=urgency)
        
        # Ordering
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering in ['budget_min', 'budget_max', 'created_at', '-created_at']:
            orders = orders.order_by(ordering)
        
        return {
            'count': orders.count(),
            'results': orders[:50]
        }
    
    def search_providers(self, query, request):
        """Search for service providers."""
        providers = ServiceProviderProfile.objects.filter(
            user_profile__is_deleted=False,
            is_available=True
        )
        
        # Text search
        if query:
            providers = providers.filter(
                Q(business_name__icontains=query) |
                Q(user_profile__user__first_name__icontains=query) |
                Q(user_profile__user__last_name__icontains=query) |
                Q(business_description__icontains=query)
            )
        
        # Apply filters
        min_rating = request.query_params.get('min_rating')
        if min_rating:
            providers = providers.filter(average_rating__gte=float(min_rating))
        
        city = request.query_params.get('city')
        if city:
            providers = providers.filter(user_profile__city__iexact=city)
        
        # Ordering
        ordering = request.query_params.get('ordering', '-average_rating')
        if ordering in ['average_rating', '-average_rating']:
            providers = providers.order_by(ordering)
        
        return {
            'count': providers.count(),
            'results': providers[:50]
        }
    
    def search_services(self, query, request):
        """Search for services and categories."""
        services = ServiceSubcategory.objects.filter(
            is_deleted=False
        )
        
        if query:
            services = services.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
        
        # Apply filters
        category = request.query_params.get('category')
        if category:
            services = services.filter(category_id=category)
        
        # Ordering
        ordering = request.query_params.get('ordering', 'sort_order')
        if ordering in ['name', 'sort_order']:
            services = services.order_by(ordering)
        
        return {
            'count': services.count(),
            'results': services[:50]
        }


class OrderSearchApiView(generics.ListAPIView):
    """Search specifically for orders (job vacancies)."""
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in orders
        orders = Order.objects.filter(
            status__in=['published', 'bidding'],
            is_deleted=False
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(city__icontains=query)
        ).select_related('service_subcategory', 'client__user_profile__user')
        
        # Apply filters
        city = request.query_params.get('city')
        if city:
            orders = orders.filter(city__iexact=city)
        
        service_category = request.query_params.get('service_category')
        if service_category:
            orders = orders.filter(service_subcategory__category_id=service_category)
        
        min_budget = request.query_params.get('min_budget')
        if min_budget:
            orders = orders.filter(budget_max__gte=float(min_budget))
        
        max_budget = request.query_params.get('max_budget')
        if max_budget:
            orders = orders.filter(budget_min__lte=float(max_budget))
        
        # Ordering
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering in ['budget_min', 'budget_max', 'created_at', '-created_at']:
            orders = orders.order_by(ordering)
        
        return Response({
            'query': query,
            'count': orders.count(),
            'results': orders[:50]
        })


class ProviderSearchApiView(generics.ListAPIView):
    """Search specifically for service providers."""
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in providers
        providers = ServiceProviderProfile.objects.filter(
            user_profile__is_deleted=False,
            is_available=True
        ).filter(
            Q(business_name__icontains=query) |
            Q(user_profile__user__first_name__icontains=query) |
            Q(user_profile__user__last_name__icontains=query) |
            Q(business_description__icontains=query)
        ).select_related('user_profile__user')
        
        # Apply filters
        min_rating = request.query_params.get('min_rating')
        if min_rating:
            providers = providers.filter(average_rating__gte=float(min_rating))
        
        city = request.query_params.get('city')
        if city:
            providers = providers.filter(user_profile__city__iexact=city)
        
        # Ordering
        ordering = request.query_params.get('ordering', '-average_rating')
        if ordering in ['average_rating', '-average_rating']:
            providers = providers.order_by(ordering)
        
        return Response({
            'query': query,
            'count': providers.count(),
            'results': providers[:50]
        })

