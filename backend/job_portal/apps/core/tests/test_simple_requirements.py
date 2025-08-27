from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .test_base import JobPortalAPITestCase
from core.models import Language, ServiceCategory, ServiceSubcategory, ServiceArea


class TestSimpleRequirements(JobPortalAPITestCase):
    """
    Test simple requirements that don't require authentication.
    These tests mimic the first steps a mobile app would take.
    """
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()  # Unauthenticated client
    
    def test_app_health_check(self):
        """Test that the app is running and responding."""
        # Test a simple endpoint that should always work
        response = self.client.get('/api/v1/core/languages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_languages_endpoint_accessible(self):
        """Test that languages endpoint is accessible without authentication."""
        url = reverse('core:languages')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_service_categories_accessible(self):
        """Test that service categories are accessible without authentication."""
        url = reverse('core:service-categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Check that we have the expected categories
        categories = response.data['results']
        category_names = [cat['name'] for cat in categories]
        
        self.assertIn('IT & Programming', category_names)
        self.assertIn('Design & Creative', category_names)
    
    def test_service_subcategories_accessible(self):
        """Test that service subcategories are accessible without authentication."""
        url = reverse('core:service-subcategories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Check that we have the expected subcategories
        subcategories = response.data['results']
        subcategory_names = [sub['name'] for sub in subcategories]
        
        self.assertIn('Web Development', subcategory_names)
        self.assertIn('Mobile App Development', subcategory_names)
        self.assertIn('Logo Design', subcategory_names)
    
    def test_service_areas_accessible(self):
        """Test that service areas are accessible without authentication."""
        url = reverse('core:service-areas')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Check that we have the expected areas
        areas = response.data['results']
        area_names = [area['name'] for area in areas]
        
        self.assertIn('Almaty', area_names)
        self.assertIn('Nur-Sultan', area_names)
    
    def test_search_endpoints_accessible(self):
        """Test that search endpoints are accessible without authentication."""
        # Test global search
        url = reverse('search:global-search')
        response = self.client.get(url, {'q': 'web development'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
        self.assertIn('results', response.data)
    
    def test_order_search_accessible(self):
        """Test that order search is accessible without authentication."""
        url = reverse('search:order-search')
        response = self.client.get(url, {'q': 'web development'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
        self.assertIn('results', response.data)
    
    def test_provider_search_accessible(self):
        """Test that provider search is accessible without authentication."""
        url = reverse('search:provider-search')
        response = self.client.get(url, {'q': 'IT solutions'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query', response.data)
        self.assertIn('results', response.data)
    
    def test_search_with_filters(self):
        """Test search functionality with various filters."""
        url = reverse('search:global-search')
        
        # Test search with city filter
        response = self.client.get(url, {
            'q': 'development',
            'city': 'Almaty'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Test search with service category filter
        response = self.client.get(url, {
            'q': 'design',
            'type': 'services'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_search_validation(self):
        """Test search validation - empty query should return error."""
        url = reverse('search:global-search')
        response = self.client.get(url, {'q': ''})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_pagination_working(self):
        """Test that pagination is working correctly."""
        url = reverse('core:service-categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pagination', response.data)
        
        pagination = response.data['pagination']
        self.assertIn('page', pagination)
        self.assertIn('page_size', pagination)
        self.assertIn('total_count', pagination)
    
    def test_ordering_working(self):
        """Test that ordering is working correctly."""
        url = reverse('core:service-categories')
        response = self.client.get(url, {'ordering': 'name'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that results are ordered by name
        results = response.data['results']
        if len(results) > 1:
            self.assertLessEqual(results[0]['name'], results[1]['name'])
    
    def test_filtering_working(self):
        """Test that filtering is working correctly."""
        url = reverse('core:service-categories')
        response = self.client.get(url, {'featured': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that only featured categories are returned
        results = response.data['results']
        for category in results:
            self.assertTrue(category['featured'])
    
    def test_search_results_structure(self):
        """Test that search results have the expected structure."""
        url = reverse('search:global-search')
        response = self.client.get(url, {'q': 'web', 'type': 'orders'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('orders', response.data['results'])
        
        orders = response.data['results']['orders']
        self.assertIn('count', orders)
        self.assertIn('results', orders)
    
    def test_core_data_integrity(self):
        """Test that core data is properly structured and related."""
        # Test that subcategories are properly linked to categories
        web_dev = ServiceSubcategory.objects.get(name='Web Development')
        it_category = ServiceCategory.objects.get(name='IT & Programming')
        
        self.assertEqual(web_dev.category, it_category)
        
        # Test that areas have proper location data
        almaty_area = ServiceArea.objects.get(name='Almaty')
        self.assertEqual(almaty_area.city, 'Almaty')
        self.assertEqual(almaty_area.country, 'Kazakhstan')
    
    def test_search_performance(self):
        """Test that search queries return results quickly."""
        import time
        
        url = reverse('search:global-search')
        
        # Measure response time
        start_time = time.time()
        response = self.client.get(url, {'q': 'development'})
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 1.0)  # Should respond within 1 second
    
    def test_mobile_friendly_responses(self):
        """Test that responses are mobile-friendly (compact, essential data only)."""
        url = reverse('core:service-categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that response contains essential fields only
        results = response.data['results']
        if results:
            category = results[0]
            essential_fields = ['id', 'name', 'slug', 'icon', 'is_active']
            
            for field in essential_fields:
                self.assertIn(field, category)
            
            # Check that response is not too verbose
            response_size = len(str(response.content))
            self.assertLess(response_size, 10000)  # Response should be reasonably sized

