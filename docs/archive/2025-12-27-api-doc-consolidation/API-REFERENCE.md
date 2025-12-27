# Lumen API Reference

**Base URL**: `http://100.106.201.33:8080/api/v1`  
**Authentication**: Firebase JWT tokens in Authorization header

## Authentication Endpoints

### Check Authentication Status
```http
GET /auth/status
```

**Response**:
```json
{
  "authenticated": true,
  "user_id": "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
}
```

### Get Auth Profile
```http
GET /auth/profile
Authorization: Bearer {firebase_token}
```

**Response**:
```json
{
  "uid": "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2",
  "email": "user@example.com",
  "email_verified": true
}
```

### Logout
```http
POST /auth/logout
Authorization: Bearer {firebase_token}
```

## User Endpoints

### Register New User
```http
POST /users/register
Authorization: Bearer {firebase_token}
Content-Type: application/json

{
  "handle": "photographer123",
  "display_name": "John Doe",
  "primary_user_type_id": 1,
  "experience_level_id": 2,
  "city_id": 150
}
```

### Get Current User Profile
```http
GET /users/me
Authorization: Bearer {firebase_token}
```

**Response**:
```json
{
  "id": "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2",
  "email": "user@example.com",
  "handle": "photographer123",
  "display_name": "John Doe",
  "bio": "Professional photographer",
  "profile_image_url": "https://storage.googleapis.com/...",
  "primary_user_type": {
    "id": 1,
    "name": "Photographer"
  },
  "experience_level": {
    "id": 2,
    "name": "Intermediate"
  },
  "city": {
    "id": 150,
    "name": "San Francisco",
    "country": "United States"
  },
  "created_at": "2025-08-01T12:00:00Z"
}
```

### Update User Profile
```http
PUT /users/me
Authorization: Bearer {firebase_token}
Content-Type: application/json

{
  "display_name": "John Doe Updated",
  "bio": "Updated bio text",
  "primary_user_type_id": 1,
  "experience_level_id": 3,
  "city_id": 200
}
```

### Upload Profile Image
```http
POST /users/me/profile-image
Authorization: Bearer {firebase_token}
Content-Type: multipart/form-data

file: [binary image data]
```

### Delete Profile Image
```http
DELETE /users/me/profile-image
Authorization: Bearer {firebase_token}
```

### Get User Statistics
```http
GET /users/stats
Authorization: Bearer {firebase_token}
```

**Response**:
```json
{
  "total_photos": 25,
  "total_likes": 150,
  "portfolio_photos": 10
}
```

### View Other User's Profile
```http
GET /users/{user_id}/public
```

### Search Users
```http
POST /users/search
Content-Type: application/json

{
  "user_type_id": 1,
  "city_id": 150,
  "experience_level_id": 3,
  "page": 1,
  "limit": 20
}
```

## Photo Endpoints

### Upload Photo
```http
POST /photos/upload
Authorization: Bearer {firebase_token}
Content-Type: multipart/form-data

file: [binary image data]
title: "Sunset at the Beach"
description: "Beautiful sunset captured at Ocean Beach"
tags: ["sunset", "beach", "landscape"]
is_portfolio: true
```

**Response**:
```json
{
  "id": "c711a9ab-4689-4576-a511-7ce60cc214f3",
  "user_id": "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2",
  "title": "Sunset at the Beach",
  "image_url": "https://storage.googleapis.com/...",
  "thumbnail_url": "https://storage.googleapis.com/...",
  "upload_date": "2025-08-13T15:30:00Z"
}
```

### Get Recent Photos
```http
GET /photos/recent?page=1&limit=20
```

**Response**:
```json
{
  "photos": [
    {
      "id": "c711a9ab-4689-4576-a511-7ce60cc214f3",
      "title": "Sunset at the Beach",
      "image_url": "https://storage.googleapis.com/...",
      "thumbnail_url": "https://storage.googleapis.com/...",
      "user": {
        "id": "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2",
        "handle": "photographer123",
        "display_name": "John Doe"
      },
      "likes_count": 5,
      "is_liked": false
    }
  ],
  "page": 1,
  "limit": 20,
  "total": 150,
  "has_more": true
}
```

### Get User's Photos
```http
GET /photos/user/{user_id}?portfolio_only=true&page=1&limit=20
```

### Get Photo Details
```http
GET /photos/{photo_id}
```

**Response**:
```json
{
  "id": "c711a9ab-4689-4576-a511-7ce60cc214f3",
  "user_id": "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2",
  "title": "Sunset at the Beach",
  "description": "Beautiful sunset captured at Ocean Beach",
  "image_url": "https://storage.googleapis.com/...",
  "thumbnail_url": "https://storage.googleapis.com/...",
  "tags": ["sunset", "beach", "landscape"],
  "camera_data": {
    "make": "Canon",
    "model": "EOS R5",
    "lens": "RF 24-70mm F2.8",
    "focal_length": 35,
    "aperture": 8.0,
    "shutter_speed": "1/250",
    "iso": 100
  },
  "is_public": true,
  "is_portfolio": true,
  "likes_count": 5,
  "upload_date": "2025-08-13T15:30:00Z"
}
```

### Update Photo
```http
PUT /photos/{photo_id}
Authorization: Bearer {firebase_token}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "tags": ["sunset", "ocean", "california"],
  "is_portfolio": false
}
```

### Delete Photo
```http
DELETE /photos/{photo_id}
Authorization: Bearer {firebase_token}
```

### Like/Unlike Photo
```http
POST /photos/{photo_id}/like
Authorization: Bearer {firebase_token}
```

**Response**:
```json
{
  "liked": true,
  "likes_count": 6
}
```

### Search Photos
```http
POST /photos/search
Content-Type: application/json

{
  "query": "sunset beach",
  "tags": ["landscape"],
  "city_id": 150,
  "page": 1,
  "limit": 20
}
```

## Reference Data Endpoints

### Get User Types
```http
GET /users/types
```

**Response**:
```json
[
  {"id": 1, "name": "Photographer"},
  {"id": 2, "name": "Model"},
  {"id": 3, "name": "Makeup Artist"},
  {"id": 4, "name": "Stylist"}
]
```

### Get Photography Styles
```http
GET /users/styles
```

**Response**:
```json
[
  {"id": 1, "name": "Portrait"},
  {"id": 2, "name": "Landscape"},
  {"id": 3, "name": "Street"},
  {"id": 4, "name": "Fashion"}
]
```

### Get Experience Levels
```http
GET /users/experience-levels
```

**Response**:
```json
[
  {"id": 1, "name": "Beginner"},
  {"id": 2, "name": "Intermediate"},
  {"id": 3, "name": "Advanced"},
  {"id": 4, "name": "Professional"}
]
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently no rate limiting is implemented. This will be added before production launch.

## CORS Configuration

Development CORS allows:
- http://localhost:8000
- http://100.106.201.33:8000

Production CORS will be restricted to the deployed frontend domain.

---

*For interactive API documentation, visit http://100.106.201.33:8080/docs*