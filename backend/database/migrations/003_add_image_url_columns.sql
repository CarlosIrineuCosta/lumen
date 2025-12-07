-- Migration: Add image_url and thumbnail_url columns to photos table
-- Date: 2025-08-15
-- Purpose: Fix photo upload database constraint violations

-- Add image_url and thumbnail_url columns to photos table
ALTER TABLE photos 
ADD COLUMN image_url VARCHAR(500),
ADD COLUMN thumbnail_url VARCHAR(500);

-- Set image_url as NOT NULL after adding the column
-- (We'll add the NOT NULL constraint after we have data in existing rows)
-- For now, allow NULL to handle existing records

-- Update any existing photos to have a placeholder URL structure
-- This ensures the constraint won't fail for existing records
UPDATE photos 
SET image_url = CONCAT('http://100.106.201.33:8000/storage/images/original/', user_id, '/', id, '.jpg'),
    thumbnail_url = CONCAT('http://100.106.201.33:8000/storage/images/thumb/', user_id, '/', id, '.jpg')
WHERE image_url IS NULL;

-- Now we can safely add the NOT NULL constraint on image_url
ALTER TABLE photos 
ALTER COLUMN image_url SET NOT NULL;

-- thumbnail_url can remain nullable as it's optional