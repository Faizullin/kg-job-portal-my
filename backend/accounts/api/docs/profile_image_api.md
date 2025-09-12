# Profile Image Upload API Documentation

## Overview
This API provides endpoints for managing user profile images, including upload, delete, and resize operations.

## Base URL
```
/api/v1/profile/image/
```

## Authentication
All endpoints require authentication using Django REST Framework Token Authentication.

## Endpoints

### 1. Upload Profile Image
**POST** `/api/v1/profile/image/`

Upload a new profile image for the authenticated user.

#### Request
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `photo` (file, required): Image file (JPEG, PNG, GIF, WebP)
  - Max file size: 5MB
  - Max dimensions: 2048x2048 pixels (will be resized to 300x300)

#### Response
**Success (200 OK)**:
```json
{
    "message": "Profile image uploaded successfully",
    "user": {
        "id": 1,
        "photo": "/media/user_photos/1/profile_abc123.jpg",
        "photo_url": "http://localhost:8000/media/user_photos/1/profile_abc123.jpg",
        "name": "John Doe"
    }
}
```

**Error (400 Bad Request)**:
```json
{
    "message": "Invalid image file",
    "errors": {
        "photo": ["File size must be no more than 5MB."]
    }
}
```

### 2. Get Profile Image
**GET** `/api/v1/profile/image/`

Get current profile image information for the authenticated user.

#### Response
**Success (200 OK)**:
```json
{
    "user": {
        "id": 1,
        "photo": "/media/user_photos/1/profile_abc123.jpg",
        "photo_url": "http://localhost:8000/media/user_photos/1/profile_abc123.jpg",
        "name": "John Doe"
    }
}
```

### 3. Delete Profile Image
**DELETE** `/api/v1/profile/image/`

Delete the current profile image for the authenticated user.

#### Response
**Success (200 OK)**:
```json
{
    "message": "Profile image deleted successfully"
}
```

**Error (404 Not Found)**:
```json
{
    "message": "No profile image to delete"
}
```

### 4. Resize Profile Image
**POST** `/api/v1/profile/image/resize/`

Resize the existing profile image to standard dimensions (300x300).

#### Response
**Success (200 OK)**:
```json
{
    "message": "Profile image resized successfully",
    "user": {
        "id": 1,
        "photo": "/media/user_photos/1/profile_def456.jpg",
        "photo_url": "http://localhost:8000/media/user_photos/1/profile_def456.jpg",
        "name": "John Doe"
    }
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid file or validation error |
| 401 | Unauthorized - Authentication required |
| 404 | Not Found - No profile image exists |
| 500 | Internal Server Error - Server error during processing |

## File Storage

- **Path**: `user_photos/{user_id}/profile_{unique_id}.{extension}`
- **Supported Formats**: JPEG, PNG, GIF, WebP
- **Max File Size**: 5MB
- **Output Size**: 300x300 pixels (maintains aspect ratio)
- **Quality**: 85% JPEG compression

## Image Processing

All uploaded images are automatically:
1. Validated for file type and size
2. Converted to RGB format if necessary
3. Resized to 300x300 pixels while maintaining aspect ratio
4. Centered on a white background if needed
5. Compressed with 85% JPEG quality

## Security Considerations

- Only authenticated users can upload/manage their own profile images
- File type validation prevents malicious file uploads
- File size limits prevent storage abuse
- Images are processed and resized to prevent large file storage
- Old images are automatically deleted when new ones are uploaded

## Usage Examples

### cURL Examples

#### Upload Image
```bash
curl -X POST \
  -H "Authorization: Token your_auth_token" \
  -F "photo=@/path/to/image.jpg" \
  http://localhost:8000/api/v1/profile/image/
```

#### Delete Image
```bash
curl -X DELETE \
  -H "Authorization: Token your_auth_token" \
  http://localhost:8000/api/v1/profile/image/
```

#### Get Image Info
```bash
curl -X GET \
  -H "Authorization: Token your_auth_token" \
  http://localhost:8000/api/v1/profile/image/
```

### JavaScript/Fetch Examples

#### Upload Image
```javascript
const formData = new FormData();
formData.append('photo', fileInput.files[0]);

fetch('/api/v1/profile/image/', {
    method: 'POST',
    headers: {
        'Authorization': 'Token your_auth_token'
    },
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Delete Image
```javascript
fetch('/api/v1/profile/image/', {
    method: 'DELETE',
    headers: {
        'Authorization': 'Token your_auth_token'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```
