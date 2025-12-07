#!/usr/bin/env python3
"""
Test Photo Management System
Creates and uploads realistic test photos for development and testing
"""

import os
import sys
import json
import requests
import uuid
from typing import List, Dict, Any, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
import tempfile
from datetime import datetime

# Add backend path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


class TestPhotoGenerator:
    """Generates synthetic test photos with EXIF-like metadata"""
    
    def __init__(self):
        self.photo_categories = {
            "portrait": {
                "colors": [(120, 90, 70), (210, 180, 140), (139, 115, 85), (205, 175, 145)],
                "titles": ["Professional Headshot", "Studio Portrait", "Corporate Photo", "Personal Portrait", "Artistic Portrait"]
            },
            "landscape": {
                "colors": [(70, 130, 180), (34, 139, 34), (255, 140, 0), (220, 20, 60)],
                "titles": ["Mountain Vista", "Sunset Landscape", "Forest Path", "Ocean View", "Desert Scene"]
            },
            "street": {
                "colors": [(105, 105, 105), (169, 169, 169), (128, 128, 128), (192, 192, 192)],
                "titles": ["Urban Life", "Street Photography", "City Scene", "Candid Moment", "Architecture"]
            },
            "fashion": {
                "colors": [(0, 0, 0), (255, 255, 255), (255, 20, 147), (138, 43, 226)],
                "titles": ["Fashion Editorial", "Style Photo", "Model Portfolio", "Fashion Week", "Editorial Shoot"]
            },
            "wedding": {
                "colors": [(255, 255, 255), (255, 182, 193), (255, 105, 180), (255, 215, 0)],
                "titles": ["Wedding Ceremony", "Bridal Portrait", "Reception", "Wedding Party", "Couple Portrait"]
            }
        }
    
    def generate_photo(self, category: str, width: int = 1200, height: int = 800) -> Tuple[BytesIO, Dict[str, Any]]:
        """Generate a synthetic photo with metadata"""
        
        if category not in self.photo_categories:
            category = "portrait"
        
        cat_data = self.photo_categories[category]
        
        # Create image
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create gradient background
        base_color = random.choice(cat_data["colors"])
        for y in range(height):
            # Create gradient effect
            ratio = y / height
            color = tuple(int(base_color[i] * (0.7 + 0.3 * ratio)) for i in range(3))
            draw.line([(0, y), (width, y)], fill=color)
        
        # Add some geometric shapes for interest
        for _ in range(random.randint(2, 6)):
            shape_type = random.choice(['rectangle', 'ellipse', 'line'])
            color = tuple(random.randint(0, 255) for _ in range(3))
            
            if shape_type == 'rectangle':
                x1, y1 = random.randint(0, width//2), random.randint(0, height//2)
                x2, y2 = random.randint(x1, width), random.randint(y1, height)
                draw.rectangle([x1, y1, x2, y2], fill=color, width=random.randint(1, 5))
            elif shape_type == 'ellipse':
                x1, y1 = random.randint(0, width//2), random.randint(0, height//2)
                x2, y2 = random.randint(x1, width), random.randint(y1, height)
                draw.ellipse([x1, y1, x2, y2], fill=color, width=random.randint(1, 5))
            else:  # line
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = random.randint(0, width), random.randint(0, height)
                draw.line([x1, y1, x2, y2], fill=color, width=random.randint(2, 8))
        
        # Add category text
        try:
            # Try to use a system font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        text = f"{category.upper()}"
        draw.text((50, 50), text, fill=(255, 255, 255), font=font)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((50, height - 100), f"Test Photo - {timestamp}", fill=(255, 255, 255))
        
        # Convert to bytes
        img_buffer = BytesIO()
        image.save(img_buffer, format='JPEG', quality=85)
        img_buffer.seek(0)
        
        # Generate metadata
        metadata = {
            "category": category,
            "title": random.choice(cat_data["titles"]),
            "width": width,
            "height": height,
            "camera_data": self.generate_camera_metadata(),
            "description": f"Test {category} photo generated for development testing",
            "tags": self.generate_tags(category),
            "created_at": datetime.now().isoformat()
        }
        
        return img_buffer, metadata
    
    def generate_camera_metadata(self) -> Dict[str, Any]:
        """Generate realistic camera metadata"""
        
        cameras = [
            {"make": "Canon", "model": "EOS R5"},
            {"make": "Nikon", "model": "D850"},
            {"make": "Sony", "model": "A7R IV"},
            {"make": "Fujifilm", "model": "X-T4"},
            {"make": "Leica", "model": "Q2"}
        ]
        
        camera = random.choice(cameras)
        
        return {
            "make": camera["make"],
            "model": camera["model"],
            "settings": {
                "iso": random.choice([100, 200, 400, 800, 1600, 3200]),
                "aperture": random.choice([1.4, 1.8, 2.8, 4.0, 5.6, 8.0]),
                "shutter": random.choice(["1/2000", "1/1000", "1/500", "1/250", "1/125", "1/60"]),
                "focal_length": random.choice([24, 35, 50, 85, 105, 200])
            }
        }
    
    def generate_tags(self, category: str) -> List[str]:
        """Generate relevant tags for a photo category"""
        
        base_tags = {
            "portrait": ["portrait", "headshot", "professional", "studio", "person"],
            "landscape": ["landscape", "nature", "outdoors", "scenic", "travel"],
            "street": ["street", "urban", "city", "documentary", "candid"],
            "fashion": ["fashion", "style", "editorial", "model", "commercial"],
            "wedding": ["wedding", "ceremony", "celebration", "couple", "event"]
        }
        
        common_tags = ["photography", "digital", "color", "professional", "artistic"]
        
        tags = random.sample(base_tags.get(category, []), k=random.randint(2, 4))
        tags.extend(random.sample(common_tags, k=random.randint(1, 2)))
        
        return tags


class TestPhotoUploader:
    """Handles uploading test photos to the Lumen backend"""
    
    def __init__(self, backend_url: str = "http://localhost:8080"):
        self.backend_url = backend_url
        self.generator = TestPhotoGenerator()
    
    def get_auth_token(self, email: str, password: str) -> str:
        """Get authentication token from Firebase emulator"""
        
        auth_url = "http://localhost:9099/www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        try:
            response = requests.post(
                auth_url,
                params={"key": "fake-api-key-for-emulator"},
                json=payload
            )
            
            if response.status_code == 200:
                return response.json().get('idToken')
            else:
                print(f"❌ Auth failed for {email}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Auth error for {email}: {e}")
            return None
    
    def upload_photo_for_user(self, user_email: str, user_password: str, category: str) -> Dict[str, Any]:
        """Upload a generated photo for a specific user"""
        
        # Get auth token
        token = self.get_auth_token(user_email, user_password)
        if not token:
            return {"success": False, "error": "Authentication failed"}
        
        # Generate photo
        photo_buffer, metadata = self.generator.generate_photo(category)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(photo_buffer.read())
            temp_file_path = temp_file.name
        
        try:
            # Upload to backend
            upload_url = f"{self.backend_url}/api/photos/upload"
            
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            files = {
                'file': ('test_photo.jpg', open(temp_file_path, 'rb'), 'image/jpeg')
            }
            
            data = {
                'title': metadata['title'],
                'description': metadata['description'],
                'tags': ','.join(metadata['tags']),
                'is_public': 'true',
                'camera_make': metadata['camera_data']['make'],
                'camera_model': metadata['camera_data']['model'],
                'camera_settings': json.dumps(metadata['camera_data']['settings'])
            }
            
            response = requests.post(upload_url, headers=headers, files=files, data=data)
            
            files['file'][1].close()  # Close file handle
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "photo_id": result.get('id'),
                    "metadata": metadata,
                    "user": user_email
                }
            else:
                return {
                    "success": False,
                    "error": f"Upload failed: {response.status_code} - {response.text}",
                    "user": user_email
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Upload error: {e}",
                "user": user_email
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass


def load_test_users() -> List[Dict[str, Any]]:
    """Load test users from credentials file"""
    
    credentials_path = backend_path / "tests" / "fixtures" / "test_credentials.json"
    
    if not credentials_path.exists():
        print(f"❌ Test credentials file not found: {credentials_path}")
        print("Run scripts/create_test_users.py first")
        return []
    
    with open(credentials_path, 'r') as f:
        data = json.load(f)
    
    return data.get("users", [])


def main():
    """Main photo upload automation"""
    
    print("📸 Test Photo Upload Automation")
    print("=" * 40)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code != 200:
            raise Exception("Backend health check failed")
    except Exception as e:
        print("❌ Backend server not running on localhost:8080")
        print("Start it first, then run this script")
        return False
    
    # Check if Firebase emulator is running
    try:
        requests.get("http://localhost:9099", timeout=5)
    except Exception as e:
        print("❌ Firebase emulator not running on localhost:9099")
        print("Start it with: firebase emulators:start --only auth,storage")
        return False
    
    # Load test users
    print("👥 Loading test users...")
    users = load_test_users()
    
    if not users:
        return False
    
    print(f"📝 Found {len(users)} test users")
    
    uploader = TestPhotoUploader()
    
    # Upload photos for each user
    total_uploads = 0
    successful_uploads = 0
    
    categories = list(uploader.generator.photo_categories.keys())
    
    for user in users:
        user_type = user["profile"].get("user_type", "photographer")
        
        # Photographers get more photos
        if user_type == "photographer":
            num_photos = random.randint(3, 8)
        elif user_type in ["model", "makeup_artist"]:
            num_photos = random.randint(2, 5)
        else:
            num_photos = random.randint(1, 3)
        
        print(f"\n📤 Uploading {num_photos} photos for {user['email']} ({user_type})...")
        
        user_categories = categories.copy()
        random.shuffle(user_categories)
        
        for i in range(num_photos):
            category = user_categories[i % len(user_categories)]
            
            result = uploader.upload_photo_for_user(
                user["email"],
                user["password"],
                category
            )
            
            total_uploads += 1
            
            if result["success"]:
                successful_uploads += 1
                print(f"  ✅ Uploaded {category} photo: {result['metadata']['title']}")
            else:
                print(f"  ❌ Failed to upload {category} photo: {result['error']}")
    
    print(f"\n📊 Upload Summary:")
    print(f"   Total attempts: {total_uploads}")
    print(f"   Successful: {successful_uploads}")
    print(f"   Failed: {total_uploads - successful_uploads}")
    print(f"   Success rate: {(successful_uploads/total_uploads*100):.1f}%")
    
    print(f"\n✅ Photo upload automation completed!")
    print("💡 Photos are now available for:")
    print("   • API endpoint testing")
    print("   • Photo retrieval testing") 
    print("   • UI gallery testing")
    print("   • Search and filtering tests")
    
    return successful_uploads > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)