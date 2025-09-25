from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServiceProviderProfile, ProviderStatistics


@receiver(post_save, sender=ServiceProviderProfile)
def create_provider_statistics(sender, instance, created, **kwargs):
    """Automatically create ProviderStatistics when ServiceProviderProfile is created."""
    if created:
        ProviderStatistics.objects.get_or_create(
            provider=instance,
            defaults={
                'total_jobs_completed': 0,
                'on_time_percentage': 0.00,
                'repeat_customer_percentage': 0.00,
                'average_rating': 0.00,
                'total_reviews': 0
            }
        )
