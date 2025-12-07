-- Lumen Photography Platform - PostgreSQL Schema
-- Flexible design for evolution as platform grows

-- User types (Photographer/Model only)
CREATE TABLE user_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(20) UNIQUE NOT NULL,
    display_name VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Specialties (art-focused categories)
CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    applicable_to TEXT[] DEFAULT ARRAY['photographer', 'model'], -- Both by default
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Filtered cities (geopolitically relevant for art photography)
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    population INTEGER,
    is_capital BOOLEAN DEFAULT false,
    tier INTEGER DEFAULT 1, -- 1=liberal markets, 2=emerging, 3=selective, 4=very selective
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, country)
);

-- Main users table (flexible with JSONB for future expansion)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    handle VARCHAR(50) UNIQUE NOT NULL,
    
    -- Required core fields
    display_name VARCHAR(100) NOT NULL,
    city_id INTEGER REFERENCES cities(id) NOT NULL,
    primary_user_type INTEGER REFERENCES user_types(id) NOT NULL,
    
    -- Model-specific mandatory fields (NULL for photographers)
    gender VARCHAR(20), -- Male, Female, Non-binary, Other
    age INTEGER,
    height_cm INTEGER,
    weight_kg INTEGER,
    
    -- Optional physical characteristics (models)
    ethnicity VARCHAR(50),
    eye_color VARCHAR(30),
    hair_color VARCHAR(30),
    measurements JSONB, -- {chest: 90, waist: 60, hips: 90, dress_size: "M", shoe_size: 38}
    has_tattoos BOOLEAN DEFAULT false,
    has_piercings BOOLEAN DEFAULT false,
    
    -- Profile data
    profile_image_url VARCHAR(500),
    bio TEXT,
    website VARCHAR(500),
    
    -- Flexible expansion fields (JSONB for unknown future needs)
    profile_data JSONB DEFAULT '{}', -- {portfolio_url, gear, experience_years, languages, etc}
    availability_data JSONB DEFAULT '{}', -- {open_for_work, travel_range, rates, etc}
    privacy_settings JSONB DEFAULT '{"show_city": false, "show_country": true, "show_age": true}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User specialties (many-to-many)
CREATE TABLE user_specialties (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    specialty_id INTEGER REFERENCES specialties(id),
    is_primary BOOLEAN DEFAULT false, -- Mark main specialty
    experience_level VARCHAR(20) DEFAULT 'intermediate', -- beginner, intermediate, advanced, professional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, specialty_id)
);

-- Series table for photo collections
CREATE TABLE series (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Photos table (flexible metadata)
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    series_id UUID REFERENCES series(id) ON DELETE SET NULL, -- CORRECTED TYPE
    
    -- Core photo data
    title VARCHAR(200),
    description TEXT,
    image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    
    -- Location (optional)
    city_id INTEGER REFERENCES cities(id),
    location_name VARCHAR(200), -- Specific venue/studio name
    
    -- Technical metadata (flexible for different cameras/equipment)
    camera_data JSONB, -- {make, model, lens, settings: {iso, aperture, shutter, focal_length}}
    
    -- Content classification
    ai_tags JSONB, -- Auto-generated tags from AI processing
    user_tags TEXT[], -- User-defined tags
    content_rating VARCHAR(20) DEFAULT 'general', -- general, artistic_nude, mature
    
    -- Collaboration and rights
    is_collaborative BOOLEAN DEFAULT false,
    model_release_status VARCHAR(20) DEFAULT 'none', -- none, verbal, signed
    
    -- Flexible expansion
    extra_metadata JSONB DEFAULT '{}', -- Any future photo-related data
    
    -- Visibility and status
    is_public BOOLEAN DEFAULT true,
    is_portfolio BOOLEAN DEFAULT false, -- Curated portfolio piece vs general feed
    status VARCHAR(20) DEFAULT 'active', -- active, archived, deleted
    
    -- Timestamps
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Photo collaborators (@ tagging system)
CREATE TABLE photo_collaborators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    photo_id UUID REFERENCES photos(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL, -- NULL if user account deleted
    
    -- Always store display info (survives user deletion)
    display_name VARCHAR(100) NOT NULL,
    handle VARCHAR(50), -- For linking if user exists
    role VARCHAR(50), -- photographer, model, mua, stylist, etc
    
    -- Flexible role data
    role_data JSONB DEFAULT '{}', -- {credit_text, collaboration_type, etc}
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Photo interactions (likes, saves, etc)
CREATE TABLE photo_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    photo_id UUID REFERENCES photos(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20) NOT NULL, -- like, save, report, etc
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(photo_id, user_id, interaction_type)
);

-- User connections (networking)
CREATE TABLE user_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id UUID REFERENCES users(id) ON DELETE CASCADE,
    target_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, declined, blocked
    message TEXT, -- Initial connection message
    connection_data JSONB DEFAULT '{}', -- {collaboration_interest, project_types, etc}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(requester_id, target_id)
);

-- Indexes for performance
CREATE INDEX idx_users_city ON users(city_id);
CREATE INDEX idx_users_type ON users(primary_user_type);
CREATE INDEX idx_users_handle ON users(handle);
CREATE INDEX idx_photos_user ON photos(user_id);
CREATE INDEX idx_photos_series ON photos(series_id);
CREATE INDEX idx_photos_city ON photos(city_id);
CREATE INDEX idx_photos_created ON photos(created_at DESC);
CREATE INDEX idx_photos_public ON photos(is_public) WHERE is_public = true;
CREATE INDEX idx_photos_portfolio ON photos(is_portfolio) WHERE is_portfolio = true;
CREATE INDEX idx_user_specialties_user ON user_specialties(user_id);
CREATE INDEX idx_photo_collaborators_photo ON photo_collaborators(photo_id);
CREATE INDEX idx_photo_interactions_photo ON photo_interactions(photo_id);
CREATE INDEX idx_user_connections_users ON user_connections(requester_id, target_id);

-- Geographic search index (for nearby functionality)
CREATE INDEX idx_cities_location ON cities USING GIST(point(longitude, latitude));

-- JSON field indexes for common queries
CREATE INDEX idx_users_privacy ON users USING GIN(privacy_settings);
CREATE INDEX idx_photos_ai_tags ON photos USING GIN(ai_tags);
CREATE INDEX idx_photos_metadata ON photos USING GIN(metadata);

-- Update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_photos_updated_at BEFORE UPDATE ON photos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_connections_updated_at BEFORE UPDATE ON user_connections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();