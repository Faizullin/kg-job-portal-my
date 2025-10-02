from django.apps import AppConfig


class AttachmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_portal.apps.attachments'
    verbose_name = 'Attachments'
    
    def ready(self):
        import job_portal.apps.attachments.signals