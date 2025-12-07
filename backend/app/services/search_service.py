"""Search service for handling search logic"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from ..models.photo import Photo
from ..models.user import User
from ..models.series import Series

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db

    async def search(self, query: str) -> Dict[str, Any]:
        """Perform a search for photos, users, and series"""
        try:
            photos = self.db.query(Photo).filter(Photo.title.ilike(f"%{query}%")).all()
            users = self.db.query(User).filter(User.display_name.ilike(f"%{query}%")).all()
            series = self.db.query(Series).filter(Series.title.ilike(f"%{query}%")).all()

            return {
                "photos": photos,
                "users": users,
                "series": series
            }
        except Exception as e:
            logger.error(f"Failed to search: {str(e)}")
            raise Exception(f"Failed to search: {str(e)}")
