-- Migration 004: Add Legal Compliance Fields
-- Adds birth_date, country_code, and tos_accepted_at to users table
-- Date: 2025-08-17

BEGIN;

-- Add new columns to users table
ALTER TABLE users 
ADD COLUMN birth_date DATE,
ADD COLUMN country_code VARCHAR(3),
ADD COLUMN tos_accepted_at TIMESTAMP WITH TIME ZONE;

-- For now, set these as nullable to handle existing users
-- We'll populate default values for existing users in a separate script

-- Add indexes for performance
CREATE INDEX idx_users_country_code ON users(country_code);
CREATE INDEX idx_users_birth_date ON users(birth_date);

-- Add comments for documentation
COMMENT ON COLUMN users.birth_date IS 'User birth date for age verification';
COMMENT ON COLUMN users.country_code IS 'ISO country code for legal age validation';
COMMENT ON COLUMN users.tos_accepted_at IS 'Timestamp when user accepted Terms of Service';

COMMIT;