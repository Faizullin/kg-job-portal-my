from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AttachmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms.apps.attachments'
    verbose_name = _("Attachments")
    
    def ready(self):
        import lms.apps.attachments.signals # noqa 
        super().ready()
