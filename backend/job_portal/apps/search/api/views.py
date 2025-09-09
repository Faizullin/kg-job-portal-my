from django.db.models import Q
from job_portal.apps.core.models import ServiceSubcategory
from job_portal.apps.orders.models import Order
from job_portal.apps.orders.api.serializers import OrderSerializer
from job_portal.apps.users.models import ServiceProviderProfile
from job_portal.apps.users.api.serializers import ServiceProviderSerializer
from rest_framework import generics, serializers, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter, ChoiceFilter
from utils.permissions import AbstractIsAuthenticatedOrReadOnly
from utils.pagination import CustomPagination


class OrderSearchFilter(FilterSet):
    """Custom filter for order search with specific query parameters."""
    q = CharFilter(method='filter_search', help_text='Search query')
    city = CharFilter(field_name='city', lookup_expr='iexact', help_text='Filter by city')
    service_category = NumberFilter(field_name='service_subcategory__category_id', help_text='Filter by service category ID')
    min_budget = NumberFilter(field_name='budget_max', lookup_expr='gte', help_text='Minimum budget')
    max_budget = NumberFilter(field_name='budget_min', lookup_expr='lte', help_text='Maximum budget')
    urgency = ChoiceFilter(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], help_text='Filter by urgency level')
    
    def filter_search(self, queryset, name, value):
        """Custom search filter for orders."""
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value) |
                Q(location__icontains=value) |
                Q(city__icontains=value)
            )
        return queryset
    
    class Meta:
        model = Order
        fields = ['q', 'city', 'service_category', 'min_budget', 'max_budget', 'urgency']


class ProviderSearchFilter(FilterSet):
    """Custom filter for provider search with specific query parameters."""
    q = CharFilter(method='filter_search', help_text='Search query')
    city = CharFilter(field_name='user_profile__city', lookup_expr='iexact', help_text='Filter by city')
    min_rating = NumberFilter(field_name='average_rating', lookup_expr='gte', help_text='Minimum rating')
    
    def filter_search(self, queryset, name, value):
        """Custom search filter for providers."""
        if value:
            return queryset.filter(
                Q(business_name__icontains=value) |
                Q(user_profile__user__first_name__icontains=value) |
                Q(user_profile__user__last_name__icontains=value) |
                Q(business_description__icontains=value)
            )
        return queryset
    
    class Meta:
        model = ServiceProviderProfile
        fields = ['q', 'city', 'min_rating']


class GlobalSearchResponseSerializer(serializers.Serializer):
    """Serializer for global search response."""

    query = serializers.CharField(help_text="Search query")
    search_type = serializers.CharField(help_text="Type of search performed")
    results = serializers.DictField(help_text="Search results by category")


class OrderSearchResponseSerializer(serializers.Serializer):
    """Serializer for order search response."""

    query = serializers.CharField(help_text="Search query")
    count = serializers.IntegerField(help_text="Number of results found")
    results = OrderSerializer(many=True, help_text="List of order results")


class ProviderSearchResponseSerializer(serializers.Serializer):
    """Serializer for provider search response."""

    query = serializers.CharField(help_text="Search query")
    count = serializers.IntegerField(help_text="Number of results found")
    results = ServiceProviderSerializer(many=True, help_text="List of provider results")


class GlobalSearchFilter(FilterSet):
    """Custom filter for global search with specific query parameters."""
    q = CharFilter(method='filter_search', help_text='Search query')
    type = ChoiceFilter(
        choices=[('all', 'All'), ('orders', 'Orders'), ('providers', 'Providers'), ('services', 'Services')],
        help_text='Type of search to perform'
    )
    city = CharFilter(help_text='Filter by city')
    service_category = NumberFilter(help_text='Filter by service category ID')
    min_budget = NumberFilter(help_text='Minimum budget')
    max_budget = NumberFilter(help_text='Maximum budget')
    urgency = ChoiceFilter(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        help_text='Filter by urgency level'
    )
    min_rating = NumberFilter(help_text='Minimum rating for providers')
    
    def filter_search(self, queryset, name, value):
        """Custom search filter - this will be handled in the view."""
        return queryset
    
    class Meta:
        model = Order  # Base model for the filter
        fields = ['q', 'type', 'city', 'service_category', 'min_budget', 'max_budget', 'urgency', 'min_rating']


class GlobalSearchApiView(generics.ListAPIView):
    """Simple global search across all content types."""

    serializer_class = GlobalSearchResponseSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = GlobalSearchFilter
    ordering_fields = ['created_at', 'budget_min', 'budget_max', 'average_rating']
    ordering = ['-created_at']
    pagination_class = CustomPagination

    def get_queryset(self):
        # Return a base queryset - the actual filtering will be done in list()
        return Order.objects.none()

    def list(self, request, *args, **kwargs):
        # Get validated query parameters from the filter
        filterset = self.filterset_class(request.query_params, queryset=self.get_queryset())
        if not filterset.is_valid():
            return Response(
                {"error": "Invalid query parameters", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        validated_data = filterset.form.cleaned_data
        query = validated_data.get("q", "")
        
        if not query:
            return Response(
                {"error": "Search query 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        search_type = validated_data.get("type", "all")
        
        results = {}
        
        if search_type in ["all", "orders"]:
            results["orders"] = self.search_orders(query, validated_data)

        if search_type in ["all", "providers"]:
            results["providers"] = self.search_providers(query, validated_data)

        if search_type in ["all", "services"]:
            results["services"] = self.search_services(query, validated_data)

        response_data = {"query": query, "search_type": search_type, "results": results}
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)

    def search_orders(self, query, validated_data):
        """Search for available orders (job vacancies)."""
        orders = Order.objects.filter(
            status__in=["published", "bidding"], is_deleted=False
        ).select_related(
            "service_subcategory",
            "service_subcategory__category",
            "client__user_profile__user"
        ).prefetch_related(
            "addons__addon",
            "photos",
            "bids__provider__user_profile__user"
        )
        
        # Text search
        if query:
            orders = orders.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(location__icontains=query)
                | Q(city__icontains=query)
            )

        # Apply filters using validated data
        if "city" in validated_data and validated_data["city"] is not None:
            orders = orders.filter(city__iexact=validated_data["city"])

        if "service_category" in validated_data and validated_data["service_category"] is not None:
            orders = orders.filter(service_subcategory__category_id=validated_data["service_category"])

        if "min_budget" in validated_data and validated_data["min_budget"] is not None:
            orders = orders.filter(budget_max__gte=validated_data["min_budget"])

        if "max_budget" in validated_data and validated_data["max_budget"] is not None:
            orders = orders.filter(budget_min__lte=validated_data["max_budget"])

        if "urgency" in validated_data and validated_data["urgency"] is not None:
            orders = orders.filter(urgency=validated_data["urgency"])
        
        # Ordering
        ordering = validated_data.get("ordering", "-created_at")
        if ordering in ["budget_min", "budget_max", "created_at", "-created_at"]:
            orders = orders.order_by(ordering)
        
        # Serialize the orders
        order_serializer = OrderSerializer(orders[:50], many=True)
        return {"count": orders.count(), "results": order_serializer.data}

    def search_providers(self, query, validated_data):
        """Search for service providers."""
        providers = ServiceProviderProfile.objects.filter(
            user_profile__is_deleted=False, is_available=True
        ).select_related(
            "user_profile__user",
            "user_profile__preferred_language"
        ).prefetch_related(
            "services__subcategory",
            "services__subcategory__category",
            "services__available_addons"
        )
        
        # Text search
        if query:
            providers = providers.filter(
                Q(business_name__icontains=query)
                | Q(user_profile__user__first_name__icontains=query)
                | Q(user_profile__user__last_name__icontains=query)
                | Q(business_description__icontains=query)
            )

        # Apply filters using validated data
        if "min_rating" in validated_data and validated_data["min_rating"] is not None:
            providers = providers.filter(average_rating__gte=validated_data["min_rating"])

        if "city" in validated_data and validated_data["city"] is not None:
            providers = providers.filter(user_profile__city__iexact=validated_data["city"])
        
        # Ordering
        ordering = validated_data.get("ordering", "-average_rating")
        if ordering in ["average_rating", "-average_rating"]:
            providers = providers.order_by(ordering)
        
        # Serialize the providers
        provider_serializer = ServiceProviderSerializer(providers[:50], many=True)
        return {"count": providers.count(), "results": provider_serializer.data}

    def search_services(self, query, validated_data):
        """Search for services and categories."""
        services = ServiceSubcategory.objects.filter(is_deleted=False)
        
        if query:
            services = services.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
            )

        # Apply filters using validated data
        if "service_category" in validated_data and validated_data["service_category"] is not None:
            services = services.filter(category_id=validated_data["service_category"])
        
        # Ordering
        ordering = validated_data.get("ordering", "sort_order")
        if ordering in ["name", "sort_order"]:
            services = services.order_by(ordering)
        
        return {"count": services.count(), "results": services[:50]}


class OrderSearchApiView(generics.ListAPIView):
    """Search specifically for orders (job vacancies)."""
    serializer_class = OrderSearchResponseSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderSearchFilter
    ordering_fields = ['created_at', 'budget_min', 'budget_max', 'service_date']
    ordering = ['-created_at']
    pagination_class = CustomPagination

    def get_queryset(self):
        return Order.objects.filter(
            status__in=["published", "bidding"], 
            is_deleted=False
        ).select_related(
            "service_subcategory",
            "service_subcategory__category",  # For service category details
            "client__user_profile__user"      # For client_name in serializer
        ).prefetch_related(
            "addons__addon",                  # For OrderAddonSerializer.addon_name
            "photos",                         # For OrderPhotoSerializer
            "bids__provider__user_profile__user"  # For BidSerializer.provider_name
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            order_serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(order_serializer.data)
        
        order_serializer = OrderSerializer(queryset, many=True)
        response_data = {
            "query": request.query_params.get("q", ""),
            "count": queryset.count(),
            "results": order_serializer.data
        }
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)


class ProviderSearchApiView(generics.ListAPIView):
    """Search specifically for service providers."""
    serializer_class = ProviderSearchResponseSerializer
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProviderSearchFilter
    ordering_fields = ['average_rating', 'total_reviews', 'created_at']
    ordering = ['-average_rating']
    pagination_class = CustomPagination

    def get_queryset(self):
        return ServiceProviderProfile.objects.filter(
            user_profile__is_deleted=False,
            is_available=True
        ).select_related(
            "user_profile__user",           # For user details in serializer
            "user_profile__preferred_language"  # For language preferences
        ).prefetch_related(
            "services__subcategory",        # For service provider services
            "services__subcategory__category",  # For service categories
            "services__available_addons"    # For available addons
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            provider_serializer = ServiceProviderSerializer(page, many=True)
            return self.get_paginated_response(provider_serializer.data)
        
        provider_serializer = ServiceProviderSerializer(queryset, many=True)
        response_data = {
            "query": request.query_params.get("q", ""),
            "count": queryset.count(),
            "results": provider_serializer.data
        }
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)
