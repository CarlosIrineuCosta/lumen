-- Migration: Add series table and photo management fields
-- Date: November 2024
-- Purpose: Enable photo collections and user photo management

-- Create series table
CREATE TABLE IF NOT EXISTS series (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(128) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    cover_photo_id UUID,
    photo_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indices for performance
CREATE INDEX idx_series_user_id ON series(user_id);
CREATE INDEX idx_series_is_public ON series(is_public);
CREATE INDEX idx_series_created_at ON series(created_at DESC);

-- Add new columns to photos table
ALTER TABLE photos
ADD COLUMN IF NOT EXISTS series_id UUID REFERENCES series(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;

-- Add indices for the new photo columns
CREATE INDEX idx_photos_series_id ON photos(series_id);
CREATE INDEX idx_photos_is_deleted ON photos(is_deleted);
CREATE INDEX idx_photos_is_public ON photos(is_public);
CREATE INDEX idx_photos_user_id_not_deleted ON photos(user_id) WHERE is_deleted = false;

-- Add foreign key constraint for cover photo (after photos table has been altered)
ALTER TABLE series
ADD CONSTRAINT fk_series_cover_photo
FOREIGN KEY (cover_photo_id)
REFERENCES photos(id)
ON DELETE SET NULL;

-- Create trigger to update series.updated_at on change
CREATE OR REPLACE FUNCTION update_series_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER series_updated_at_trigger
BEFORE UPDATE ON series
FOR EACH ROW
EXECUTE FUNCTION update_series_updated_at();

-- Create function to update series photo count
CREATE OR REPLACE FUNCTION update_series_photo_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NEW.series_id IS NOT NULL) THEN
        UPDATE series
        SET photo_count = (
            SELECT COUNT(*)
            FROM photos
            WHERE series_id = NEW.series_id
            AND is_deleted = false
        )
        WHERE id = NEW.series_id;
    END IF;

    IF TG_OP = 'UPDATE' AND OLD.series_id IS NOT NULL AND OLD.series_id != NEW.series_id THEN
        UPDATE series
        SET photo_count = (
            SELECT COUNT(*)
            FROM photos
            WHERE series_id = OLD.series_id
            AND is_deleted = false
        )
        WHERE id = OLD.series_id;
    END IF;

    IF TG_OP = 'DELETE' AND OLD.series_id IS NOT NULL THEN
        UPDATE series
        SET photo_count = (
            SELECT COUNT(*)
            FROM photos
            WHERE series_id = OLD.series_id
            AND is_deleted = false
        )
        WHERE id = OLD.series_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER photos_series_count_trigger
AFTER INSERT OR UPDATE OR DELETE ON photos
FOR EACH ROW
EXECUTE FUNCTION update_series_photo_count();

-- Migration info
INSERT INTO migrations (name, applied_at)
VALUES ('003_add_series_and_photo_management', NOW())
ON CONFLICT (name) DO NOTHING;