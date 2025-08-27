# Elasticsearch Integration Guide for KG Job Portal

This document outlines the integration of Elasticsearch with the KG Job Portal Django backend to enhance search capabilities and performance.

## 🎯 **Why Elasticsearch for Job Portal?**

### **Current Search Limitations:**
- **Simple Text Matching**: Basic `icontains` queries
- **No Relevance Scoring**: Results not ranked by importance
- **Limited Filtering**: Basic Django ORM filtering
- **Performance Issues**: Database queries can be slow with large datasets
- **No Fuzzy Search**: Exact text matching only
- **No Search Analytics**: Can't track search behavior

### **Elasticsearch Benefits:**
- **Relevance-Based Results**: Smart ranking of search results
- **Fast Performance**: Sub-second response times
- **Advanced Queries**: Complex search with multiple criteria
- **Fuzzy Matching**: Handles typos and partial matches
- **Geospatial Search**: Location-based queries with radius
- **Real-Time Updates**: Immediate search index updates
- **Search Analytics**: Track and optimize search performance

## 🏗️ **Integration Architecture**

### **High-Level Architecture:**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Django App    │    │   Elasticsearch  │    │   PostgreSQL    │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Search API  │◄┼────┼►│ Search Index │ │    │ │ Data Store │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│                 │    │                  │     │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Indexing    │◄┼────┼►│ Document     │ │    │ │ Sync       │ │
│ │ Service     │ │    │ │ Management   │ │    │ │ Service    │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Data Flow:**
1. **Data Creation/Update**: Django models save to PostgreSQL
2. **Indexing**: Data automatically synced to Elasticsearch
3. **Search Requests**: API calls routed to Elasticsearch
4. **Results**: Elasticsearch returns ranked, relevant results
5. **Response**: Django API returns formatted results to client

## 📦 **Required Dependencies**

### **Python Packages:**
```bash
pip install elasticsearch-dsl
pip install elasticsearch
pip install django-elasticsearch-dsl
pip install celery  # For background indexing
```

### **System Requirements:**
- **Elasticsearch 8.x**: Latest stable version
- **Java 17+**: Required for Elasticsearch
- **Minimum 2GB RAM**: For Elasticsearch node
- **Docker**: Optional, for easy deployment

## 🔧 **Implementation Steps**

### **Step 1: Elasticsearch Setup**

#### **Option A: Docker (Recommended for Development)**
```yaml
# docker-compose.elasticsearch.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

volumes:
  elasticsearch_data:
```

#### **Option B: Local Installation**
```bash
# Download and install Elasticsearch
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
cd elasticsearch-8.11.0
./bin/elasticsearch
```

### **Step 2: Django Configuration**

#### **Settings Configuration:**
```python
# backend/backend/settings/base.py

# Elasticsearch Configuration
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    }
}

# Search Configuration
SEARCH_INDEX_PREFIX = 'kg_job_portal'
ELASTICSEARCH_TIMEOUT = 30
ELASTICSEARCH_MAX_RETRIES = 3
```

#### **Environment Variables:**
```bash
# .env
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_USE_SSL=false
```

### **Step 3: Create Search Documents**

#### **Order Search Document:**
```python
# backend/job_portal/apps/search/documents.py
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from orders.models import Order

@registry.register_document
class OrderDocument(Document):
    # Basic fields
    title = fields.TextField(
        analyzer='standard',
        fields={'raw': fields.KeywordField()}
    )
    description = fields.TextField(analyzer='standard')
    location = fields.TextField(analyzer='standard')
    city = fields.KeywordField()
    state = fields.KeywordField()
    
    # Numeric fields
    budget_min = fields.FloatField()
    budget_max = fields.FloatField()
    urgency = fields.KeywordField()
    
    # Date fields
    created_at = fields.DateField()
    deadline = fields.DateField()
    
    # Relationships
    service_category = fields.TextField(
        attr='service_subcategory.category.name',
        analyzer='standard'
    )
    service_subcategory = fields.TextField(
        attr='service_subcategory.name',
        analyzer='standard'
    )
    
    # Client information
    client_name = fields.TextField(
        attr='client.user_profile.user.get_full_name',
        analyzer='standard'
    )
    
    # Status and availability
    status = fields.KeywordField()
    is_active = fields.BooleanField()
    
    # Location for geospatial search
    location_coords = fields.GeoPointField(
        attr='location_coords_field'
    )
    
    class Index:
        name = 'orders'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'custom_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'stop', 'snowball']
                    }
                }
            }
        }
    
    class Django:
        model = Order
        fields = [
            'id',
            'status',
            'budget_min',
            'budget_max',
            'urgency',
            'created_at',
            'deadline',
            'is_active',
        ]
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def location_coords_field(self, obj):
        """Convert location to GeoPoint format."""
        if obj.latitude and obj.longitude:
            return {
                'lat': float(obj.latitude),
                'lon': float(obj.longitude)
            }
        return None
```

#### **Provider Search Document:**
```python
# backend/job_portal/apps/search/documents.py
from users.models import ServiceProviderProfile

@registry.register_document
class ProviderDocument(Document):
    # Basic information
    business_name = fields.TextField(
        analyzer='standard',
        fields={'raw': fields.KeywordField()}
    )
    business_description = fields.TextField(analyzer='standard')
    
    # User information
    first_name = fields.TextField(
        attr='user_profile.user.first_name',
        analyzer='standard'
    )
    last_name = fields.TextField(
        attr='user_profile.user.last_name',
        analyzer='standard'
    )
    
    # Location
    city = fields.KeywordField()
    state = fields.KeywordField()
    country = fields.KeywordField()
    
    # Skills and services
    services = fields.NestedField(properties={
        'name': fields.TextField(analyzer='standard'),
        'category': fields.TextField(analyzer='standard'),
        'experience_years': fields.IntegerField()
    })
    
    # Ratings and reviews
    average_rating = fields.FloatField()
    total_reviews = fields.IntegerField()
    
    # Availability
    is_available = fields.BooleanField()
    response_time = fields.IntegerField()  # in hours
    
    # Location coordinates
    location_coords = fields.GeoPointField(
        attr='location_coords_field'
    )
    
    class Index:
        name = 'providers'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    
    class Django:
        model = ServiceProviderProfile
        fields = [
            'id',
            'average_rating',
            'total_reviews',
            'is_available',
            'response_time',
        ]
    
    def get_queryset(self):
        return super().get_queryset().filter(
            user_profile__is_deleted=False
        )
    
    def location_coords_field(self, obj):
        """Convert location to GeoPoint format."""
        if obj.user_profile.latitude and obj.user_profile.longitude:
            return {
                'lat': float(obj.user_profile.latitude),
                'lon': float(obj.user_profile.longitude)
            }
        return None
```

### **Step 4: Update Search Views**

#### **Enhanced Global Search:**
```python
# backend/job_portal/apps/search/api/views.py
from elasticsearch_dsl import Q as ES_Q
from elasticsearch_dsl.query import MultiMatch, Range, Term, GeoDistance
from ..documents import OrderDocument, ProviderDocument

class ElasticsearchGlobalSearchApiView(generics.ListAPIView):
    """Enhanced global search using Elasticsearch."""
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')
        
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = {}
        
        if search_type in ['all', 'orders']:
            results['orders'] = self.search_orders_elasticsearch(query, request)
        
        if search_type in ['all', 'providers']:
            results['providers'] = self.search_providers_elasticsearch(query, request)
        
        return Response({
            'query': query,
            'search_type': search_type,
            'results': results
        })
    
    def search_orders_elasticsearch(self, query, request):
        """Search orders using Elasticsearch."""
        # Build search query
        search = OrderDocument.search()
        
        # Text search with multiple fields
        if query:
            text_query = MultiMatch(
                query=query,
                fields=['title^3', 'description^2', 'location^2', 'service_category^2'],
                type='best_fields',
                fuzziness='AUTO'
            )
            search = search.query(text_query)
        
        # Apply filters
        filters = []
        
        # City filter
        city = request.query_params.get('city')
        if city:
            filters.append(Term(city=city.lower()))
        
        # Service category filter
        service_category = request.query_params.get('service_category')
        if service_category:
            filters.append(Term(service_category=service_category))
        
        # Budget range filter
        min_budget = request.query_params.get('min_budget')
        max_budget = request.query_params.get('max_budget')
        if min_budget or max_budget:
            budget_filter = {}
            if min_budget:
                budget_filter['gte'] = float(min_budget)
            if max_budget:
                budget_filter['lte'] = float(max_budget)
            filters.append(Range(budget_max=budget_filter))
        
        # Urgency filter
        urgency = request.query_params.get('urgency')
        if urgency:
            filters.append(Term(urgency=urgency))
        
        # Location-based filtering
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', 50)  # Default 50km
        
        if lat and lng:
            location_filter = GeoDistance(
                location_coords={
                    'lat': float(lat),
                    'lon': float(lng)
                },
                distance=f'{radius}km'
            )
            filters.append(location_filter)
        
        # Apply all filters
        if filters:
            search = search.filter('bool', must=filters)
        
        # Ordering
        ordering = request.query_params.get('ordering', '_score')
        if ordering == 'budget_min':
            search = search.sort('budget_min')
        elif ordering == 'budget_max':
            search = search.sort('budget_max')
        elif ordering == 'created_at':
            search = search.sort('-created_at')
        elif ordering == 'deadline':
            search = search.sort('deadline')
        else:
            # Default: relevance score
            search = search.sort('_score')
        
        # Execute search
        response = search[:50].execute()
        
        return {
            'count': response.hits.total.value,
            'results': [hit.to_dict() for hit in response.hits],
            'took': response.took,
            'max_score': response.hits.max_score
        }
    
    def search_providers_elasticsearch(self, query, request):
        """Search providers using Elasticsearch."""
        search = ProviderDocument.search()
        
        # Text search
        if query:
            text_query = MultiMatch(
                query=query,
                fields=['business_name^3', 'business_description^2', 'first_name^2', 'last_name^2'],
                type='best_fields',
                fuzziness='AUTO'
            )
            search = search.query(text_query)
        
        # Apply filters
        filters = []
        
        # Rating filter
        min_rating = request.query_params.get('min_rating')
        if min_rating:
            filters.append(Range(average_rating={'gte': float(min_rating)}))
        
        # City filter
        city = request.query_params.get('city')
        if city:
            filters.append(Term(city=city.lower()))
        
        # Service category filter
        service_category = request.query_params.get('service_category')
        if service_category:
            filters.append(Term(services__category=service_category))
        
        # Location-based filtering
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', 50)
        
        if lat and lng:
            location_filter = GeoDistance(
                location_coords={
                    'lat': float(lat),
                    'lon': float(lng)
                },
                distance=f'{radius}km'
            )
            filters.append(location_filter)
        
        # Apply filters
        if filters:
            search = search.filter('bool', must=filters)
        
        # Ordering
        ordering = request.query_params.get('ordering', '_score')
        if ordering == 'average_rating':
            search = search.sort('-average_rating')
        elif ordering == 'response_time':
            search = search.sort('response_time')
        else:
            # Default: relevance score
            search = search.sort('_score')
        
        # Execute search
        response = search[:50].execute()
        
        return {
            'count': response.hits.total.value,
            'results': [hit.to_dict() for hit in response.hits],
            'took': response.took,
            'max_score': response.hits.max_score
        }
```

### **Step 5: Indexing Service**

#### **Automatic Indexing:**
```python
# backend/job_portal/apps/search/services.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from orders.models import Order
from users.models import ServiceProviderProfile
from .documents import OrderDocument, ProviderDocument

@receiver(post_save, sender=Order)
def index_order(sender, instance, **kwargs):
    """Index order when saved."""
    if not instance.is_deleted:
        OrderDocument.update(instance)
    else:
        OrderDocument.get(id=instance.id).delete()

@receiver(post_delete, sender=Order)
def delete_order_index(sender, instance, **kwargs):
    """Remove order from index when deleted."""
    try:
        OrderDocument.get(id=instance.id).delete()
    except:
        pass

@receiver(post_save, sender=ServiceProviderProfile)
def index_provider(sender, instance, **kwargs):
    """Index provider when saved."""
    if not instance.user_profile.is_deleted:
        ProviderDocument.update(instance)
    else:
        ProviderDocument.get(id=instance.id).delete()

@receiver(post_delete, sender=ServiceProviderProfile)
def delete_provider_index(sender, instance, **kwargs):
    """Remove provider from index when deleted."""
    try:
        ProviderDocument.get(id=instance.id).delete()
    except:
        pass
```

#### **Bulk Indexing Management:**
```python
# backend/job_portal/apps/search/management/commands/rebuild_index.py
from django.core.management.base import BaseCommand
from django_elasticsearch_dsl.management.commands import search_index
from orders.models import Order
from users.models import ServiceProviderProfile

class Command(BaseCommand):
    help = 'Rebuild Elasticsearch index for all data'
    
    def handle(self, *args, **options):
        self.stdout.write('Rebuilding Elasticsearch index...')
        
        # Rebuild orders index
        self.stdout.write('Indexing orders...')
        for order in Order.objects.filter(is_deleted=False):
            OrderDocument.update(order)
        
        # Rebuild providers index
        self.stdout.write('Indexing providers...')
        for provider in ServiceProviderProfile.objects.filter(
            user_profile__is_deleted=False
        ):
            ProviderDocument.update(provider)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully rebuilt Elasticsearch index')
        )
```

### **Step 6: Search Analytics**

#### **Search Analytics Model:**
```python
# backend/job_portal/apps/search/models.py
from django.db import models
from utils.abstract_models import AbstractTimestampedModel

class SearchAnalytics(AbstractTimestampedModel):
    """Track search performance and user behavior."""
    query = models.CharField(max_length=500)
    search_type = models.CharField(max_length=20)
    results_count = models.PositiveIntegerField()
    response_time = models.PositiveIntegerField()  # milliseconds
    user = models.ForeignKey('accounts.UserModel', null=True, blank=True, on_delete=models.SET_NULL)
    filters_applied = models.JSONField(default=dict)
    clicked_result = models.BooleanField(default=False)
    result_position = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Search Analytics'
        verbose_name_plural = 'Search Analytics'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Search: '{self.query}' - {self.results_count} results in {self.response_time}ms"
```

#### **Analytics API:**
```python
# backend/job_portal/apps/search/api/views.py
class SearchAnalyticsApiView(generics.ListAPIView):
    """Get search analytics and performance metrics."""
    permission_classes = [AbstractIsAuthenticatedOrReadOnly]
    
    def get(self, request, *args, **kwargs):
        # Get search performance metrics
        total_searches = SearchAnalytics.objects.count()
        avg_response_time = SearchAnalytics.objects.aggregate(
            avg_time=models.Avg('response_time')
        )['avg_time'] or 0
        
        # Get popular search terms
        popular_queries = SearchAnalytics.objects.values('query').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]
        
        # Get search type distribution
        search_type_distribution = SearchAnalytics.objects.values('search_type').annotate(
            count=models.Count('id')
        ).order_by('-count')
        
        # Get click-through rates
        total_clicks = SearchAnalytics.objects.filter(clicked_result=True).count()
        click_through_rate = (total_clicks / total_searches * 100) if total_searches > 0 else 0
        
        return Response({
            'performance': {
                'total_searches': total_searches,
                'average_response_time': round(avg_response_time, 2),
                'click_through_rate': round(click_through_rate, 2)
            },
            'popular_queries': popular_queries,
            'search_type_distribution': search_type_distribution
        })
```

## 🚀 **Deployment Considerations**

### **Production Setup:**
1. **Multiple Elasticsearch Nodes**: For high availability
2. **Load Balancer**: Distribute search requests
3. **Monitoring**: Elasticsearch monitoring with Kibana
4. **Backup Strategy**: Regular index snapshots
5. **Security**: Enable authentication and SSL

### **Performance Optimization:**
1. **Index Sharding**: Distribute data across multiple shards
2. **Replica Configuration**: Configure appropriate replicas
3. **Memory Allocation**: Optimize JVM heap size
4. **Query Optimization**: Use appropriate analyzers and mappings
5. **Caching**: Implement search result caching

### **Scaling Strategy:**
1. **Horizontal Scaling**: Add more Elasticsearch nodes
2. **Data Partitioning**: Split indices by time or region
3. **CDN Integration**: Cache search results globally
4. **Async Processing**: Background indexing for large datasets

## 📊 **Monitoring and Maintenance**

### **Health Checks:**
```python
# backend/job_portal/apps/search/health.py
from elasticsearch import Elasticsearch
from django.conf import settings

def check_elasticsearch_health():
    """Check Elasticsearch cluster health."""
    try:
        es = Elasticsearch([settings.ELASTICSEARCH_DSL['default']['hosts']])
        health = es.cluster.health()
        
        return {
            'status': health['status'],
            'cluster_name': health['cluster_name'],
            'number_of_nodes': health['number_of_nodes'],
            'active_shards': health['active_shards'],
            'relocating_shards': health['relocating_shards'],
            'initializing_shards': health['initializing_shards'],
            'unassigned_shards': health['unassigned_shards']
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
```

### **Index Management:**
```python
# backend/job_portal/apps/search/management/commands/manage_index.py
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from django.conf import settings

class Command(BaseCommand):
    help = 'Manage Elasticsearch indices'
    
    def add_arguments(self, parser):
        parser.add_argument('action', choices=['create', 'delete', 'status'])
        parser.add_argument('--index', type=str, help='Index name')
    
    def handle(self, *args, **options):
        es = Elasticsearch([settings.ELASTICSEARCH_DSL['default']['hosts']])
        action = options['action']
        index = options['index']
        
        if action == 'create':
            self.create_index(es, index)
        elif action == 'delete':
            self.delete_index(es, index)
        elif action == 'status':
            self.show_status(es, index)
    
    def create_index(self, es, index):
        """Create Elasticsearch index."""
        if not index:
            self.stdout.write('Please specify index name with --index')
            return
        
        try:
            es.indices.create(index=index)
            self.stdout.write(f'Successfully created index: {index}')
        except Exception as e:
            self.stdout.write(f'Error creating index: {e}')
    
    def delete_index(self, es, index):
        """Delete Elasticsearch index."""
        if not index:
            self.stdout.write('Please specify index name with --index')
            return
        
        try:
            es.indices.delete(index=index)
            self.stdout.write(f'Successfully deleted index: {index}')
        except Exception as e:
            self.stdout.write(f'Error deleting index: {e}')
    
    def show_status(self, es, index):
        """Show index status."""
        try:
            if index:
                status = es.indices.get(index=index)
                self.stdout.write(f'Index {index} status: {status}')
            else:
                status = es.indices.stats()
                self.stdout.write(f'All indices status: {status}')
        except Exception as e:
            self.stdout.write(f'Error getting status: {e}')
```

## 🔒 **Security Considerations**

### **Authentication:**
1. **Elasticsearch Security**: Enable X-Pack security
2. **User Management**: Create dedicated search users
3. **Role-Based Access**: Limit index access by role
4. **API Security**: Secure Django-Elasticsearch communication

### **Data Protection:**
1. **Field-Level Security**: Hide sensitive fields from search
2. **Document-Level Security**: Filter results by user permissions
3. **Audit Logging**: Track all search operations
4. **Data Encryption**: Encrypt data in transit and at rest

## 📈 **Performance Benchmarks**

### **Expected Improvements:**
- **Search Speed**: 10-100x faster than database queries
- **Relevance**: Better result ranking with relevance scoring
- **Scalability**: Handle millions of documents efficiently
- **Real-time**: Immediate search index updates
- **Advanced Features**: Fuzzy search, geospatial queries, aggregations

### **Resource Requirements:**
- **Memory**: 2-8GB RAM per Elasticsearch node
- **Storage**: 2-3x data size for indices
- **CPU**: 2-4 cores per node
- **Network**: Low latency connection to Django app

## 🎯 **Migration Strategy**

### **Phase 1: Setup and Testing**
1. Install and configure Elasticsearch
2. Create search documents and mappings
3. Implement basic search functionality
4. Test with small datasets

### **Phase 2: Data Migration**
1. Bulk index existing data
2. Implement real-time indexing
3. Test search performance
4. Validate result accuracy

### **Phase 3: Production Deployment**
1. Deploy to staging environment
2. Load testing and optimization
3. Production deployment
4. Monitor and maintain

### **Phase 4: Advanced Features**
1. Implement search analytics
2. Add advanced filtering
3. Optimize relevance scoring
4. Performance tuning

## 📚 **Additional Resources**

### **Documentation:**
- [Elasticsearch Official Docs](https://www.elastic.co/guide/index.html)
- [Django Elasticsearch DSL](https://django-elasticsearch-dsl.readthedocs.io/)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)

### **Best Practices:**
- Use appropriate analyzers for different languages
- Implement proper index mapping
- Regular index optimization and maintenance
- Monitor cluster health and performance
- Implement proper error handling and fallbacks

---

This integration guide provides a comprehensive roadmap for implementing Elasticsearch in your KG Job Portal project. The implementation will significantly improve search performance, relevance, and user experience while maintaining the simplicity of your current architecture.
