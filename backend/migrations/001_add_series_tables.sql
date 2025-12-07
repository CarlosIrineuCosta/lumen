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

-- 3. Add foreign key for cover photo
ALTER TABLE series 
ADD CONSTRAINT fk_series_cover_photo 
FOREIGN KEY (cover_photo_id) REFERENCES photos(id) ON DELETE SET NULL;

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