#!/usr/bin/env python3
"""
Database Test Data Seeding System
Creates realistic database records for comprehensive testing
"""

import sys
import os
import json
import uuid
from datetime import datetime, timedelta, date
import random
from typing import List, Dict, Any
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set environment variables before importing app modules
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "postgresql:///lumen_test"

try:
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine, text
    from app.models.user import User
    from app.models.photo import Photo
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root and the backend environment is set up")
    sys.exit(1)


class DatabaseSeeder:
    """Handles seeding the database with test data"""
    
    def __init__(self, database_url: str = "postgresql:///lumen_test"):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
    
    def clear_test_data(self):
        """Clear all test data from database"""
        try:
            # Order matters due to foreign key constraints
            self.db.execute(text("TRUNCATE photo_interactions, photo_collaborators, user_connections, user_specialties, photos, users RESTART IDENTITY CASCADE"))
            self.db.commit()
            print("🧹 Cleared all test data from database")
        except Exception as e:
            self.db.rollback()
            print(f"⚠️ Warning: Could not truncate tables, trying delete: {e}")
            try:
                # Fallback to individual deletes
                self.db.execute(text("DELETE FROM photo_interactions"))
                self.db.execute(text("DELETE FROM photo_collaborators")) 
                self.db.execute(text("DELETE FROM user_connections"))
                self.db.execute(text("DELETE FROM user_specialties"))
                self.db.execute(text("DELETE FROM photos"))
                self.db.execute(text("DELETE FROM users"))
                self.db.commit()
                print("🧹 Cleared test data using DELETE statements")
            except Exception as e2:
                self.db.rollback()
                print(f"❌ Failed to clear test data: {e2}")
    
    def load_test_users(self) -> List[Dict[str, Any]]:
        """Load test user data from credentials file"""
        credentials_path = backend_path / "tests" / "fixtures" / "test_credentials.json"
        
        if not credentials_path.exists():
            print(f"❌ Test credentials file not found: {credentials_path}")
            print("Run scripts/create_test_users.py first")
            return []
        
        with open(credentials_path, 'r') as f:
            data = json.load(f)
        
        return data.get("users", [])
    
    def create_cities(self):
        """Create City records in database"""
        city_mapping = {
            "New York": 1, "Los Angeles": 2, "Chicago": 3, "Houston": 4, "Phoenix": 5,
            "Philadelphia": 6, "San Antonio": 7, "San Diego": 8, "Dallas": 9, "San Jose": 10,
            "Austin": 11, "Jacksonville": 12, "San Francisco": 13
        }
        try:
            for city_name, city_id in city_mapping.items():
                self.db.execute(text(f"INSERT INTO cities (id, name, country) VALUES ({city_id}, '{city_name}', 'USA') ON CONFLICT (id) DO NOTHING"))
            self.db.commit()
            print(f"✅ Created {len(city_mapping)} city records")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Failed to create cities: {e}")

    def create_user_types(self):
        """Create UserType records in database"""
        user_type_mapping = {
            "photographer": 1,
            "model": 2, 
            "makeup_artist": 3,
            "client": 4,
            "admin": 5
        }
        try:
            for type_name, type_id in user_type_mapping.items():
                self.db.execute(text(f"INSERT INTO user_types (id, type_name, display_name) VALUES ({type_id}, '{type_name}', '{type_name.replace('_', ' ').title()}') ON CONFLICT (id) DO NOTHING"))
            self.db.commit()
            print(f"✅ Created {len(user_type_mapping)} user type records")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Failed to create user types: {e}")

    def create_database_users(self, test_users: List[Dict[str, Any]]) -> List[User]:
        """Create User records in database from test user data"""
        
        # City mapping for IDs
        city_mapping = {
            "New York": 1, "Los Angeles": 2, "Chicago": 3, "Houston": 4, "Phoenix": 5,
            "Philadelphia": 6, "San Antonio": 7, "San Diego": 8, "Dallas": 9, "San Jose": 10,
            "Austin": 11, "Jacksonville": 12, "San Francisco": 13
        }
        
        # User type mapping
        user_type_mapping = {
            "photographer": 1,
            "model": 2, 
            "makeup_artist": 3,
            "client": 4,
            "admin": 5
        }
        
        created_users = []
        
        for user_data in test_users:
            profile = user_data["profile"]
            
            try:
                birth_date = self.generate_birth_date()
                tos_timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 180))
                country_code = profile.get("country_code", "USA")[:3].upper()

                # Create User record using the current ORM schema
                user = User(
                    id=profile.get("firebase_uid", str(uuid.uuid4())),
                    email=user_data["email"],
                    handle=profile["handle"],
                    display_name=user_data["display_name"],
                    bio=profile.get("bio", ""),
                    city_id=city_mapping.get(profile.get("city"), 1),
                    primary_user_type=user_type_mapping.get(profile.get("user_type"), 1),
                    birth_date=birth_date,
                    country_code=country_code,
                    tos_accepted_at=tos_timestamp,
                    profile_image_url=f"https://api.dicebear.com/7.x/avataaars/png?seed={profile['handle']}",
                    profile_data={
                        "specialties": profile.get("specialties", []),
                        "experience_years": profile.get("experience_years", 1),
                        "portfolio_url": profile.get("portfolio_url"),
                        "instagram": profile.get("instagram"),
                        "website": profile.get("website")
                    },
                    created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                    updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    last_active=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
                )
                
                self.db.add(user)
                created_users.append(user)
                
            except Exception as e:
                print(f"❌ Failed to create user {user_data['email']}: {e}")
                continue
        
        try:
            self.db.commit()
            print(f"✅ Created {len(created_users)} database user records")
            return created_users
        except Exception as e:
            self.db.rollback()
            print(f"❌ Failed to commit users: {e}")
            return []
    
    def create_sample_photos(self, users: List[User]) -> List[Photo]:
        """Create sample photo records for users"""
        
        photo_titles = [
            "Golden Hour Portrait", "Urban Street Scene", "Wedding Ceremony", "Fashion Editorial",
            "Landscape Sunset", "Studio Portrait", "Event Photography", "Commercial Product",
            "Nature Close-up", "Architectural Detail", "Candid Moment", "Artistic Composition",
            "Travel Photography", "Family Portrait", "Corporate Headshot", "Creative Concept",
            "Black and White Study", "Color Study", "Macro Photography", "Documentary Style"
        ]
        
        camera_makes = ["Canon", "Nikon", "Sony", "Fujifilm", "Leica", "Pentax", "Olympus"]
        camera_models = {
            "Canon": ["EOS R5", "EOS R6", "5D Mark IV", "1DX Mark III", "EOS RP"],
            "Nikon": ["D850", "Z7", "Z6", "D780", "Z5"],
            "Sony": ["A7R IV", "A7 III", "A9 II", "A6600", "FX3"],
            "Fujifilm": ["X-T4", "X-Pro3", "X100V", "GFX 100S", "X-T30"],
            "Leica": ["Q2", "M10-R", "SL2", "CL", "M10"],
            "Pentax": ["K-1 II", "K-3 III", "K-70", "KP", "645Z"],
            "Olympus": ["OM-D E-M1X", "OM-D E-M5 III", "PEN-F", "OM-D E-M10 IV", "Tough TG-6"]
        }
        
        created_photos = []
        
        # Create photos for photographers and some other user types
        photographer_users = [u for u in users if u.primary_user_type == 1]  # photographers
        other_users = [u for u in users if u.primary_user_type != 1]
        
        # Photographers get more photos
        for user in photographer_users:
            num_photos = random.randint(5, 20)
            for _ in range(num_photos):
                photo = self.create_single_photo(user, photo_titles, camera_makes, camera_models)
                if photo:
                    created_photos.append(photo)
        
        # Other users get fewer photos
        for user in other_users[:len(other_users)//2]:  # Only some non-photographers have photos
            num_photos = random.randint(1, 5)
            for _ in range(num_photos):
                photo = self.create_single_photo(user, photo_titles, camera_makes, camera_models)
                if photo:
                    created_photos.append(photo)
        
        try:
            self.db.commit()
            print(f"✅ Created {len(created_photos)} sample photo records")
            return created_photos
        except Exception as e:
            self.db.rollback()
            print(f"❌ Failed to commit photos: {e}")
            return []

    @staticmethod
    def generate_birth_date() -> date:
        """Return a realistic birth date for adult test users (ages 21-45)."""
        today = date.today()
        age_in_years = random.randint(21, 45)
        reference_year = today.year - age_in_years
        # Clamp day-of-year within range for the reference year
        day_offset = random.randint(0, 364)
        # Build a date safely by starting at Jan 1 of reference year
        return date(reference_year, 1, 1) + timedelta(days=day_offset)
    
    def create_single_photo(self, user: User, titles: List[str], makes: List[str], models: Dict[str, List[str]]) -> Photo:
        """Create a single photo record"""
        
        try:
            photo_id = str(uuid.uuid4())
            make = random.choice(makes)
            model = random.choice(models[make])
            
            # Generate realistic camera settings
            iso_values = [100, 200, 400, 800, 1600, 3200, 6400]
            apertures = [1.4, 1.8, 2.8, 4.0, 5.6, 8.0, 11.0]
            shutters = ["1/2000", "1/1000", "1/500", "1/250", "1/125", "1/60", "1/30"]
            focal_lengths = [24, 35, 50, 85, 105, 200, 300]
            
            photo = Photo(
                id=photo_id,
                user_id=user.id,
                title=random.choice(titles) + f" #{random.randint(1, 999)}",
                description=f"Captured with {make} {model}. {random.choice(['Professional shoot', 'Personal project', 'Client work', 'Creative exploration'])}.",
                image_url=f"https://picsum.photos/1200/800?random={photo_id}",
                thumbnail_url=f"https://picsum.photos/400/300?random={photo_id}",
                camera_data={
                    "make": make,
                    "model": model,
                    "settings": {
                        "iso": random.choice(iso_values),
                        "aperture": random.choice(apertures),
                        "shutter": random.choice(shutters),
                        "focal_length": random.choice(focal_lengths)
                    }
                },
                city_id=user.city_id,
                location_name=user.city.name if user.city else None,
                user_tags=random.sample(["portrait", "landscape", "street", "wedding", "fashion", "commercial", "artistic", "documentary"], k=random.randint(1, 3)),
                is_public=random.choice([True, True, True, False]),  # 75% public
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(photo)
            return photo
            
        except Exception as e:
            print(f"❌ Failed to create photo for {user.handle}: {e}")
            return None
    
    def create_user_connections(self, users: List[User]):
        """Create connections between users"""
        
        # Create some random connections
        num_connections = min(len(users) * 2, 50)  # Reasonable number of connections
        
        connections_created = 0
        
        for _ in range(num_connections):
            user1, user2 = random.sample(users, 2)
            
            # Check if connection already exists
            existing = self.db.execute(text("""
                SELECT 1 FROM user_connections 
                WHERE (requester_id = :uid1 AND target_id = :uid2) 
                   OR (requester_id = :uid2 AND target_id = :uid1)
            """), {"uid1": user1.id, "uid2": user2.id}).fetchone()
            
            if not existing:
                # Create bidirectional connection (mutual follow)
                try:
                    self.db.execute(text("""
                        INSERT INTO user_connections (requester_id, target_id, created_at, status)
                        VALUES (:uid1, :uid2, :created_at, 'accepted')
                    """), {
                        "uid1": user1.id,
                        "uid2": user2.id,
                        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 180))
                    })
                    
                    # Sometimes make it bidirectional
                    if random.choice([True, False]):
                        self.db.execute(text("""
                            INSERT INTO user_connections (requester_id, target_id, created_at, status)
                            VALUES (:uid2, :uid1, :created_at, 'accepted')
                        """), {
                            "uid1": user1.id,
                            "uid2": user2.id,
                            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 180))
                        })
                    
                    connections_created += 1
                    
                except Exception as e:
                    print(f"⚠️ Warning: Could not create connection: {e}")
                    continue
        
        try:
            self.db.commit()
            print(f"✅ Created {connections_created} user connections")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Failed to commit connections: {e}")
    
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main seeding function"""
    
    print("🌱 Database Test Data Seeding")
    print("=" * 40)
    
    try:
        seeder = DatabaseSeeder()
        
        # Clear existing test data
        print("🧹 Clearing existing test data...")
        seeder.clear_test_data()
        
        print("👥 Creating user type records...")
        seeder.create_user_types()

        print("🏙️ Creating city records...")
        seeder.create_cities()

        # Load test users from Firebase credentials
        print("👥 Loading test user profiles...")
        test_users = seeder.load_test_users()
        
        if not test_users:
            print("❌ No test users found. Run scripts/create_test_users.py first")
            return False
        
        print(f"📝 Found {len(test_users)} test users")
        
        # Create database user records
        print("🔧 Creating database user records...")
        db_users = seeder.create_database_users(test_users)
        
        if not db_users:
            print("❌ Failed to create database users")
            return False
        
        # Create sample photos
        print("📸 Creating sample photo records...")
        photos = seeder.create_sample_photos(db_users)
        
        # Create user connections
        print("🔗 Creating user connections...")
        seeder.create_user_connections(db_users)
        
        print("\n✅ Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   Users: {len(db_users)}")
        print(f"   Photos: {len(photos)}")
        print(f"   Database: lumen_test")
        
        print("\n💡 Test database is now ready for:")
        print("   • Authentication testing")
        print("   • Photo upload/retrieval")
        print("   • User profile operations") 
        print("   • Social features testing")
        print("   • API endpoint testing")
        
        seeder.close()
        return True
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
