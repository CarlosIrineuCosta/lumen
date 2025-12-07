"""
Series (Photo Collections) API endpoints
Allows photographers to organize photos into collections
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from app.database.connection import get_db
from app.models.series import Series
from app.models.photo import Photo
from app.auth_middleware import get_current_user


router = APIRouter(prefix="/series", tags=["series"])


# Pydantic schemas
class SeriesCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = True


class SeriesUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_photo_id: Optional[UUID] = None


class SeriesResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    photo_count: int
    is_public: bool
    cover_photo_id: Optional[UUID]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class SeriesAddPhotos(BaseModel):
    photo_ids: List[UUID]


@router.get("", response_model=List[SeriesResponse])
async def get_user_series(
    skip: int = 0,
    limit: int = 50,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all series for the current user"""
    series = db.query(Series).filter(
        Series.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return series


@router.post("", response_model=SeriesResponse)
async def create_series(
    series_data: SeriesCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new photo series"""
    series = Series(
        user_id=current_user.id,
        title=series_data.title,
        description=series_data.description,
        is_public=series_data.is_public
    )

    db.add(series)
    db.commit()
    db.refresh(series)

    return series


@router.get("/{series_id}", response_model=SeriesResponse)
async def get_series(
    series_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific series"""
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    return series


@router.put("/{series_id}", response_model=SeriesResponse)
async def update_series(
    series_id: int,
    series_data: SeriesUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a series"""
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    # Update fields
    for field, value in series_data.dict(exclude_unset=True).items():
        setattr(series, field, value)

    db.commit()
    db.refresh(series)

    return series


@router.delete("/{series_id}")
async def delete_series(
    series_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a series (photos become unassigned)"""
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    # Remove series assignment from all photos
    db.query(Photo).filter(Photo.series_id == series_id).update({"series_id": None})

    # Delete the series
    db.delete(series)
    db.commit()

    return {"message": "Series deleted successfully"}


@router.post("/{series_id}/photos")
async def add_photos_to_series(
    series_id: int,
    photo_data: SeriesAddPhotos,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add photos to a series"""
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    # Verify all photos belong to current user
    photos = db.query(Photo).filter(
        Photo.id.in_(photo_data.photo_ids),
        Photo.user_id == current_user.id,
        Photo.is_deleted == False
    ).all()

    if len(photos) != len(photo_data.photo_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some photos not found or don't belong to you"
        )

    # Add photos to series
    for photo in photos:
        photo.series_id = series_id

    # Set first photo as cover if series doesn't have one
    if not series.cover_photo_id and photos:
        series.cover_photo_id = photos[0].id

    db.commit()

    return {"message": f"Added {len(photos)} photos to series"}


@router.delete("/{series_id}/photos")
async def remove_photos_from_series(
    series_id: int,
    photo_data: SeriesAddPhotos,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove photos from a series"""
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    # Remove photos from series
    updated_count = db.query(Photo).filter(
        Photo.id.in_(photo_data.photo_ids),
        Photo.series_id == series_id,
        Photo.user_id == current_user.id
    ).update({"series_id": None})

    # If cover photo was removed, pick a new one
    if series.cover_photo_id in photo_data.photo_ids:
        remaining_photo = db.query(Photo).filter(
            Photo.series_id == series_id,
            Photo.is_deleted == False
        ).first()
        series.cover_photo_id = remaining_photo.id if remaining_photo else None

    db.commit()

    return {"message": f"Removed {updated_count} photos from series"}


@router.get("/{series_id}/photos")
async def get_series_photos(
    series_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all photos in a series"""
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.user_id == current_user.id
    ).first()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Series not found"
        )

    photos = db.query(Photo).filter(
        Photo.series_id == series_id,
        Photo.is_deleted == False
    ).offset(skip).limit(limit).all()

    return photos