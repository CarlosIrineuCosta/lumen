-- Lumen Photography Platform - Seed Data
-- Initial data for platform launch

-- User types
INSERT INTO user_types (type_name, display_name) VALUES 
('photographer', 'Photographer'),
('model', 'Model');

-- Specialties (art-focused, no brands/street)
INSERT INTO specialties (name, description, applicable_to) VALUES 
('Art Nude', 'Artistic nude photography emphasizing form and aesthetics', ARRAY['photographer', 'model']),
('Portrait', 'Professional portrait photography', ARRAY['photographer', 'model']),
('Dance', 'Dance photography and performance art', ARRAY['photographer', 'model']),
('Yoga', 'Yoga and wellness photography', ARRAY['photographer', 'model']),
('Tattoo', 'Tattoo and body art photography', ARRAY['photographer', 'model']),
('Creative', 'Creative and conceptual photography', ARRAY['photographer', 'model']),
('Editorial', 'Editorial and magazine-style photography', ARRAY['photographer', 'model']),
('Beauty', 'Beauty and makeup photography', ARRAY['photographer', 'model']),
('Pole Dance', 'Pole dance and aerial arts photography', ARRAY['photographer', 'model']),
('Lifestyle', 'Lifestyle and natural photography', ARRAY['photographer', 'model']),
('Fitness', 'Fitness and sports photography', ARRAY['photographer', 'model']),
('Bikini', 'Swimwear and beach photography', ARRAY['photographer', 'model']);

-- Sample cities (will be expanded with GeoNames data)
-- Tier 1: Liberal art markets
INSERT INTO cities (name, country, region, latitude, longitude, population, is_capital, tier) VALUES 
-- United States (major cities)
('New York', 'United States', 'New York', 40.7128, -74.0060, 8400000, false, 1),
('Los Angeles', 'United States', 'California', 34.0522, -118.2437, 4000000, false, 1),
('Chicago', 'United States', 'Illinois', 41.8781, -87.6298, 2700000, false, 1),
('Miami', 'United States', 'Florida', 25.7617, -80.1918, 470000, false, 1),
('San Francisco', 'United States', 'California', 37.7749, -122.4194, 880000, false, 1),
('Washington', 'United States', 'District of Columbia', 38.9072, -77.0369, 700000, true, 1),

-- Canada
('Toronto', 'Canada', 'Ontario', 43.6532, -79.3832, 2930000, false, 1),
('Vancouver', 'Canada', 'British Columbia', 49.2827, -123.1207, 630000, false, 1),
('Montreal', 'Canada', 'Quebec', 45.5017, -73.5673, 1780000, false, 1),
('Ottawa', 'Canada', 'Ontario', 45.4215, -75.6972, 990000, true, 1),

-- Western Europe
('London', 'United Kingdom', 'England', 51.5074, -0.1278, 9000000, true, 1),
('Paris', 'France', 'Île-de-France', 48.8566, 2.3522, 2200000, true, 1),
('Berlin', 'Germany', 'Berlin', 52.5200, 13.4050, 3700000, true, 1),
('Amsterdam', 'Netherlands', 'North Holland', 52.3676, 4.9041, 870000, true, 1),
('Barcelona', 'Spain', 'Catalonia', 41.3851, 2.1734, 1620000, false, 1),
('Madrid', 'Spain', 'Community of Madrid', 40.4168, -3.7038, 3200000, true, 1),
('Rome', 'Italy', 'Lazio', 41.9028, 12.4964, 2870000, true, 1),
('Milan', 'Italy', 'Lombardy', 45.4642, 9.1900, 1400000, false, 1),
('Vienna', 'Austria', 'Vienna', 48.2082, 16.3738, 1900000, true, 1),
('Zurich', 'Switzerland', 'Zurich', 47.3769, 8.5417, 420000, false, 1),

-- Australia & New Zealand
('Sydney', 'Australia', 'New South Wales', -33.8688, 151.2093, 5300000, false, 1),
('Melbourne', 'Australia', 'Victoria', -37.8136, 144.9631, 5000000, false, 1),
('Brisbane', 'Australia', 'Queensland', -27.4705, 153.0260, 2560000, false, 1),
('Canberra', 'Australia', 'Australian Capital Territory', -35.2809, 149.1300, 430000, true, 1),
('Auckland', 'New Zealand', 'Auckland', -36.8485, 174.7633, 1700000, false, 1),
('Wellington', 'New Zealand', 'Wellington', -41.2865, 174.7762, 420000, true, 1),

-- Japan
('Tokyo', 'Japan', 'Tokyo', 35.6762, 139.6503, 14000000, true, 1),
('Osaka', 'Japan', 'Osaka', 34.6937, 135.5023, 19000000, false, 1),
('Kyoto', 'Japan', 'Kyoto', 35.0116, 135.7681, 1460000, false, 1),

-- Tier 2: Emerging art markets
-- Brazil
('São Paulo', 'Brazil', 'São Paulo', -23.5558, -46.6396, 12300000, false, 2),
('Rio de Janeiro', 'Brazil', 'Rio de Janeiro', -22.9068, -43.1729, 6700000, false, 2),
('Brasília', 'Brazil', 'Distrito Federal', -15.8267, -47.9218, 3100000, true, 2),
('Salvador', 'Brazil', 'Bahia', -12.9714, -38.5014, 2900000, false, 2),
('Belo Horizonte', 'Brazil', 'Minas Gerais', -19.9167, -43.9345, 2500000, false, 2),
('Florianópolis', 'Brazil', 'Santa Catarina', -27.5954, -48.5480, 510000, false, 2),

-- Mexico
('Mexico City', 'Mexico', 'Mexico City', 19.4326, -99.1332, 9200000, true, 2),
('Guadalajara', 'Mexico', 'Jalisco', 20.6597, -103.3496, 1500000, false, 2),
('Monterrey', 'Mexico', 'Nuevo León', 25.6866, -100.3161, 1130000, false, 2),
('Cancún', 'Mexico', 'Quintana Roo', 21.1619, -86.8515, 890000, false, 2),
('Puerto Vallarta', 'Mexico', 'Jalisco', 20.6534, -105.2253, 290000, false, 2),

-- Argentina
('Buenos Aires', 'Argentina', 'Buenos Aires', -34.6118, -58.3960, 15200000, true, 2),
('Córdoba', 'Argentina', 'Córdoba', -31.4201, -64.1888, 1500000, false, 2),

-- Chile
('Santiago', 'Chile', 'Santiago Metropolitan', -33.4489, -70.6693, 6200000, true, 2),
('Valparaíso', 'Chile', 'Valparaíso', -33.0472, -71.6127, 930000, false, 2),

-- Tier 3: Selective markets
-- Russia
('Moscow', 'Russia', 'Moscow', 55.7558, 37.6176, 12500000, true, 3),
('Saint Petersburg', 'Russia', 'Saint Petersburg', 59.9311, 30.3609, 5400000, false, 3),

-- Eastern Europe
('Prague', 'Czech Republic', 'Prague', 50.0755, 14.4378, 1300000, true, 3),
('Budapest', 'Hungary', 'Budapest', 47.4979, 19.0402, 1750000, true, 3),
('Warsaw', 'Poland', 'Masovian', 52.2297, 21.0122, 1790000, true, 3),
('Bucharest', 'Romania', 'Bucharest', 44.4268, 26.1025, 1880000, true, 3),

-- Turkey
('Istanbul', 'Turkey', 'Istanbul', 41.0082, 28.9784, 15500000, false, 3),
('Ankara', 'Turkey', 'Ankara', 39.9334, 32.8597, 5700000, true, 3),

-- Tier 4: Very selective (cultural constraints)
-- Iran
('Tehran', 'Iran', 'Tehran', 35.6892, 51.3890, 9000000, true, 4),
('Isfahan', 'Iran', 'Isfahan', 32.6546, 51.6680, 2200000, false, 4),

-- Cuba
('Havana', 'Cuba', 'Havana', 23.1136, -82.3666, 2100000, true, 4),
('Santiago de Cuba', 'Cuba', 'Santiago de Cuba', 20.0247, -75.8219, 430000, false, 4),

-- UAE
('Dubai', 'United Arab Emirates', 'Dubai', 25.2048, 55.2708, 3400000, false, 4),
('Abu Dhabi', 'United Arab Emirates', 'Abu Dhabi', 24.4539, 54.3773, 1500000, true, 4);

-- Create indexes after data insertion for better performance
REINDEX TABLE cities;
REINDEX TABLE specialties;
REINDEX TABLE user_types;