-- Insert dummy photographers into database
-- Note: Replace the Firebase UIDs with the actual ones created

INSERT INTO users (
    id, email, handle, display_name, bio, city_id, primary_user_type,
    profile_data, availability_data, privacy_settings,
    created_at, updated_at, last_active
) VALUES 
(
    '5lZhgKApMYetBdOh8290zypRyIh1',
    'dummy.carla.74349fb9@test.com',
    'dummycarla6084',
    'Dummy Carla',
    'Fine art photographer specializing in intimate portraiture.',
    1,
    1,
    '{"photography_styles": ["artistic_nude", "portrait", "fashion", "beauty"], "artistic_statement": "Beauty emerges through vulnerability and authentic human connection.", "mission_statement": "Creating powerful imagery through São Paulo-based photography.", "experience_level": "professional", "experience_years": 8, "specializes_in": ["artistic nude photography", "portrait work"], "camera_gear": ["Canon EOS R5", "85mm f/1.8"]}',
    '{"open_for_work": true, "available_for_travel": true, "available_for_collaborations": true, "rate_range": "$300-650", "location_preferences": ["studio", "outdoor", "urban"]}',
    '{"show_city": true, "show_country": true, "show_age": false}',
    NOW(),
    NOW(),
    NOW()
),
(
    'rUpaKIiFdbTWojg1HtswPHulN8u2',
    'dummy.charles.7e2a2323@test.com',
    'dummycharles4810',
    'Dummy Charles',
    'Professional photographer with editorial experience.',
    2,
    1,
    '{"photography_styles": ["artistic_nude", "portrait", "fashion", "editorial"], "artistic_statement": "Exploring the intersection of light and human emotion.", "mission_statement": "Creating powerful imagery through Los Angeles-based photography.", "experience_level": "professional", "experience_years": 12, "specializes_in": ["artistic nude photography", "portrait work"], "camera_gear": ["Nikon D850", "50mm f/1.4"]}',
    '{"open_for_work": true, "available_for_travel": false, "available_for_collaborations": true, "rate_range": "$400-800", "location_preferences": ["studio", "outdoor", "urban"]}',
    '{"show_city": true, "show_country": true, "show_age": false}',
    NOW(),
    NOW(),
    NOW()
),
(
    '3rgJ9mpEUTXp6d52urAii0ZhrGJ2',
    'dummy.joe.67c86c44@test.com',
    'dummyjoe3534',
    'Dummy Joe',
    'Contemporary artist focusing on minimalist compositions.',
    3,
    1,
    '{"photography_styles": ["artistic_nude", "portrait", "commercial", "beauty"], "artistic_statement": "Simplicity reveals the essence of artistic expression.", "mission_statement": "Creating powerful imagery through Miami-based photography.", "experience_level": "semi_pro", "experience_years": 5, "specializes_in": ["artistic nude photography", "portrait work"], "camera_gear": ["Sony A7R IV", "24-70mm f/2.8"]}',
    '{"open_for_work": true, "available_for_travel": true, "available_for_collaborations": true, "rate_range": "$250-500", "location_preferences": ["studio", "outdoor", "urban"]}',
    '{"show_city": true, "show_country": true, "show_age": false}',
    NOW(),
    NOW(),
    NOW()
),
(
    'pa8e3PeXqcOfxOe7pCOWeV6R7rI3',
    'dummy.alex.8eddeae0@test.com',
    'dummyalex9838',
    'Dummy Alex',
    'Experimental photographer blending traditional and modern techniques.',
    4,
    1,
    '{"photography_styles": ["artistic_nude", "portrait", "fashion", "conceptual"], "artistic_statement": "Art challenges boundaries and invites new perspectives.", "mission_statement": "Creating powerful imagery through Portland-based photography.", "experience_level": "amateur", "experience_years": 3, "specializes_in": ["artistic nude photography", "portrait work"], "camera_gear": ["Canon EOS R5", "50mm f/1.4"]}',
    '{"open_for_work": true, "available_for_travel": false, "available_for_collaborations": true, "rate_range": "$200-400", "location_preferences": ["studio", "outdoor", "urban"]}',
    '{"show_city": true, "show_country": true, "show_age": false}',
    NOW(),
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Verify insertion
SELECT id, display_name, handle, city_id FROM users WHERE handle LIKE 'dummy%';