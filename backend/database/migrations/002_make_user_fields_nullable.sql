-- Migration: Make user registration fields nullable for progressive completion
-- Date: 2025-08-15
-- Description: Allow users to register with minimal data and complete profile later

-- Make city_id nullable (users can select city during registration)
ALTER TABLE users ALTER COLUMN city_id DROP NOT NULL;

-- Make primary_user_type nullable (users can select type during registration)  
ALTER TABLE users ALTER COLUMN primary_user_type DROP NOT NULL;

-- Add index for better performance on nullable fields
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_city_id ON users(city_id) WHERE city_id IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_primary_user_type ON users(primary_user_type) WHERE primary_user_type IS NOT NULL;

-- Add constraint to ensure registered users have required fields
-- Note: This will be enforced in the API layer, not database level
-- ALTER TABLE users ADD CONSTRAINT check_registered_users 
--   CHECK (city_id IS NOT NULL AND primary_user_type IS NOT NULL);

-- Migration verification queries:
-- SELECT COUNT(*) FROM users WHERE city_id IS NULL; 
-- SELECT COUNT(*) FROM users WHERE primary_user_type IS NULL;

COMMENT ON COLUMN users.city_id IS 'City ID - nullable during registration, required after profile completion';
COMMENT ON COLUMN users.primary_user_type IS 'User type (1=photographer, 2=model, 3=studio) - nullable during registration';