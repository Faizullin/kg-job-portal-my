#!/usr/bin/env python
"""
Seed script for Master KG Job Portal
Creates superuser, loads fixtures, and sets up initial data
"""

import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.dev')#

import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.db import transaction
from job_portal.apps.core.models import Language, ServiceCategory, ServiceSubcategory, ServiceArea
from job_portal.apps.users.models import Master, Employer, Profession, Skill, Company
from job_portal.apps.locations.models import Country, City

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


def assign_users_to_groups():
    """Assign users to appropriate groups based on their profiles."""

    print("👥 Assigning users to groups...")

    try:
        master_group = Group.objects.get(name='Master')
        employer_group = Group.objects.get(name='Employer')

        # Assign masters to Master group
        masters = Master.objects.select_related('user').all()
        for master in masters:
            if not master.user.groups.filter(name='Master').exists():
                master.user.groups.add(master_group)
                print(f"   ✅ Assigned {master.user.username} to Master group")

        # Assign employers to Employer group
        employers = Employer.objects.select_related('user').all()
        for employer in employers:
            if not employer.user.groups.filter(name='Employer').exists():
                employer.user.groups.add(employer_group)
                print(f"   ✅ Assigned {employer.user.username} to Employer group")

        print("✅ User group assignments completed!")

    except Group.DoesNotExist as err:
        print(f"   ⚠️  Group not found: {err}")


def create_demo_profiles():
    """Create demo master and employer profiles."""

    maria_user = User.objects.filter(username='maria_gonzalez').first()
    if maria_user and not hasattr(maria_user, 'master_profile'):
        # Get first profession and skill
        profession = Profession.objects.first()
        skill = Skill.objects.first()

        master = Master.objects.create(
            user=maria_user,
            profession=profession,
            hourly_rate=25.00,
            is_available=True,
            works_remotely=False,
            travels_to_clients=True,
            about_description="Experienced cleaner with 5+ years of experience"
        )

        # Add skill to master
        if skill:
            master.master_skills.create(
                skill=skill,
                proficiency_level='advanced',
                years_of_experience=5,
                is_primary_skill=True
            )

    # Create demo employer profile
    arman_user = User.objects.filter(username='arman_yussupov').first()
    if arman_user and not hasattr(arman_user, 'employer_profile'):
        Employer.objects.create(
            user=arman_user,
            total_orders=3,
            completed_orders=2,
            cancelled_orders=1
        )


def verify_seeding():
    """Verify that seeding was successful."""

    print("🔍 Verifying seeding results...")

    # Check core models
    languages_count = Language.objects.count()
    categories_count = ServiceCategory.objects.count()
    subcategories_count = ServiceSubcategory.objects.count()
    areas_count = ServiceArea.objects.count()

    # Check location models
    countries_count = Country.objects.count()
    cities_count = City.objects.count()

    # Check user models
    professions_count = Profession.objects.count()
    skills_count = Skill.objects.count()
    companies_count = Company.objects.count()

    # Check users
    users_count = User.objects.count()

    print(f"📊 Seeding verification results:")
    print(f"   Languages: {languages_count}")
    print(f"   Countries: {countries_count}")
    print(f"   Cities: {cities_count}")
    print(f"   Service Categories: {categories_count}")
    print(f"   Service Subcategories: {subcategories_count}")
    print(f"   Service Areas: {areas_count}")
    print(f"   Professions: {professions_count}")
    print(f"   Skills: {skills_count}")
    print(f"   Companies: {companies_count}")
    print(f"   Users: {users_count}")

    # Check if we have the minimum expected data
    if (languages_count >= 3 and countries_count >= 3 and cities_count >= 3 and 
        categories_count >= 3 and professions_count >= 3):
        print("✅ Seeding verification passed!")
        return True
    else:
        print("⚠️  Seeding verification failed - some data might be missing")
        return False


def load_fixtures():
    """Load fixture files in the correct order."""
    fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')

    # Define fixtures in dependency order
    fixture_files = [
        'languages.json',
        'countries.json',
        'cities.json',
        'service_categories.json',
        'service_subcategories.json',
        'service_areas.json',
        'professions.json',
        'skills.json',
        'companies.json',
        'system_settings.json',
        'support_faq.json'
    ]

    for fixture_file in fixture_files:
        fixture_path = os.path.join(fixtures_dir, fixture_file)
        if not os.path.exists(fixture_path):
            print(f"⚠️  Warning: Fixture file not found: {fixture_file}")
            continue
        print(f"📦 Loading {fixture_file}...")
        call_command('loaddata', fixture_path, verbosity=0)


def setup_groups():
    """Setup initial groups and permissions."""

    print("👥 Creating groups...")

    # Create groups
    groups_data = [
        {
            'name': 'Master',
            'description': 'masters who offer services',
            'permissions': [
                'add_jobapplication', 'change_jobapplication', 'view_jobapplication',
                'add_master', 'change_master', 'view_master',
                'add_portfolioitem', 'change_portfolioitem', 'view_portfolioitem',
                'add_certificate', 'change_certificate', 'view_certificate',
            ]
        },
        {
            'name': 'Employer',
            'description': 'Users who post jobs and hire masters',
            'permissions': [
                'add_job', 'change_job', 'view_job',
                'add_employer', 'change_employer', 'view_employer',
                'add_bookmarkjob', 'change_bookmarkjob', 'view_bookmarkjob',
                'add_favoritejob', 'change_favoritejob', 'view_favoritejob',
            ]
        },
        {
            'name': 'Moderator',
            'description': 'Users who moderate content and disputes',
            'permissions': [
                'change_job', 'view_job', 'delete_job',
                'change_jobapplication', 'view_jobapplication', 'delete_jobapplication',
                'change_jobdispute', 'view_jobdispute', 'delete_jobdispute',
                'change_review', 'view_review', 'delete_review',
                'view_master', 'view_employer',
            ]
        }
    ]

    for group_data in groups_data:
        group, created = Group.objects.get_or_create(name=group_data['name'])
        if created:
            print(f"   ✅ Created group: {group_data['name']}")
        else:
            print(f"   ℹ️  Group already exists: {group_data['name']}")

        # Add permissions to group
        for perm_codename in group_data['permissions']:
            try:
                permission = Permission.objects.get(codename=perm_codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                print(f"   ⚠️  Permission not found: {perm_codename}")

    print("✅ Groups setup completed!")


def run_migrations():
    """Run database migrations."""
    call_command('makemigrations', verbosity=0)
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

        # Create demo profiles
        print("👥 Creating demo profiles...")
        create_demo_profiles()

        # Assign users to groups
        print("👥 Assigning users to groups...")
        assign_users_to_groups()

        # Verify seeding
        print("🔍 Verifying seeding...")
        verify_seeding()

        print("🎉 Seeding completed successfully!")
        print("🔐 Login: admin@masterkg.kg / admin123")
        print("👤 Demo users: maria@example.com / demo123 (Master)")
        print("👤 Demo users: arman@example.com / demo123 (Employer)")

    except Exception as err:
        print(f"❌ Seeding failed: {err}")
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
