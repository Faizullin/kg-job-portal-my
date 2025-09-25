#!/usr/bin/env python
"""
Seed script for Master KG Job Portal
Creates superuser, loads fixtures, and sets up initial data
"""

import os
import sys
import django
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.dev')
django.setup()


User = get_user_model()


def create_superuser():
    """Create a superuser if it doesn't exist."""
    superuser_email = "admin@masterkg.kg"
    superuser_username = "admin"
    superuser_password = "admin123"
    
    if not User.objects.filter(email=superuser_email).exists():
        User.objects.create_superuser(
            username=superuser_username,
            email=superuser_email,
            password=superuser_password,
            first_name="Admin",
            last_name="Master KG"
        )


def create_demo_users():
    """Create demo users for testing."""
    demo_users = [
        {
            'username': 'maria_gonzalez',
            'email': 'maria@example.com',
            'password': 'demo123',
            'first_name': 'Maria',
            'last_name': 'Gonzalez',
            'is_active': True
        },
        {
            'username': 'arman_yussupov',
            'email': 'arman@example.com',
            'password': 'demo123',
            'first_name': 'Арман',
            'last_name': 'Юссупов',
            'is_active': True
        },
        {
            'username': 'zhandos_amanbaev',
            'email': 'zhandos@example.com',
            'password': 'demo123',
            'first_name': 'Жандос',
            'last_name': 'Аманбаев',
            'is_active': True
        },
        {
            'username': 'master_support',
            'email': 'support@masterkg.kg',
            'password': 'support123',
            'first_name': 'Master KG',
            'last_name': 'Support',
            'is_active': True,
            'is_staff': True
        }
    ]
    
    for user_data in demo_users:
        if not User.objects.filter(email=user_data['email']).exists():
            User.objects.create_user(**user_data)


def load_fixtures():
    """Load fixture files in the correct order."""
    fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')
    
    # Define fixtures in dependency order
    fixture_files = [
        'languages.json',
        'service_categories.json',
        'service_subcategories.json',
        'service_areas.json',
        'system_settings.json',
        'support_faq.json'
    ]
    
    for fixture_file in fixture_files:
        fixture_path = os.path.join(fixtures_dir, fixture_file)
        if not os.path.exists(fixture_path):
            raise FileNotFoundError(f"Fixture file not found: {fixture_file}")
        call_command('loaddata', fixture_path, verbosity=0)


def setup_groups():
    """Setup initial groups and permissions."""
    call_command('setup_groups', verbosity=0)


def run_migrations():
    """Run database migrations."""
    call_command('migrate', verbosity=0)


@transaction.atomic
def main():
    """Main seeding function with transaction rollback."""
    print("🌱 Starting Master KG Job Portal seeding...")
    
    try:
        # Run migrations
        print("📊 Running migrations...")
        run_migrations()
        
        # Setup groups
        print("👥 Setting up groups...")
        setup_groups()
        
        # Load fixtures
        print("📦 Loading fixtures...")
        load_fixtures()
        
        # Create superuser
        print("👑 Creating superuser...")
        create_superuser()
        
        # Create demo users
        print("👤 Creating demo users...")
        create_demo_users()
        
        print("🎉 Seeding completed successfully!")
        print("🔐 Login: admin@masterkg.kg / admin123")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        print("🔄 Rolling back all changes...")
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        sys.exit(1)
