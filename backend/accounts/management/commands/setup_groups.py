from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ...models import UserModel


class Command(BaseCommand):
    help = 'Set up initial groups and permissions for the accounts app'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial groups and permissions...')
        
        # Create admin group
        admin_group, created = Group.objects.get_or_create(name='admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Created admin group'))
        else:
            self.stdout.write('Admin group already exists')
        
        # Create moderator group
        moderator_group, created = Group.objects.get_or_create(name='moderator')
        if created:
            self.stdout.write(self.style.SUCCESS('Created moderator group'))
        else:
            self.stdout.write('Moderator group already exists')
        
        # Create user group
        user_group, created = Group.objects.get_or_create(name='user')
        if created:
            self.stdout.write(self.style.SUCCESS('Created user group'))
        else:
            self.stdout.write('User group already exists')
        
        # Get content types for permissions
        user_content_type = ContentType.objects.get_for_model(UserModel)
        
        # Get all user permissions
        user_permissions = Permission.objects.filter(content_type=user_content_type)
        
        # Assign all permissions to admin group
        admin_group.permissions.set(user_permissions)
        self.stdout.write(self.style.SUCCESS('Assigned all user permissions to admin group'))
        
        # Assign view permissions to moderator group
        view_permissions = user_permissions.filter(codename__startswith='view_')
        moderator_group.permissions.set(view_permissions)
        self.stdout.write(self.style.SUCCESS('Assigned view permissions to moderator group'))
        
        # Assign view permissions to user group
        user_group.permissions.set(view_permissions)
        self.stdout.write(self.style.SUCCESS('Assigned view permissions to user group'))
        
        self.stdout.write(self.style.SUCCESS('Successfully set up groups and permissions!'))
        self.stdout.write('\nGroups created:')
        self.stdout.write('- admin: Full access to all user operations')
        self.stdout.write('- moderator: Can view users and basic operations')
        self.stdout.write('- user: Can view basic user information')
        self.stdout.write('\nUse Django admin at /admin/auth/group/ to manage groups')
