from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_portal.apps.users'
    verbose_name = 'User Management'
    
    def ready(self):
        import job_portal.apps.users.signals  # noqa: F401
