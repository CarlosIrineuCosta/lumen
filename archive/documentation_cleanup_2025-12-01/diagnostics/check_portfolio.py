#!/usr/bin/env python3
"""
Portfolio photo checker script

MOVED FROM: /check_portfolio.py to organized test structure
Updated paths and imports for new location
"""
import sys
sys.path.append('../../..')  # Updated path for new location

from app.database.connection import SessionLocal
from app.models.photo import Photo  # Fixed import path

db = SessionLocal()

# Check portfolio photos
portfolio_count = db.query(Photo).filter(Photo.is_portfolio == True).count()
total_count = db.query(Photo).count()

print(f'Portfolio photos: {portfolio_count}')
print(f'Total photos: {total_count}')
print('\nSample photos with is_portfolio field:')

photos = db.query(Photo).limit(10).all()
for p in photos:
    print(f'  - {p.title}: is_portfolio={p.is_portfolio}')

db.close()