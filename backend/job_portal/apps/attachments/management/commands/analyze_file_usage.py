from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import models
from django.utils import timezone
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_usage_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Analyze file usage across all models and log which fields use FileField or ImageField'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Analyze specific app only (e.g., users, core, orders)',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Analyze specific model only (e.g., UserProfile, Order)',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed field information including upload_to paths',
        )
        parser.add_argument(
            '--check-usage',
            action='store_true',
            help='Check actual file usage in database (slower but more accurate)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Starting file usage analysis...')
        )
        
        start_time = timezone.now()
        logger.info("=" * 80)
        logger.info("FILE USAGE ANALYSIS STARTED")
        logger.info(f"Timestamp: {start_time}")
        logger.info("=" * 80)

        try:
            # Get all Django apps
            django_apps = apps.get_app_configs()
            
            # Filter by app if specified
            if options['app']:
                django_apps = [app for app in django_apps if options['app'] in app.name]
                if not django_apps:
                    raise CommandError(f"App '{options['app']}' not found")

            total_models_analyzed = 0
            total_file_fields = 0
            total_image_fields = 0
            total_models_with_files = 0

            for app in django_apps:
                logger.info(f"\n📱 ANALYZING APP: {app.name}")
                logger.info("-" * 50)
                
                app_file_fields = 0
                app_image_fields = 0
                app_models_with_files = 0

                for model in app.get_models():
                    # Skip if specific model requested
                    if options['model'] and model.__name__ != options['model']:
                        continue
                    
                    total_models_analyzed += 1
                    model_info = self.analyze_model_file_fields(
                        model, 
                        detailed=options['detailed'],
                        check_usage=options['check_usage']
                    )
                    
                    if model_info['has_file_fields']:
                        total_models_with_files += 1
                        app_models_with_files += 1
                        total_file_fields += model_info['file_field_count']
                        total_image_fields += model_info['image_field_count']
                        app_file_fields += model_info['file_field_count']
                        app_image_fields += model_info['image_field_count']

                # App summary
                logger.info(f"\n📊 APP SUMMARY: {app.name}")
                logger.info(f"   Models with file fields: {app_models_with_files}")
                logger.info(f"   Total FileField count: {app_file_fields}")
                logger.info(f"   Total ImageField count: {app_image_fields}")

            # Overall summary
            end_time = timezone.now()
            duration = end_time - start_time
            
            logger.info("\n" + "=" * 80)
            logger.info("ANALYSIS COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Total models analyzed: {total_models_analyzed}")
            logger.info(f"Models with file fields: {total_models_with_files}")
            logger.info(f"Total FileField count: {total_file_fields}")
            logger.info(f"Total ImageField count: {total_image_fields}")
            logger.info(f"Duration: {duration}")
            logger.info("=" * 80)

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Analysis complete! Check file_usage_analysis.log for details.\n'
                    f'📊 Summary: {total_models_with_files} models with file fields, '
                    f'{total_file_fields} FileFields, {total_image_fields} ImageFields'
                )
            )

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            raise CommandError(f"Analysis failed: {str(e)}")

    def analyze_model_file_fields(self, model, detailed=False, check_usage=False):
        """Analyze a single model for file and image fields."""
        
        model_info = {
            'model_name': model.__name__,
            'app_name': model._meta.app_label,
            'has_file_fields': False,
            'file_field_count': 0,
            'image_field_count': 0,
            'fields': []
        }

        file_fields = []
        image_fields = []

        # Check all fields in the model
        for field in model._meta.get_fields():
            if isinstance(field, models.FileField):
                file_fields.append(field)
                model_info['file_field_count'] += 1
                model_info['has_file_fields'] = True
                
                field_info = {
                    'name': field.name,
                    'type': 'FileField',
                    'upload_to': getattr(field, 'upload_to', None),
                    'blank': getattr(field, 'blank', False),
                    'null': getattr(field, 'null', False),
                }
                
                if check_usage:
                    field_info['usage_count'] = self.check_field_usage(model, field)
                
                model_info['fields'].append(field_info)

            elif isinstance(field, models.ImageField):
                image_fields.append(field)
                model_info['image_field_count'] += 1
                model_info['has_file_fields'] = True
                
                field_info = {
                    'name': field.name,
                    'type': 'ImageField',
                    'upload_to': getattr(field, 'upload_to', None),
                    'blank': getattr(field, 'blank', False),
                    'null': getattr(field, 'null', False),
                }
                
                if check_usage:
                    field_info['usage_count'] = self.check_field_usage(model, field)
                
                model_info['fields'].append(field_info)

        # Log model information if it has file fields
        if model_info['has_file_fields']:
            logger.info(f"\n📋 MODEL: {model_info['app_name']}.{model_info['model_name']}")
            logger.info(f"   FileField count: {model_info['file_field_count']}")
            logger.info(f"   ImageField count: {model_info['image_field_count']}")
            
            if detailed:
                for field_info in model_info['fields']:
                    upload_path = field_info['upload_to']
                    upload_str = f" -> {upload_path}" if upload_path else ""
                    usage_str = f" (used: {field_info['usage_count']})" if 'usage_count' in field_info else ""
                    
                    logger.info(
                        f"   🔸 {field_info['name']}: {field_info['type']}"
                        f"{upload_str}{usage_str}"
                        f" [blank={field_info['blank']}, null={field_info['null']}]"
                    )
            else:
                # Simple summary
                field_names = [f['name'] for f in model_info['fields']]
                logger.info(f"   Fields: {', '.join(field_names)}")

        return model_info

    def check_field_usage(self, model, field):
        """Check how many records actually use this field."""
        try:
            # Count non-null values for this field
            filter_kwargs = {f"{field.name}__isnull": False}
            if field.blank:
                filter_kwargs[f"{field.name}__exact"] = ""
                count = model.objects.exclude(**filter_kwargs).count()
            else:
                count = model.objects.filter(**filter_kwargs).count()
            return count
        except Exception as e:
            logger.warning(f"Could not check usage for {model.__name__}.{field.name}: {str(e)}")
            return "unknown"
