from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.abstract_models import AbstractTimestampedModel, PhoneNumberField

UserModel = get_user_model()


class ContactEnquiryType(models.TextChoices):
    GENERAL = 'general', _('General')
    SUPPORT = 'support', _('Support')
    SALES = 'sales', _('Sales')
    FEEDBACK = 'feedback', _('Feedback')
    OTHER = 'other', _('Other')


class SimpleContact(AbstractTimestampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='simple_contacts')
    subject = models.CharField(max_length=100)
    message = models.TextField()
    phone = PhoneNumberField()
    enquiry_type = models.CharField(max_length=20, choices=ContactEnquiryType.choices,
                                    default=ContactEnquiryType.GENERAL)
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP Address'))
