import os
import logging
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from job_portal.apps.attachments.models import Attachment
from job_portal.apps.users.models import PortfolioItem, Certificate

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up orphaned files from storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write("Starting orphaned file cleanup...")
        
        # Get all file paths from database
        db_file_paths = set()
        
        # Attachment files
        attachment_files = Attachment.objects.values_list('file', flat=True).exclude(file='')
        db_file_paths.update(attachment_files)
        
        # Portfolio images
        portfolio_images = PortfolioItem.objects.values_list('image', flat=True).exclude(image='')
        db_file_paths.update(portfolio_images)
        
        # Certificate files
        certificate_files = Certificate.objects.values_list('certificate_file', flat=True).exclude(certificate_file='')
        db_file_paths.update(certificate_files)
        
        # Remove empty strings and None values
        db_file_paths = {path for path in db_file_paths if path}
        
        if verbose:
            self.stdout.write(f"Found {len(db_file_paths)} files in database")
        
        # Get all files in storage
        try:
            storage_files = set()
            for root, dirs, files in os.walk(default_storage.location):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Convert to relative path
                    rel_path = os.path.relpath(file_path, default_storage.location)
                    storage_files.add(rel_path)
            
            if verbose:
                self.stdout.write(f"Found {len(storage_files)} files in storage")
            
            # Find orphaned files
            orphaned_files = storage_files - db_file_paths
            
            if not orphaned_files:
                self.stdout.write(self.style.SUCCESS("No orphaned files found!"))
                return
            
            self.stdout.write(f"Found {len(orphaned_files)} orphaned files:")
            
            total_size = 0
            for file_path in orphaned_files:
                try:
                    full_path = os.path.join(default_storage.location, file_path)
                    if os.path.exists(full_path):
                        file_size = os.path.getsize(full_path)
                        total_size += file_size
                        
                        if verbose:
                            self.stdout.write(f"  - {file_path} ({file_size} bytes)")
                        
                        if not dry_run:
                            default_storage.delete(file_path)
                            self.stdout.write(f"    Deleted: {file_path}")
                        else:
                            self.stdout.write(f"    Would delete: {file_path}")
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing {file_path}: {e}")
                    )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"DRY RUN: Would delete {len(orphaned_files)} files "
                        f"totaling {total_size} bytes"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully deleted {len(orphaned_files)} orphaned files "
                        f"totaling {total_size} bytes"
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error during cleanup: {e}")
            )
