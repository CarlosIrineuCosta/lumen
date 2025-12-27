# Lumen - API Reference (Updated)

**FOR CLAUDE CODE - COMPREHENSIVE API ENDPOINTS AND INTEGRATION**

## Base URL
- **Development**: http://100.106.201.33:8080
- **Documentation**: http://100.106.201.33:8080/docs

## Authentication

All protected endpoints require Firebase JWT token in Authorization header:
```
Authorization: Bearer {firebase_jwt_token}
```

## Authentication Endpoints (`/auth/`)

### Auth Status
```http
GET /auth/status
Authorization: Bearer {token}

Response: 200 OK
{
  "authenticated": true,
  "user_id": "firebase_uid",
  "email": "user@example.com"
}
```

### Get Auth Profile
```http
GET /auth/profile
Authorization: Bearer {token}

Response: 200 OK
{
  "user_id": "firebase_uid",
  "email": "user@example.com",
  "display_name": "John Doe"
}
```

### Logout
```http
POST /auth/logout
Authorization: Bearer {token}

Response: 200 OK
{
  "message": "Successfully logged out"
}
```

### Test Endpoints (Development)
```http
GET /auth/test
Response: {"message": "Auth endpoint working"}

GET /auth/demo-protected
Authorization: Bearer {token}
Response: {"message": "Protected endpoint working", "user": {...}}
```

## User Management Endpoints (`/users/`)

### Register New User
```http
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "handle": "photographer123",
  "display_name": "John Doe",
  "primary_user_type": "photographer",
  "city_id": 1
}

Response: 201 Created
{
  "id": "firebase_uid",
  "email": "user@example.com",
  "handle": "photographer123",
  "display_name": "John Doe",
  "primary_user_type": "photographer",
  "created_at": "2025-08-11T10:00:00Z"
}
```

### Get My Full Profile
```http
GET /users/me
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "firebase_uid",
  "email": "user@example.com",
  "handle": "photographer123",
  "display_name": "John Doe",
  "bio": "Professional photographer specializing in portraits",
  "primary_user_type": "photographer",
  "city_name": "São Paulo",
  "experience_level": "professional",
  "location_preference": "studio_outdoor",
  "photography_styles": ["portrait", "fashion", "street"],
  "profile_image_url": "https://storage.googleapis.com/...",
  "created_at": "2025-08-11T10:00:00Z"
}
```

### Get My Public Profile
```http
GET /users/me/public
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "firebase_uid",
  "handle": "photographer123",
  "display_name": "John Doe",
  "bio": "Professional photographer",
  "primary_user_type": "photographer",
  "city_name": "São Paulo",
  "experience_level": "professional",
  "photography_styles": ["portrait", "fashion"],
  "profile_image_url": "https://storage.googleapis.com/..."
}
```

### Update My Profile
```http
PUT /users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "display_name": "John Smith",
  "bio": "Award-winning portrait photographer",
  "experience_level": "professional",
  "location_preference": "studio_preferred",
  "photography_styles": ["portrait", "fashion", "commercial"]
}

Response: 200 OK
{
  "id": "firebase_uid",
  "display_name": "John Smith",
  "bio": "Award-winning portrait photographer",
  "updated_at": "2025-08-11T15:30:00Z"
}
```

### Upload/Update Profile Image
```http
POST /users/me/profile-image
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- file: (image binary data)

Response: 200 OK
{
  "profile_image_url": "https://storage.googleapis.com/bucket/profiles/firebase_uid/profile.jpg?signed_url...",
  "message": "Profile image updated successfully"
}
```

### Delete Profile Image
```http
DELETE /users/me/profile-image
Authorization: Bearer {token}

Response: 200 OK
{
  "message": "Profile image deleted successfully"
}
```

### Get User Statistics
```http
GET /users/stats
Authorization: Bearer {token}

Response: 200 OK
{
  "total_photos": 150,
  "total_likes": 2340,
  "profile_views": 1200,
  "followers": 45
}
```

### Get Public User Profile
```http
GET /users/{user_id}/public

Response: 200 OK
{
  "id": "firebase_uid",
  "handle": "photographer123",
  "display_name": "John Doe",
  "bio": "Professional photographer",
  "primary_user_type": "photographer",
  "city_name": "São Paulo",
  "photography_styles": ["portrait", "fashion"]
}
```

### Search Users
```http
POST /users/search
Content-Type: application/json

{
  "query": "portrait photographer",
  "city": "São Paulo",
  "user_type": "photographer",
  "experience_level": "professional"
}

Response: 200 OK
{
  "users": [
    {
      "id": "firebase_uid",
      "handle": "photographer123",
      "display_name": "John Doe",
      "primary_user_type": "photographer",
      "city_name": "São Paulo",
      "experience_level": "professional"
    }
  ],
  "total": 25
}
```

### Get Reference Data
```http
GET /users/types
Response: ["photographer", "model", "makeup_artist", "stylist"]

GET /users/styles
Response: ["portrait", "fashion", "street", "landscape", "commercial", "wedding"]

GET /users/experience-levels
Response: ["beginner", "amateur", "semi_professional", "professional"]

GET /users/location-preferences
Response: ["studio_only", "outdoor_only", "studio_preferred", "outdoor_preferred", "studio_outdoor"]
```

## Photo Management Endpoints (`/photos/`)

### Upload Photo
```http
POST /photos/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- file: (image binary)
- title: "Golden Hour Portrait"
- description: "Professional portrait session at sunset"
- tags: ["portrait", "golden_hour", "professional"]
- camera_make: "Canon"
- camera_model: "EOS R5"
- lens: "RF 85mm F1.2"
- focal_length: 85
- aperture: 1.4
- shutter_speed: "1/200"
- iso: 100
- location_name: "Ibirapuera Park, São Paulo"

Response: 201 Created
{
  "id": "photo_uuid",
  "title": "Golden Hour Portrait",
  "image_url": "https://storage.googleapis.com/bucket/photos/user_id/photo_uuid.jpg?signed...",
  "thumbnail_url": "https://storage.googleapis.com/bucket/thumbnails/user_id/photo_uuid_thumb.jpg?signed...",
  "upload_date": "2025-08-11T18:30:00Z"
}
```

### Get Recent Photos (Feed)
```http
GET /photos/recent
Query Parameters:
- page: 1 (default)
- limit: 20 (default, max 50)

Response: 200 OK
{
  "photos": [
    {
      "id": "photo_uuid",
      "user_id": "firebase_uid",
      "title": "Mountain Landscape",
      "thumbnail_url": "https://storage.googleapis.com/...",
      "like_count": 24,
      "is_liked": false,
      "upload_date": "2025-08-11T16:00:00Z"
    }
  ],
  "total": 500,
  "page": 1,
  "limit": 20,
  "has_more": true
}
```

### Get All Photos (Public Feed)
```http
GET /photos/
Query Parameters:
- page: 1
- limit: 20

Response: Same as /recent
```

### Get My Photos
```http
GET /photos/my-photos
Authorization: Bearer {token}
Query Parameters:
- portfolio_only: true/false
- page: 1
- limit: 20

Response: 200 OK
{
  "photos": [
    {
      "id": "photo_uuid",
      "title": "Studio Portrait Session",
      "thumbnail_url": "https://storage.googleapis.com/...",
      "like_count": 42,
      "upload_date": "2025-08-11T15:30:00Z",
      "is_portfolio": true
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "has_more": true
}
```

### Get User's Photos
```http
GET /photos/user
Authorization: Bearer {token}
Query Parameters:
- page: 1
- limit: 20

Response: Same as /my-photos (for authenticated user's own photos)

GET /photos/user/{user_id}
Query Parameters:
- page: 1
- limit: 20

Response: 200 OK (public photos for specified user)
```

### Get Photo Details
```http
GET /photos/{photo_id}
Authorization: Bearer {token} (optional)

Response: 200 OK
{
  "id": "photo_uuid",
  "user_id": "firebase_uid",
  "title": "Studio Portrait Session",
  "description": "Professional headshot session with natural lighting",
  "image_url": "https://storage.googleapis.com/...",
  "thumbnail_url": "https://storage.googleapis.com/...",
  "camera_data": {
    "make": "Canon",
    "model": "EOS R5",
    "lens": "RF 85mm F1.2",
    "focal_length": 85,
    "aperture": 1.4,
    "shutter_speed": "1/200",
    "iso": 100
  },
  "location_name": "Studio São Paulo",
  "like_count": 42,
  "is_liked": true,
  "upload_date": "2025-08-11T15:30:00Z"
}
```

### Update Photo
```http
PUT /photos/{photo_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "tags": ["portrait", "studio", "professional"]
}

Response: 200 OK
{
  "id": "photo_uuid",
  "title": "Updated Title",
  "description": "Updated description",
  "updated_at": "2025-08-11T17:00:00Z"
}
```

### Delete Photo
```http
DELETE /photos/{photo_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "message": "Photo deleted successfully"
}
```

### Like/Unlike Photo
```http
POST /photos/{photo_id}/like
Authorization: Bearer {token}

Response: 200 OK
{
  "liked": true,
  "like_count": 43
}

# To unlike, send the same POST request again - it toggles
```

### Search Photos
```http
POST /photos/search
Content-Type: application/json

{
  "query": "portrait professional",
  "tags": ["portrait", "studio"],
  "location": "São Paulo",
  "user_type": "photographer"
}

Response: 200 OK
{
  "photos": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "has_more": true
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error: Email is required"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired authentication token"
}
```

### 403 Forbidden
```json
{
  "detail": "You don't have permission to modify this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Photo not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred"
}
```

## Rate Limiting & File Limits

- **File Upload**: Max 10MB per image
- **Supported Formats**: JPEG, PNG, WebP
- **Daily Limits**: 100 photo uploads per day
- **API Rate Limits**: 1000 requests per hour per authenticated user

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Image URLs are signed URLs with 1-hour expiration
- Profile images are automatically resized to 400x400px
- Photo thumbnails are automatically generated at 400x400px max
- Firebase UID is used as the primary user identifier throughout the system

---

*This document reflects the current API implementation as of August 11, 2025. For the latest changes, check the live documentation at /docs endpoint.*