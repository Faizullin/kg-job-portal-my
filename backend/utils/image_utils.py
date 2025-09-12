"""
Utility functions for image processing and handling
"""
from PIL import Image
from io import BytesIO
import uuid
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def resize_image(image, target_size=(300, 300), quality=85, format='JPEG'):
    """
    Resize an image to target dimensions while maintaining aspect ratio
    
    Args:
        image: PIL Image object
        target_size: tuple of (width, height)
        quality: JPEG quality (1-100)
        format: Output format ('JPEG', 'PNG', etc.)
    
    Returns:
        BytesIO object containing the resized image
    """
    # Convert to RGB if necessary
    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')
    
    # Resize while maintaining aspect ratio
    image.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # Create a new image with the target size and paste the resized image
    new_image = Image.new('RGB', target_size, (255, 255, 255))
    new_image.paste(image, (
        (target_size[0] - image.size[0]) // 2,
        (target_size[1] - image.size[1]) // 2
    ))
    
    # Save to BytesIO
    output = BytesIO()
    new_image.save(output, format=format, quality=quality)
    output.seek(0)
    
    return output


def generate_profile_image_filename(user_id, file_extension='jpg'):
    """
    Generate a unique filename for profile images
    
    Args:
        user_id: User ID
        file_extension: File extension (without dot)
    
    Returns:
        str: Generated filename
    """
    unique_id = uuid.uuid4().hex[:8]
    return f"user_photos/{user_id}/profile_{unique_id}.{file_extension}"


def validate_image_file(file, max_size=5*1024*1024, allowed_types=None):
    """
    Validate uploaded image file
    
    Args:
        file: Uploaded file object
        max_size: Maximum file size in bytes (default: 5MB)
        allowed_types: List of allowed MIME types
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if allowed_types is None:
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    
    # Check file size
    if file.size > max_size:
        return False, f"File size must be no more than {max_size // (1024 * 1024)}MB."
    
    # Check file type
    if hasattr(file, 'content_type') and file.content_type not in allowed_types:
        return False, "Only JPEG, PNG, GIF and WebP images are allowed."
    
    # Try to open with PIL to validate it's a valid image
    try:
        file.seek(0)  # Reset file pointer
        Image.open(file)
        file.seek(0)  # Reset file pointer again
    except Exception:
        return False, "Invalid image file."
    
    return True, None


def process_profile_image(image_file, user_id, target_size=(300, 300)):
    """
    Process and save a profile image
    
    Args:
        image_file: Uploaded file object
        user_id: User ID
        target_size: Target image dimensions
    
    Returns:
        tuple: (filename, ContentFile) or (None, error_message)
    """
    # Validate the image
    is_valid, error = validate_image_file(image_file)
    if not is_valid:
        return None, error
    
    try:
        # Open and process the image
        image = Image.open(image_file)
        resized_image = resize_image(image, target_size)
        
        # Generate filename
        filename = generate_profile_image_filename(user_id)
        
        # Create ContentFile
        content_file = ContentFile(resized_image.getvalue())
        
        return filename, content_file
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"


def delete_profile_image(image_field):
    """
    Delete a profile image from storage
    
    Args:
        image_field: Django ImageField
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not image_field:
        return True
    
    try:
        if default_storage.exists(image_field.name):
            default_storage.delete(image_field.name)
        return True
    except Exception:
        return False
