# Lumen Code Style & Conventions

## Python/Backend Code Style

### General Conventions
- **Python Version**: 3.11.x
- **Line Length**: No strict limit, but reasonable (FastAPI examples show ~100-120 chars)
- **Import Organization**: Standard library → Third party → Local imports
- **Docstrings**: Triple quotes with descriptive function/class documentation

### FastAPI Patterns
```python
# Router definition
router = APIRouter()

# Endpoint with type hints and documentation
@router.get("/endpoint", response_model=ResponseModel)
async def endpoint_name(param: ParamType = Depends(dependency)):
    """
    Clear description of endpoint purpose
    """
    return response_data
```

### Pydantic Models
```python
class UserModel(BaseModel):
    """Clear model description"""
    field_name: str = Field(..., min_length=1, max_length=100)
    optional_field: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {"example": {...}}
```

### SQLAlchemy Models
```python
class User(Base):
    """Model description"""
    __tablename__ = "users"
    
    # Primary key and required fields first
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    required_field = Column(String(255), nullable=False)
    
    # Optional fields with defaults
    optional_field = Column(String(500))
    json_data = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships at end
    related_items = relationship("RelatedModel", back_populates="user")
```

### Error Handling
```python
# Consistent HTTP exception patterns
if not resource:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found"
    )
```

### Type Hints
- **Comprehensive**: All function parameters and return types
- **Standard**: `from typing import Optional, List, Dict, Any`
- **Pydantic Integration**: Use Pydantic models for request/response types

## Database Conventions

### Table Naming
- **Snake Case**: `user_types`, `photo_collaborators`
- **Descriptive**: Clear purpose from name
- **Singular Relations**: Foreign keys like `user_id`, `city_id`

### Column Conventions
- **JSONB Usage**: Flexible data in `profile_data`, `camera_data`, `privacy_settings`
- **UUID Primary Keys**: `gen_random_uuid()` default
- **Timestamp Patterns**: `created_at`, `updated_at` with timezone
- **Boolean Defaults**: Explicit defaults like `default=False`

### Schema Flexibility
```sql
-- Core required fields
display_name VARCHAR(100) NOT NULL,
city_id INTEGER REFERENCES cities(id) NOT NULL,

-- Model-specific mandatory (NULL for photographers)
gender VARCHAR(20),
age INTEGER,

-- Flexible expansion
profile_data JSONB DEFAULT {},
privacy_settings JSONB DEFAULT {'show_city': false, 'show_country': true}
```

## Frontend Code Style (Current Web Interface)

### JavaScript Patterns
- **ES6+ Syntax**: Arrow functions, const/let, template literals
- **Firebase Integration**: Consistent auth patterns
- **jQuery Usage**: Element selection and event handling
- **Modular Functions**: Clear separation of concerns

### CSS Organization
```css
:root {
    --primary-black: #0a0a0a;
    --secondary-black: #1a1a1a;
    --accent-gold: #d4af37;
}

/* Component-based organization */
.component-name {
    /* Layout properties first */
    display: flex;
    /* Visual properties second */
    background-color: var(--primary-black);
}
```

### HTML Structure
- **Semantic Elements**: Proper use of nav, main, section, article
- **Accessibility**: Alt text, proper labeling
- **Responsive Design**: Mobile-first approach

## API Design Conventions

### Endpoint Structure
```
/api/v1/
├── auth/
│   ├── test (public)
│   ├── status (protected)
│   └── profile (protected)
├── users/
│   ├── profile (GET/PUT)
│   ├── search (GET)
│   └── {user_id} (GET)
└── photos/
    ├── upload (POST)
    ├── stream (GET)
    ├── {photo_id} (GET/PUT/DELETE)
    └── user/{user_id} (GET)
```

### Response Patterns
```python
# Success responses
{
    "data": {...},
    "message": "Operation successful",
    "timestamp": "2025-08-03T10:30:00Z"
}

# Error responses
{
    "detail": "Specific error message",
    "error_code": "RESOURCE_NOT_FOUND"
}
```

## Documentation Conventions

### Code Comments
- **Minimal Inline Comments**: Code should be self-documenting
- **Docstrings Required**: All classes, functions, and modules
- **Business Logic Explanation**: Complex algorithms and business rules

### API Documentation
- **FastAPI Auto-docs**: Leverage built-in documentation
- **Response Models**: Clear Pydantic models for all endpoints
- **Examples**: Realistic example data in schema

## File Organization

### Backend Structure
```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── api/
│   │   └── endpoints/          # Route handlers by domain
│   ├── models/                 # SQLAlchemy and Pydantic models
│   ├── services/               # Business logic layer
│   ├── database/               # Database connection and utilities
│   └── utils/                  # Shared utilities
├── database/
│   ├── schema.sql              # Database schema
│   └── seed_data.sql           # Sample data
└── requirements.txt            # Dependencies
```

### Frontend Structure
```
frontend/
├── css/
│   └── lumen.css              # Main stylesheet
├── js/
│   └── lumen-gallery.js       # Gallery functionality
├── public/                    # Static assets
└── *.html                     # Page templates
```

## Testing Conventions

### Backend Testing
- **Test Files**: Located in `backend/tests/` (when implemented)
- **Test Naming**: `test_feature_functionality.py`
- **Fixtures**: Shared test data and setup

### API Testing
- **Test Clients**: Current HTML test clients in frontend/
- **Endpoint Coverage**: Test all public and protected endpoints
- **Authentication**: Test both authenticated and unauthenticated access

## Environment Configuration

### Environment Variables
- **Required Variables**: All documented in `.env.example`
- **Naming Convention**: `SCREAMING_SNAKE_CASE`
- **Security**: Sensitive data in Google Secret Manager

## Version Control

### Commit Conventions
- **Clear Messages**: Descriptive commit messages
- **Atomic Commits**: Single logical change per commit
- **No Sensitive Data**: Service account keys and secrets excluded

### Branch Strategy
- **Main Branch**: Production-ready code
- **Feature Development**: Direct commits during MVP phase
- **Future**: Feature branches for post-MVP development