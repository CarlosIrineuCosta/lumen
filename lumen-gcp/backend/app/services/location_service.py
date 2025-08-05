"""Location resolution service for Lumen Photography Platform"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.lookup_tables import City


class LocationService:
    """Service for resolving location strings to city IDs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def resolve_city(self, location_string: str) -> Optional[int]:
        """
        Resolve a location string to a city_id
        
        Args:
            location_string: User input like "New York", "London, UK", "Paris, France"
        
        Returns:
            city_id if found, None otherwise
        """
        if not location_string or not location_string.strip():
            return None
            
        location = location_string.strip()
        
        # Try exact match first (case insensitive)
        city = self.db.query(City).filter(
            func.lower(City.name) == func.lower(location)
        ).first()
        
        if city:
            return city.id
            
        # Try with country if comma separated
        if ',' in location:
            parts = [part.strip() for part in location.split(',')]
            if len(parts) >= 2:
                city_name, country_name = parts[0], parts[1]
                
                city = self.db.query(City).filter(
                    func.lower(City.name) == func.lower(city_name),
                    func.lower(City.country) == func.lower(country_name)
                ).first()
                
                if city:
                    return city.id
        
        # Try partial match on city name
        city = self.db.query(City).filter(
            func.lower(City.name).contains(func.lower(location))
        ).first()
        
        if city:
            return city.id
            
        return None
    
    def get_city_info(self, city_id: int) -> Optional[Tuple[str, str]]:
        """
        Get city info by ID
        
        Returns:
            (city_name, country) tuple if found, None otherwise
        """
        city = self.db.query(City).filter(City.id == city_id).first()
        if city:
            return (city.name, city.country)
        return None
    
    def search_cities(self, query: str, limit: int = 10) -> list:
        """
        Search cities by name for autocomplete
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of city dictionaries with id, name, country
        """
        if not query or len(query) < 2:
            return []
            
        cities = self.db.query(City).filter(
            func.lower(City.name).contains(func.lower(query))
        ).limit(limit).all()
        
        return [
            {
                "id": city.id,
                "name": city.name,
                "country": city.country,
                "display": f"{city.name}, {city.country}"
            }
            for city in cities
        ]