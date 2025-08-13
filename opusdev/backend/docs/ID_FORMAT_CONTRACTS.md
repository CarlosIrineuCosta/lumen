# ID Format Contracts

This document defines the precise ID format contracts used throughout the Lumen application. These contracts ensure consistency between Firebase Authentication, PostgreSQL database, Google Cloud Storage, and all application layers.

## Overview

The Lumen application uses two primary identifier types:
- **Firebase UIDs**: 28-character alphanumeric strings for user identification
- **UUIDs**: Standard UUID4 format for photos and other entities

## Critical System Dependencies

**WARNING**: Changes to these ID format contracts can break the entire photo loading system! The following systems must remain synchronized:

1. **Firebase Authentication**: Provides 28-character UID strings
2. **PostgreSQL Database**: Stores these UIDs as primary keys
3. **Google Cloud Storage**: Uses UID strings in file paths
4. **Photo Service**: Generates signed URLs using consistent ID formats

## Layer-by-Layer Contracts

### 1. Authentication Layer

**Firebase Authentication**
- **Input**: OAuth providers (Google, etc.)
- **Output**: Firebase UID strings
- **Format**: 28-character alphanumeric strings
- **Examples**: 
  - `9pGzwsVBRMaSxMOZ6QNTJJjnl1b2`
  - `abcd1234efgh5678ijkl9012mnop3456`

**AuthUser Interface**
```python
class AuthUser:
    uid: str  # Firebase UID (28-char alphanumeric)
    email: str
    name: Optional[str]
```

**Contract Requirements**:
- Firebase UID MUST be exactly 28 characters
- Firebase UID MUST contain only alphanumeric characters [a-zA-Z0-9]
- Firebase UID MUST NOT contain special characters, spaces, or Unicode

### 2. Database Layer

**Users Table**
```sql
CREATE TABLE users (
    id VARCHAR(128) PRIMARY KEY,  -- Firebase UID stored as string
    email VARCHAR(255) UNIQUE NOT NULL,
    handle VARCHAR(50) UNIQUE NOT NULL,
    -- ... other fields
);
```

**Photos Table**
```sql
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- UUID4 for photos
    user_id VARCHAR(128) NOT NULL REFERENCES users(id),  -- Firebase UID reference
    -- ... other fields
);
```

**Related Tables** (all use same pattern)
```sql
-- All user references use Firebase UID strings
user_id VARCHAR(128) REFERENCES users(id)

-- All photo references use UUID
photo_id UUID REFERENCES photos(id)
```

**Contract Requirements**:
- `users.id` MUST store Firebase UID as string (not UUID)
- `photos.id` MUST be UUID4 format
- All `user_id` foreign key columns MUST reference Firebase UID strings
- All `photo_id` foreign key columns MUST reference UUID format

### 3. Storage Layer (Google Cloud Storage)

**File Path Structure**
```
gs://lumen-photos-20250731/
├── photos/
│   └── {firebase_uid}/
│       └── {photo_uuid}.{extension}
└── thumbnails/
    └── {firebase_uid}/
        └── {photo_uuid}_thumb.{extension}
```

**Path Examples**
```
photos/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/c711a9ab-4689-4576-a511-7ce60cc214f3.jpg
thumbnails/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/c711a9ab-4689-4576-a511-7ce60cc214f3_thumb.jpg
```

**Contract Requirements**:
- User folder names MUST be Firebase UID strings (28-char alphanumeric)
- Photo filenames MUST use UUID string format (with hyphens)
- Path separators MUST be forward slashes
- File extensions MUST be lowercase
- Thumbnail files MUST include `_thumb` suffix before extension

### 4. API Layer

**Request/Response Formats**

Photo Upload Request:
```json
{
  "title": "string",
  "description": "string",
  // ... other fields
}
```

Photo Response:
```json
{
  "id": "c711a9ab-4689-4576-a511-7ce60cc214f3",  // UUID as string
  "title": "string",
  "image_url": "https://storage.googleapis.com/...",
  "thumbnail_url": "https://storage.googleapis.com/...",
  // ... other fields
}
```

User Profile Response:
```json
{
  "id": "9pGzwsVBRMaSxMOZ6QNTJJjnl1b2",  // Firebase UID as string
  "email": "user@example.com",
  "display_name": "string",
  // ... other fields
}
```

**Contract Requirements**:
- All photo IDs in API responses MUST be UUID strings (with hyphens)
- All user IDs in API responses MUST be Firebase UID strings
- API endpoints accepting photo IDs MUST validate UUID format
- API endpoints accepting user IDs MUST validate Firebase UID format

### 5. Service Layer

**PhotoService Contract**
```python
class PhotoService:
    async def upload_photo(
        self, 
        firebase_user: AuthUser,  # Must have valid Firebase UID
        file_content: bytes,
        filename: str,
        content_type: str,
        request: CreatePhotoRequest
    ) -> PhotoResponse:
        # Returns photo with string UUID in response
        pass
    
    def _generate_photo_urls(
        self, 
        photo_id: uuid.UUID,  # Accepts UUID object
        firebase_uid: str     # Must be valid Firebase UID string
    ) -> tuple[str, str]:
        # Returns (image_url, thumbnail_url)
        pass
```

**IDManagementService Contract**
```python
class IDManagementService:
    def normalize_user_id(self, user_id: Any) -> str:
        # Always returns validated Firebase UID string
        pass
    
    def normalize_photo_id(self, photo_id: Any, return_uuid: bool = False) -> Union[str, uuid.UUID]:
        # Returns UUID string or object based on return_uuid parameter
        pass
    
    def generate_storage_paths(self, user_id: Any, photo_id: Any) -> tuple[str, str]:
        # Returns (photo_path, thumbnail_path) with validated IDs
        pass
```

**Contract Requirements**:
- All service methods MUST validate input ID formats
- All service methods MUST use ID validation utilities
- Service methods MUST raise `IDValidationError` for invalid formats
- Internal service operations MUST use consistent string formatting

## Validation Rules

### Firebase UID Validation
```python
# Pattern: Exactly 28 alphanumeric characters
FIREBASE_UID_PATTERN = r'^[a-zA-Z0-9]{28}$'

# Valid examples:
"9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"
"abcd1234efgh5678ijkl9012mnop3456"
"ABCD1234EFGH5678IJKL9012MNOP3456"

# Invalid examples:
"short"                              # Too short
"9pGzwsVBRMaSxMOZ6QNTJJjnl1b2extra" # Too long
"9pGzwsVBRMaSxMOZ6QNTJJjnl1b!"      # Special character
""                                   # Empty string
None                                 # Null value
```

### UUID Validation
```python
# Pattern: Standard UUID4 format with hyphens
UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'

# Valid examples:
uuid.uuid4()                                        # UUID object
"550e8400-e29b-41d4-a716-446655440000"             # UUID string
"c711a9ab-4689-4576-a511-7ce60cc214f3"             # UUID string

# Invalid examples:
"not-a-uuid"                         # Invalid format
"550e8400-e29b-41d4-a716"           # Too short
"9pGzwsVBRMaSxMOZ6QNTJJjnl1b2"     # Firebase UID (wrong type)
""                                   # Empty string
None                                 # Null value
```

## Error Handling Contracts

### IDValidationError Format
```python
class IDValidationError(Exception):
    def __init__(self, message: str, id_value: any, expected_type: IDType):
        self.id_value = id_value
        self.expected_type = expected_type
        super().__init__(f"{message}. Got: '{id_value}' (type: {type(id_value).__name__}), expected: {expected_type.value}")
```

### Error Response Format
```json
{
  "detail": "Invalid Firebase UID in photo upload. Got: 'invalid-uid!' (type: str), expected: firebase_uid",
  "type": "id_validation_error"
}
```

## Migration Considerations

### Adding New ID Types
When adding new identifier types:

1. **Define validation pattern** in `app/utils/id_validation.py`
2. **Add to IDType enum** with descriptive name
3. **Create validation function** following existing patterns
4. **Update IDManagementService** with new methods
5. **Add database constraints** if storing in PostgreSQL
6. **Update API documentation** with new format requirements
7. **Add comprehensive tests** in integration test suite

### Changing Existing ID Formats
**WARNING**: Changing existing ID formats requires careful migration:

1. **Audit existing data** using IDManagementService audit methods
2. **Create migration scripts** to update database records
3. **Plan GCS file migrations** if path formats change
4. **Update all validation patterns** consistently
5. **Test extensively** with integration test suite
6. **Deploy with rollback plan** in case of issues

## Testing Contracts

### Unit Tests
- Every ID validation function MUST have tests for valid and invalid inputs
- Tests MUST cover edge cases (empty strings, None values, wrong types)
- Tests MUST verify exact error messages and types

### Integration Tests
- End-to-end photo upload/retrieval flow MUST be tested
- Database consistency checks MUST be tested
- GCS path generation MUST be tested
- Service layer integration MUST be tested

### Performance Considerations
- ID validation MUST complete in < 1ms for typical cases
- Large batch operations MUST use efficient validation patterns
- Database queries MUST use appropriate indexes on ID columns

## Monitoring and Observability

### Logging Requirements
All ID validation operations MUST log:
- Operation context and description
- Input ID values and detected types
- Validation results (success/failure)
- Generated paths for GCS operations

### Error Tracking
ID validation errors MUST be tracked with:
- Error frequency and patterns
- Common invalid input types
- Performance impact of validation
- User impact of validation failures

## Security Considerations

### ID Format Security
- Firebase UIDs are NOT sensitive but should not be enumerable
- UUIDs provide sufficient entropy to prevent guessing
- ID validation prevents injection attacks through malformed inputs
- Storage paths using IDs prevent unauthorized file access

### Access Control
- Firebase UID verification ensures user identity
- Photo UUID ownership must be verified before operations
- Cross-user access requires explicit permission checks
- Invalid ID formats must be rejected before database queries

## Future-Proofing

This contract system is designed to support:
- Additional identifier types (e.g., organization IDs, album IDs)
- Migration to different storage backends
- Enhanced validation requirements
- Performance optimizations
- Security enhancements

All changes to ID formats MUST follow the established patterns in this document and maintain backward compatibility where possible.