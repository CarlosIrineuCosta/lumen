#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Migration SQL
migration_sql = """
-- Migration: Add Series support (one photo per series)
-- Date: 2025-09-03

-- 1. Create series table
CREATE TABLE IF NOT EXISTS series (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL REFERENCES users(firebase_uid),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  cover_photo_id UUID,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  photo_count INTEGER DEFAULT 0
);

-- 2. Add series_id to photos (NULL = not in any series)
ALTER TABLE photos 
ADD COLUMN IF NOT EXISTS series_id INTEGER REFERENCES series(id) ON DELETE SET NULL;

-- 3. Add foreign key for cover photo (skip if exists)
DO $$ BEGIN
  ALTER TABLE series 
  ADD CONSTRAINT fk_series_cover_photo 
  FOREIGN KEY (cover_photo_id) REFERENCES photos(id) ON DELETE SET NULL;
EXCEPTION
  WHEN duplicate_object THEN null;
END $$;

-- 4. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_series_user ON series(user_id);
CREATE INDEX IF NOT EXISTS idx_photos_series ON photos(series_id);

-- 5. Add display_type enum if not exists
DO $$ BEGIN
  CREATE TYPE gallery_type AS ENUM ('gallery', 'portfolio', 'both');
EXCEPTION
  WHEN duplicate_object THEN null;
END $$;

ALTER TABLE photos 
ADD COLUMN IF NOT EXISTS display_type gallery_type DEFAULT 'gallery';
"""

def run_migration():
    try:
        # Connect to database
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Execute migration
        print("Running migration...")
        cur.execute(migration_sql)
        conn.commit()
        
        # Verify series table exists
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'series';")
        result = cur.fetchone()
        
        if result:
            print("✅ Series table created successfully")
        else:
            print("❌ Series table not found")
            
        # Check if series_id was added to photos
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'photos' AND column_name = 'series_id';
        """)
        result = cur.fetchone()
        
        if result:
            print("✅ series_id column added to photos table")
        else:
            print("❌ series_id column not found in photos table")
            
        cur.close()
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()