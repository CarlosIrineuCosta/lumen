"""Search endpoints for Lumen API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from sqlalchemy.orm import Session

from ..services.search_service import SearchService
from ..database.connection import get_db

router = APIRouter()

@router.get("/")
async def search(
    query: str = Query(..., min_length=3),
    db: Session = Depends(get_db)
):
    """Search for photos, users, and series"""
    try:
        search_service = SearchService(db)
        results = await search_service.search(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search: {str(e)}")
