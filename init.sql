-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create spatial index function if not exists
CREATE OR REPLACE FUNCTION create_spatial_indexes() RETURNS void AS $$
BEGIN
    -- This function will be called after tables are created
    -- to ensure spatial indexes are properly set up
END;
$$ LANGUAGE plpgsql;
