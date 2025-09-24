from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random

from job_portal.apps.users.models import ServiceProviderProfile, ClientProfile
from job_portal.apps.users.models_enhanced import (
    PricingStructure, ProfessionalInformation, ProviderLanguage, 
    Certificate, WorkPortfolio, AvailabilityStatus, UserPreference,
    RecommendationEngine, StatisticsAggregation, Language
)
from job_portal.apps.core.models import ServiceSubcategory, ServiceCategory
from accounts.models import UserModel


class Command(BaseCommand):
    help = 'Populate enhanced data for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--providers',
            type=int,
            default=10,
            help='Number of providers to enhance',
        )
        parser.add_argument(
            '--clients',
            type=int,
            default=20,
            help='Number of clients to enhance',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting enhanced data population...')
        
        with transaction.atomic():
            self._create_languages()
            self._enhance_providers(options['providers'])
            self._enhance_clients(options['clients'])
            self._create_recommendations()
            self._create_statistics()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated enhanced data!')
        )

    def _create_languages(self):
        """Create language data."""
        languages = [
            ('Russian', 'ru'),
            ('Kyrgyz', 'ky'),
            ('English', 'en'),
            ('Kazakh', 'kk'),
            ('Uzbek', 'uz'),
            ('Turkish', 'tr'),
        ]
        
        for name, code in languages:
            Language.objects.get_or_create(
                name=name,
                defaults={'code': code}
            )
        
        self.stdout.write('Created languages')

    def _enhance_providers(self, count):
        """Enhance service providers with additional data."""
        providers = ServiceProviderProfile.objects.all()[:count]
        
        for provider in providers:
            # Create pricing structures
            self._create_pricing_structures(provider)
            
            # Create professional information
            self._create_professional_info(provider)
            
            # Create languages
            self._create_provider_languages(provider)
            
            # Create certificates
            self._create_certificates(provider)
            
            # Create portfolio
            self._create_portfolio(provider)
            
            # Create availability status
            self._create_availability_status(provider)
        
        self.stdout.write(f'Enhanced {len(providers)} providers')

    def _create_pricing_structures(self, provider):
        """Create pricing structures for provider."""
        services = provider.services_offered.all()[:3]  # Limit to 3 services
        
        for service in services:
            PricingStructure.objects.get_or_create(
                provider=provider,
                service_subcategory=service,
                defaults={
                    'hourly_rate': random.randint(200, 800),
                    'daily_rate': random.randint(800, 2000),
                    'per_order_rate': random.randint(500, 1500),
                    'minimum_charge': random.randint(200, 500),
                    'currency': 'KGS',
                    'is_negotiable': random.choice([True, False]),
                    'includes_materials': random.choice([True, False]),
                }
            )

    def _create_professional_info(self, provider):
        """Create professional information for provider."""
        ProfessionalInformation.objects.get_or_create(
            provider=provider,
            defaults={
                'years_of_experience': random.randint(1, 15),
                'work_experience_description': f"Experienced professional with {random.randint(1, 15)} years in the field.",
                'education_level': random.choice(['high_school', 'vocational', 'bachelor', 'master']),
                'education_institution': random.choice([
                    'Kyrgyz National University',
                    'Bishkek Technical University',
                    'International University of Kyrgyzstan',
                    'Kyrgyz State University',
                ]),
                'education_field': random.choice([
                    'Engineering',
                    'Business Administration',
                    'Computer Science',
                    'Construction',
                    'Electrical Engineering',
                ]),
                'graduation_year': random.randint(2000, 2020),
                'specializations': 'Specialized in modern techniques and quality work',
                'tools_and_equipment': 'Professional tools and equipment available',
            }
        )

    def _create_provider_languages(self, provider):
        """Create language skills for provider."""
        languages = Language.objects.all()
        selected_languages = random.sample(list(languages), random.randint(1, 3))
        
        for language in selected_languages:
            ProviderLanguage.objects.get_or_create(
                provider=provider,
                language=language,
                defaults={
                    'proficiency_level': random.choice(['intermediate', 'advanced', 'native']),
                }
            )

    def _create_certificates(self, provider):
        """Create certificates for provider."""
        certificate_templates = [
            ('Professional Certification 2020', 'Industry Association'),
            ('Safety Training Certificate', 'Safety Institute'),
            ('Quality Assurance Certificate', 'Quality Board'),
            ('Advanced Skills Certificate', 'Skills Development Center'),
        ]
        
        for name, organization in certificate_templates:
            if random.choice([True, False]):  # 50% chance
                Certificate.objects.get_or_create(
                    provider=provider,
                    name=name,
                    defaults={
                        'issuing_organization': organization,
                        'issue_date': timezone.now().date() - timedelta(days=random.randint(30, 1000)),
                        'expiry_date': timezone.now().date() + timedelta(days=random.randint(365, 1095)),
                        'certificate_number': f"CERT-{random.randint(1000, 9999)}",
                        'is_verified': random.choice([True, False]),
                    }
                )

    def _create_portfolio(self, provider):
        """Create portfolio items for provider."""
        portfolio_templates = [
            ('Modern Kitchen Renovation', 'Complete kitchen renovation with modern appliances'),
            ('Office Space Design', 'Professional office space design and setup'),
            ('Home Repair Project', 'Comprehensive home repair and maintenance'),
            ('Custom Furniture Assembly', 'Custom furniture assembly and installation'),
        ]
        
        for title, description in portfolio_templates:
            if random.choice([True, False]):  # 50% chance
                WorkPortfolio.objects.get_or_create(
                    provider=provider,
                    title=title,
                    defaults={
                        'description': description,
                        'service_category': random.choice(provider.services_offered.all()) if provider.services_offered.exists() else None,
                        'completion_date': timezone.now().date() - timedelta(days=random.randint(30, 365)),
                        'client_feedback': 'Excellent work! Highly recommended.',
                        'is_featured': random.choice([True, False]),
                        'is_public': True,
                    }
                )

    def _create_availability_status(self, provider):
        """Create availability status for provider."""
        AvailabilityStatus.objects.get_or_create(
            provider=provider,
            defaults={
                'status': random.choice(['available', 'busy', 'offline']),
                'current_location': provider.user_profile.city or 'Bishkek',
                'is_location_accurate': random.choice([True, False]),
                'last_location_update': timezone.now(),
                'working_hours_start': '09:00',
                'working_hours_end': '18:00',
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            }
        )

    def _enhance_clients(self, count):
        """Enhance clients with preferences."""
        clients = ClientProfile.objects.all()[:count]
        
        for client in clients:
            UserPreference.objects.get_or_create(
                user=client.user_profile.user,
                defaults={
                    'preferred_cities': [client.user_profile.city or 'Bishkek'],
                    'max_distance_km': random.randint(10, 100),
                    'budget_range_min': random.randint(500, 2000),
                    'budget_range_max': random.randint(3000, 10000),
                    'min_rating_preference': random.uniform(3.0, 5.0),
                    'prefer_verified_providers': random.choice([True, False]),
                }
            )
        
        self.stdout.write(f'Enhanced {len(clients)} clients')

    def _create_recommendations(self):
        """Create sample recommendations."""
        users = UserModel.objects.all()[:10]
        
        for user in users:
            # Create some sample recommendations
            RecommendationEngine.objects.get_or_create(
                user=user,
                recommendation_type='service_provider',
                recommended_object_type='ServiceProviderProfile',
                recommended_object_id=random.randint(1, 10),
                defaults={
                    'confidence_score': random.uniform(0.3, 0.9),
                    'reason': 'Based on your preferences and ratings',
                    'algorithm_version': 'v1.0',
                }
            )
        
        self.stdout.write('Created sample recommendations')

    def _create_statistics(self):
        """Create statistics aggregation."""
        today = timezone.now().date()
        
        StatisticsAggregation.objects.get_or_create(
            date=today,
            defaults={
                'total_providers': ServiceProviderProfile.objects.count(),
                'active_providers': ServiceProviderProfile.objects.filter(is_available=True).count(),
                'verified_providers': ServiceProviderProfile.objects.filter(is_verified_provider=True).count(),
                'average_provider_rating': 4.2,
                'total_clients': ClientProfile.objects.count(),
                'active_clients': ClientProfile.objects.count(),
                'total_orders': random.randint(100, 1000),
                'completed_orders': random.randint(80, 800),
                'cancelled_orders': random.randint(10, 100),
                'average_order_value': random.randint(2000, 8000),
                'total_reviews': random.randint(50, 500),
                'average_review_rating': 4.3,
                'total_searches': random.randint(200, 2000),
                'searches_with_results': random.randint(150, 1800),
            }
        )
        
        self.stdout.write('Created statistics aggregation')
