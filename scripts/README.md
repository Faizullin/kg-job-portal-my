# Migration Cleanup Script

This folder contains a Python script to clean up Django migration files in your project.

## Script Available

### Python Script (Cross-Platform)
- **File**: `clean_migrations.py`
- **Usage**: Run with Python 3
- **Description**: Deletes all migration files except `__init__.py` in all Django apps
- **Platform**: Works on Windows, macOS, and Linux

## What These Scripts Do

1. **Find Migration Directories**: Locate all `migrations/` folders in your Django project
2. **Delete Migration Files**: Remove all `.py` files except `__init__.py`
3. **Keep Structure**: Preserve the `migrations/` folder structure
4. **Provide Feedback**: Show what files were deleted and kept

## Usage Instructions

### All Platforms (Python)
```bash
# Navigate to the scripts folder
cd scripts

# Run the Python script
python clean_migrations.py
```

### Windows (Command Prompt)
```cmd
# Navigate to the scripts folder
cd scripts

# Run the Python script
python clean_migrations.py
```

### Linux/macOS (Terminal)
```bash
# Navigate to the scripts folder
cd scripts

# Run the Python script
python3 clean_migrations.py
```

## ⚠️ Important Warnings

**⚠️ BACKUP YOUR DATABASE FIRST!** This operation will:
- Delete all existing migration files
- Require you to recreate migrations from scratch
- Potentially cause data loss if not handled properly

## After Running the Script

1. **Create New Migrations**:
   ```bash
   python manage.py makemigrations
   ```

2. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Verify Database State**: Ensure your database schema matches your models

## When to Use These Scripts

- **Development Environment**: When you want to start fresh with migrations
- **Testing**: To test migration creation and application
- **Cleanup**: After major model changes or when migrations become inconsistent
- **New Project Setup**: When setting up a project from scratch

## Safety Features

- Scripts only delete files in `migrations/` directories
- Always preserves `__init__.py` files
- Provides detailed feedback on what was deleted
- Shows count of deleted files
- Includes helpful reminders for next steps

## Troubleshooting

If you encounter issues:

1. **Permission Denied**: Ensure you have write permissions to the project directory
2. **Script Not Found**: Make sure you're in the correct directory
3. **Python Not Found**: Make sure Python 3 is installed and in your PATH
4. **Import Errors**: The script uses only standard library modules, so no additional packages needed

## Support

This script is designed for Django projects. Make sure you understand the implications before running it in production environments.

## Requirements

- **Python 3.6+** (uses pathlib and f-strings)
- **No external dependencies** - uses only standard library modules
- **Cross-platform compatibility** - works on Windows, macOS, and Linux
