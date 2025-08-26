#!/usr/bin/env python3
"""
Django Migration Cleanup Script
This script deletes all migration files except __init__.py in all Django apps
"""

import os
import shutil
from pathlib import Path


def clean_migrations():
    """Clean up all Django migration files except __init__.py"""
    
    print("🧹 Starting Django migration cleanup...")
    
    # Get the backend directory path
    script_dir = Path(__file__).parent
    backend_path = script_dir.parent / "backend"
    
    if not backend_path.exists():
        print("❌ Backend directory not found at:", backend_path)
        print("💡 Make sure you're running this script from the scripts folder")
        return False
    
    print("📁 Backend directory found at:", backend_path)
    
    # Find all migration directories
    migration_dirs = list(backend_path.rglob("migrations"))
    
    if not migration_dirs:
        print("ℹ️  No migration directories found")
        return True
    
    print(f"🔍 Found {len(migration_dirs)} migration directories:")
    
    total_deleted = 0
    
    for migration_dir in migration_dirs:
        print(f"  📂 Processing: {migration_dir}")
        
        # Get all files in the migration directory
        for file_path in migration_dir.iterdir():
            if file_path.is_file() and file_path.name != "__init__.py":
                try:
                    file_path.unlink()
                    print(f"    🗑️  Deleted: {file_path.name}")
                    total_deleted += 1
                except Exception as e:
                    print(f"    ❌ Failed to delete {file_path.name}: {e}")
            elif file_path.name == "__init__.py":
                print(f"    ✅ Kept: {file_path.name}")
    
    print(f"\n🎉 Migration cleanup completed!")
    print(f"📊 Total files deleted: {total_deleted}")
    print("💡 Don't forget to:")
    print("   1. Run 'python manage.py makemigrations' to create new migrations")
    print("   2. Run 'python manage.py migrate' to apply the new migrations")
    print("   3. Update your database if needed")
    print("\n💻 To run this script again, use: python clean_migrations.py")
    
    return True


if __name__ == "__main__":
    try:
        success = clean_migrations()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        exit(1)
