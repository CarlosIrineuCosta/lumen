# Lumen - API Reference

**FOR CLAUDE CODE - API ENDPOINTS AND INTEGRATION**

## Base URL
- **Development**: http://100.106.201.33:8080/api/v1
- **Documentation**: http://100.106.201.33:8080/docs

## Authentication

All protected endpoints require Firebase JWT token in Authorization header:
```
Authorization: Bearer {firebase_jwt_token}
```

### Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "photographer123",
  "display_name": "John Doe"
}

Response: 200 OK
{
  "user_id": "uuid",
  "email": "user@example.com",
  "username": "photographer123",
  "created_at": "2025-08-03T10:00:00Z"
}
```

#### Get Auth Status
```http
GET /api/v1/auth/status
Authorization: Bearer {token}

Response: 200 OK
{
  "authenticated": true,
  "user_id": "uuid",
  "email": "user@example.com"
}
```

#### Get User Profile
```http
GET /api/v1/auth/profile
Authorization: Bearer {token}

Response: 200 OK
{
  "user_id": "uuid",
  "email": "user@example.com",
  "username": "photographer123",
  "display_name": "John Doe",
  "bio": "Professional photographer",
  "profile_image_url": "https://storage.googleapis.com/...",
  "location_city": "São Paulo",
  "location_country": "Brazil",
  "is_professional": true,
  "portfolio_url": "https://johndoe.photography"
}
```

## Photo Management

#### Upload Photo
```http
POST /api/v1/photos/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- file: (binary)
- title: "Sunset Portrait"
- description: "Golden hour shoot at the beach"
- tags: ["portrait", "beach", "golden hour"]

Response: 201 Created
{
  "photo_id": "uuid",
  "filename": "sunset_portrait.jpg",
  "original_url": "https://storage.googleapis.com/...",
  "thumbnail_url": "https://storage.googleapis.com/...",
  "upload_date": "2025-08-03T15:30:00Z"
}
```

#### Get My Photos
```http
GET /api/v1/photos/my-photos
Authorization: Bearer {token}
Query Parameters:
- page: 1
- limit: 20

Response: 200 OK
{
  "photos": [
    {
      "photo_id": "uuid",
      "title": "Sunset Portrait",
      "thumbnail_url": "https://storage.googleapis.com/...",
      "likes_count": 42,
      "upload_date": "2025-08-03T15:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

#### Get Recent Photos (Feed)
```http
GET /api/v1/photos/recent
Query Parameters:
- page: 1
- limit: 20

Response: 200 OK
{
  "photos": [
    {
      "photo_id": "uuid",
      "user": {
        "user_id": "uuid",
        "username": "photographer123",
        "display_name": "John Doe",
        "profile_image_url": "https://..."
      },
      "title": "Mountain Landscape",
      "thumbnail_url": "https://storage.googleapis.com/...",
      "likes_count": 24,
      "upload_date": "2025-08-03T16:00:00Z",
      "is_liked": false
    }
  ],
  "total": 500,
  "page": 1,
  "pages": 25
}
```

#### Get Photo Details
```http
GET /api/v1/photos/{photo_id}

Response: 200 OK
{
  "photo_id": "uuid",
  "user": {
    "user_id": "uuid",
    "username": "photographer123",
    "display_name": "John Doe"
  },
  "title": "Mountain Landscape",
  "description": "Shot at sunrise in the Alps",
  "original_url": "https://storage.googleapis.com/...",
  "camera_make": "Canon",
  "camera_model": "EOS R5",
  "lens": "RF 24-70mm F2.8",
  "focal_length": 35,
  "aperture": 2.8,
  "shutter_speed": "1/250",
  "iso": 100,
  "location_name": "Swiss Alps",
  "tags": ["landscape", "mountains", "sunrise"],
  "likes_count": 24,
  "upload_date": "2025-08-03T16:00:00Z"
}
```

#### Update Photo
```http
PUT /api/v1/photos/{photo_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "New description",
  "tags": ["landscape", "nature"]
}

Response: 200 OK
{
  "photo_id": "uuid",
  "title": "Updated Title",
  "updated_at": "2025-08-03T17:00:00Z"
}
```

#### Delete Photo
```http
DELETE /api/v1/photos/{photo_id}
Authorization: Bearer {token}

Response: 204 No Content
```

## Engagement

#### Like Photo
```http
POST /api/v1/photos/{photo_id}/like
Authorization: Bearer {token}

Response: 200 OK
{
  "liked": true,
  "likes_count": 43
}
```

#### Unlike Photo
```http
DELETE /api/v1/photos/{photo_id}/like
Authorization: Bearer {token}

Response: 200 OK
{
  "liked": false,
  "likes_count": 42
}
```

## Discovery (To Be Implemented)

#### Search Photos
```http
GET /api/v1/search/photos
Query Parameters:
- q: "portrait outdoor"
- tags: ["portrait", "outdoor"]
- location: "São Paulo"
- page: 1
- limit: 20

Response: 200 OK
{
  "photos": [...],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

#### Find Nearby Photographers
```http
GET /api/v1/photographers/nearby
Authorization: Bearer {token}
Query Parameters:
- radius: 30 (km)
- specialties: ["portrait", "fashion"]

Response: 200 OK
{
  "photographers": [
    {
      "user_id": "uuid",
      "username": "photographer123",
      "display_name": "John Doe",
      "distance_km": 12.5,
      "specialties": ["portrait", "fashion", "editorial"],
      "portfolio_sample": ["url1", "url2", "url3"]
    }
  ],
  "total": 15
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "message": "Email is required",
  "field": "email"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "You don't have permission to modify this resource"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "message": "Photo not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

- **Anonymous**: 100 requests per hour
- **Authenticated**: 1000 requests per hour
- **Upload**: 50 photos per day

Headers returned:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1691074800
```

---

*This document provides API reference for Lumen platform endpoints. For implementation details, see CODE-technical-implementation.md*