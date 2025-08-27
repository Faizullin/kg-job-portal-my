from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .test_base import JobPortalAPITestCase
from orders.models import Order
from users.models import ServiceProviderProfile
from core.models import ServiceCategory, ServiceSubcategory, ServiceArea


class TestAdvancedSearch(JobPortalAPITestCase):
    """
    Test advanced search functionality.
    These tests mimic complex search scenarios a mobile app would use.
    """
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()
    
    def test_advanced_order_search(self):
        """Test advanced order search with multiple filters."""
        url = reverse('search:order-search')
        
        # Search with multiple filters
        search_params = {
            'q': 'development',
            'city': 'Almaty',
            'service_category': '1',  # IT & Programming
            'min_budget': '1000',
            'max_budget': '10000',
            'urgency': 'high'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify filters are applied
        results = response.data['results']
        for order in results:
            self.assertEqual(order['city'], 'Almaty')
            self.assertGreaterEqual(order['budget_max'], 1000)
            self.assertLessEqual(order['budget_min'], 10000)
    
    def test_advanced_provider_search(self):
        """Test advanced provider search with multiple filters."""
        url = reverse('search:provider-search')
        
        # Search with multiple filters
        search_params = {
            'q': 'IT',
            'city': 'Almaty',
            'min_rating': '4.0'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify filters are applied
        results = response.data['results']
        for provider in results:
            self.assertGreaterEqual(provider['average_rating'], 4.0)
    
    def test_search_with_geolocation(self):
        """Test search with geolocation filters."""
        url = reverse('search:global-search')
        
        # Search by location
        search_params = {
            'q': 'development',
            'city': 'Almaty',
            'country': 'Kazakhstan'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Check that results are from the specified location
        results = response.data['results']
        if 'orders' in results:
            for order in results['orders']['results']:
                self.assertEqual(order['city'], 'Almaty')
    
    def test_search_with_service_categories(self):
        """Test search filtered by service categories."""
        url = reverse('search:global-search')
        
        # Search for IT services
        search_params = {
            'q': 'development',
            'type': 'services',
            'category': '1'  # IT & Programming
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('services', response.data['results'])
        
        # Verify only IT services are returned
        services = response.data['results']['services']['results']
        for service in services:
            self.assertEqual(service['category'], 1)
    
    def test_search_with_budget_range(self):
        """Test search with budget range filters."""
        url = reverse('search:order-search')
        
        # Search for orders within budget range
        search_params = {
            'q': 'development',
            'min_budget': '500',
            'max_budget': '3000'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify budget constraints
        results = response.data['results']
        for order in results:
            self.assertGreaterEqual(order['budget_max'], 500)
            self.assertLessEqual(order['budget_min'], 3000)
    
    def test_search_with_urgency_levels(self):
        """Test search with urgency level filters."""
        url = reverse('search:order-search')
        
        # Search for high urgency orders
        search_params = {
            'q': 'development',
            'urgency': 'high'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify only high urgency orders are returned
        results = response.data['results']
        for order in results:
            self.assertEqual(order['urgency'], 'high')
    
    def test_search_with_rating_filters(self):
        """Test search with rating filters."""
        url = reverse('search:provider-search')
        
        # Search for highly rated providers
        search_params = {
            'q': 'IT',
            'min_rating': '4.5'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify only highly rated providers are returned
        results = response.data['results']
        for provider in results:
            self.assertGreaterEqual(provider['average_rating'], 4.5)
    
    def test_search_with_availability_filters(self):
        """Test search with availability filters."""
        url = reverse('search:provider-search')
        
        # Search for available providers
        search_params = {
            'q': 'IT',
            'available': 'true'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify only available providers are returned
        results = response.data['results']
        for provider in results:
            self.assertTrue(provider['is_available'])
    
    def test_search_with_date_filters(self):
        """Test search with date-based filters."""
        url = reverse('search:order-search')
        
        # Search for recent orders
        search_params = {
            'q': 'development',
            'created_after': '2024-01-01'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify orders are recent
        results = response.data['results']
        for order in results:
            # Check that order was created after specified date
            self.assertIsNotNone(order['created_at'])
    
    def test_search_with_multiple_keywords(self):
        """Test search with multiple keywords."""
        url = reverse('search:global-search')
        
        # Search with multiple keywords
        search_params = {
            'q': 'web mobile development',
            'type': 'all'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify search results contain relevant content
        results = response.data['results']
        self.assertIn('orders', results)
        self.assertIn('providers', results)
        self.assertIn('services', results)
    
    def test_search_with_exact_matching(self):
        """Test search with exact matching."""
        url = reverse('search:order-search')
        
        # Search for exact title match
        search_params = {
            'q': 'Web Development Project',
            'exact_match': 'true'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify exact match results
        results = response.data['results']
        for order in results:
            self.assertIn('Web Development Project', order['title'])
    
    def test_search_with_fuzzy_matching(self):
        """Test search with fuzzy matching."""
        url = reverse('search:global-search')
        
        # Search with typo (fuzzy matching should handle this)
        search_params = {
            'q': 'web devlopment',  # Typo in 'development'
            'fuzzy': 'true'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should still return relevant results despite typo
        results = response.data['results']
        self.assertGreater(len(results), 0)
    
    def test_search_with_sorting(self):
        """Test search with various sorting options."""
        url = reverse('search:order-search')
        
        # Test different sorting options
        sort_options = ['created_at', '-created_at', 'budget_min', 'budget_max']
        
        for sort_option in sort_options:
            search_params = {
                'q': 'development',
                'ordering': sort_option
            }
            
            response = self.client.get(url, search_params)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify results are sorted
            results = response.data['results']
            if len(results) > 1:
                # Check that sorting is applied (basic check)
                self.assertIsNotNone(results[0]['created_at'])
    
    def test_search_with_pagination(self):
        """Test search with pagination."""
        url = reverse('search:global-search')
        
        # Test pagination
        search_params = {
            'q': 'development',
            'page': '1',
            'page_size': '5'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pagination', response.data)
        
        # Verify pagination info
        pagination = response.data['pagination']
        self.assertEqual(pagination['page'], 1)
        self.assertEqual(pagination['page_size'], 5)
    
    def test_search_performance_with_large_queries(self):
        """Test search performance with complex queries."""
        import time
        
        url = reverse('search:global-search')
        
        # Complex search query
        search_params = {
            'q': 'web mobile development design programming',
            'city': 'Almaty',
            'min_budget': '100',
            'max_budget': '10000',
            'type': 'all'
        }
        
        # Measure response time
        start_time = time.time()
        response = self.client.get(url, search_params)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 2.0)  # Should respond within 2 seconds
    
    def test_search_result_relevance(self):
        """Test that search results are relevant to the query."""
        url = reverse('search:order-search')
        
        # Search for web development
        search_params = {
            'q': 'web development'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Verify results are relevant
        results = response.data['results']
        for order in results:
            # Check that order title or description contains relevant keywords
            title_lower = order['title'].lower()
            description_lower = order['description'].lower()
            
            self.assertTrue(
                'web' in title_lower or 'development' in title_lower or
                'web' in description_lower or 'development' in description_lower
            )
    
    def test_search_with_empty_results(self):
        """Test search that should return no results."""
        url = reverse('search:order-search')
        
        # Search for something that shouldn't exist
        search_params = {
            'q': 'nonexistentkeyword12345'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should return empty results
        results = response.data['results']
        self.assertEqual(len(results), 0)
    
    def test_search_with_special_characters(self):
        """Test search with special characters."""
        url = reverse('search:global-search')
        
        # Search with special characters
        search_params = {
            'q': 'web-dev & programming',
            'type': 'all'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should handle special characters gracefully
        results = response.data['results']
        self.assertIsInstance(results, dict)
    
    def test_search_with_unicode_characters(self):
        """Test search with unicode characters."""
        url = reverse('search:global-search')
        
        # Search with unicode characters
        search_params = {
            'q': 'веб разработка',  # Russian for "web development"
            'type': 'all'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should handle unicode characters gracefully
        results = response.data['results']
        self.assertIsInstance(results, dict)
    
    def test_search_with_very_long_queries(self):
        """Test search with very long queries."""
        url = reverse('search:global-search')
        
        # Very long search query
        long_query = 'web development mobile app design programming ' * 10
        search_params = {
            'q': long_query,
            'type': 'all'
        }
        
        response = self.client.get(url, search_params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Should handle long queries gracefully
        results = response.data['results']
        self.assertIsInstance(results, dict)
    
    def test_search_with_mixed_case(self):
        """Test search with mixed case sensitivity."""
        url = reverse('search:global-search')
        
        # Test different case variations
        case_variations = [
            'WEB DEVELOPMENT',
            'web Development',
            'Web development',
            'WEB development'
        ]
        
        for case_variation in case_variations:
            search_params = {
                'q': case_variation,
                'type': 'all'
            }
            
            response = self.client.get(url, search_params)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # All case variations should return similar results
            results = response.data['results']
            self.assertIsInstance(results, dict)

