-- Ensure cities table has default entry
INSERT INTO cities (id, name, country, region, latitude, longitude)
VALUES (1, 'Unknown', 'Unknown', NULL, 0, 0)
ON CONFLICT (id) DO NOTHING;

-- Ensure user_types table has all types
INSERT INTO user_types (id, type_name, display_name) VALUES
(1, 'photographer', 'Professional or amateur photographer'),
(2, 'model', 'Fashion, portrait, or artistic model'),
(3, 'studio', 'Photography studio or rental space'),
(4, 'makeup_artist', 'Makeup and styling professional'),
(5, 'stylist', 'Fashion and wardrobe stylist')
ON CONFLICT (id) DO NOTHING;

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_handle ON users(handle);