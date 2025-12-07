-- Migration: Add category field to photos table
-- Date: 2025-09-17
-- Description: Add category field to support art photography taxonomy

-- Add category column to photos table
ALTER TABLE photos
ADD COLUMN category VARCHAR(50) DEFAULT 'portrait';

-- Add comment to document the field
COMMENT ON COLUMN photos.category IS 'Photography category: portrait, artistic_nude, boudoir, lingerie, bikini, dark, fetish';

-- Update existing photos with categories (demo data assignment)
-- Since we don't have actual category data, we'll set some initial values
UPDATE photos SET category = 'portrait' WHERE id IS NOT NULL;

-- Add index for better filtering performance
CREATE INDEX idx_photos_category ON photos(category);

-- Optional: Add check constraint to ensure valid categories
ALTER TABLE photos
ADD CONSTRAINT chk_photos_category
CHECK (category IN ('portrait', 'artistic_nude', 'boudoir', 'lingerie', 'bikini', 'dark', 'fetish'));