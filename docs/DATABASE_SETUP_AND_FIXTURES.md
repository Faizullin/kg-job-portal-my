# Database Setup and Fixtures Guide

This guide covers setting up the database and loading initial data for the Job Portal application.

## Fixture Files (in loading order)

1. **00_groups_and_permissions.json** - Django groups and permissions
2. **01_languages.json** - Supported languages
3. **02_service_categories.json** - Main service categories
4. **03_service_subcategories.json** - Service subcategories
5. **04_service_addons.json** - Service add-ons and extras
6. **05_service_areas.json** - Service coverage areas
7. **06_system_settings.json** - System configuration
8. **19_notification_templates.json** - Email and push notification templates

## Step-by-Step Setup Commands

### 1. Create Superuser
```bash
cd backend
python manage.py createsuperuser
```
**Follow the prompts to create your admin user:**
- Username: `admin` (or your preferred username)
- Email: `admin@example.com` (or your email)
- Password: Create a strong password

### 2. Load Fixtures in Order
```bash
# Load groups and permissions first
python manage.py loaddata 00_groups_and_permissions.json

# Load core data
python manage.py loaddata 01_languages.json
python manage.py loaddata 02_service_categories.json
python manage.py loaddata 03_service_subcategories.json
python manage.py loaddata 04_service_addons.json
python manage.py loaddata 05_service_areas.json

# Load system configuration
python manage.py loaddata 06_system_settings.json

# Load notification templates
python manage.py loaddata 19_notification_templates.json
```

### 3. Alternative: Load All Fixtures at Once
```bash
python manage.py loaddata fixtures/*.json
```

### 4. Verify Setup
```bash
# Check if data was loaded correctly
python manage.py shell
```
```python
# In Django shell, verify:
from django.contrib.auth.models import Group
from core.models import Language, ServiceCategory, ServiceSubcategory
from notifications.models import NotificationTemplate

# Check groups
print("Groups:", Group.objects.all().values_list('name', flat=True))

# Check core data
print("Languages:", Language.objects.count())
print("Categories:", ServiceCategory.objects.count())
print("Subcategories:", ServiceSubcategory.objects.count())

# Check notifications
print("Templates:", NotificationTemplate.objects.count())
```

## User Management

### Create Additional Users
```bash
# Create regular users through Django admin or shell
python manage.py shell
```

```python
from accounts.models import UserModel
from django.contrib.auth.models import Group

# Create a service provider
provider = UserModel.objects.create_user(
    username='provider1',
    email='provider@example.com',
    password='provider123',
    first_name='John',
    last_name='Provider',
    name='John Provider',
    user_type='paid'
)

# Add to service provider group
provider_group = Group.objects.get(name='service_provider')
provider.groups.add(provider_group)

# Create a client
client = UserModel.objects.create_user(
    username='client1',
    email='client@example.com',
    password='client123',
    first_name='Jane',
    last_name='Client',
    name='Jane Client',
    user_type='free'
)

# Add to client group
client_group = Group.objects.get(name='client')
client.groups.add(client_group)
```

### Assign Users to Groups
```bash
python manage.py shell
```

```python
from accounts.models import UserModel
from django.contrib.auth.models import Group

# Get admin user
admin_user = UserModel.objects.get(username='admin')

# Get groups
admin_group = Group.objects.get(name='admin')
service_provider_group = Group.objects.get(name='service_provider')
payment_manager_group = Group.objects.get(name='payment_manager')
finance_manager_group = Group.objects.get(name='finance_manager')

# Assign admin user to multiple groups
admin_user.groups.add(admin_group, service_provider_group, payment_manager_group, finance_manager_group)
```

## Available Groups

- **admin**: Full system access
- **moderator**: Content moderation capabilities
- **user**: Basic user permissions
- **service_provider**: Service provider specific permissions
- **client**: Client user permissions
- **payment_manager**: Payment processing permissions
- **finance_manager**: Financial management permissions

## Troubleshooting

### Common Issues

1. **Fixture loading errors**: Check if models exist and migrations are applied
2. **Permission errors**: Ensure superuser has proper permissions
3. **Group assignment errors**: Verify groups exist before assigning users

### Reset Database (if needed)
```bash
# Drop and recreate database (WARNING: This will delete all data)
python manage.py flush

# Or reset specific apps
python manage.py migrate core zero
python manage.py migrate core
```

## Next Steps

After loading fixtures:
1. Access Django admin at `/admin/`
2. Create additional users as needed
3. Configure service categories and areas
4. Set up payment providers
5. Test the system functionality

## Notes

- Fixtures use hardcoded primary keys for consistency
- User passwords in fixtures are placeholders - use `createsuperuser` for real users
- Groups and permissions are set up automatically
- All core data is in Russian/Kazakh as per the application locale
