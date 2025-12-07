"""
Data Mappers for the service layer.

These functions handle the transformation of data between different layers of the application,
(e.g., from API models to Service DTOs, or from DB models to Service DTOs).
This centralizes mapping logic and provides a clear audit trail.
"""

import logging
from ..api.endpoints.users import UpdateUserRequest
from .dtos import UserProfileUpdateDTO

logger = logging.getLogger(__name__)

def map_update_request_to_dto(request: UpdateUserRequest) -> UserProfileUpdateDTO:
    """Maps the API's UpdateUserRequest to the service's UserProfileUpdateDTO."""
    
    update_data = request.dict(exclude_unset=True, by_alias=False)
    
    logger.info(f"Mapping API request to service DTO. Raw data: {update_data}")
    
    # Here you could add more complex mapping logic, validation, or enrichment.
    # For now, it's a direct mapping of the fields that are present.
    
    dto = UserProfileUpdateDTO(**update_data)
    
    logger.info(f"Successfully mapped to DTO: {dto.dict()}")
    
    return dto
