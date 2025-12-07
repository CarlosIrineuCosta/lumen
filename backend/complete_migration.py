#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def complete_migration():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        print("Completing migration...")
        
        # Add series_id to photos
        print("Adding series_id column...")
        cur.execute("""
            ALTER TABLE photos 
            ADD COLUMN IF NOT EXISTS series_id INTEGER REFERENCES series(id) ON DELETE SET NULL;
        """)
        
        # Add display_type enum and column
        print("Adding display_type...")
        cur.execute("""
            DO $$ BEGIN
              CREATE TYPE gallery_type AS ENUM ('gallery', 'portfolio', 'both');
            EXCEPTION
              WHEN duplicate_object THEN null;
            END $$;
        """)
        
        cur.execute("""
            ALTER TABLE photos 
            ADD COLUMN IF NOT EXISTS display_type gallery_type DEFAULT 'gallery';
        """)
        
        # Create indexes
        print("Creating indexes...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_series_user ON series(user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_photos_series ON photos(series_id);")
        
        conn.commit()
        
        # Verify
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'photos' AND column_name = 'series_id';")
        if cur.fetchone():
            print("✅ series_id column added successfully")
        
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'photos' AND column_name = 'display_type';")
        if cur.fetchone():
            print("✅ display_type column added successfully")
            
        cur.close()
        conn.close()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    complete_migration()