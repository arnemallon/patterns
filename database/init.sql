-- Bitcoin Classifier Production Database Initialization
-- This script runs when the PostgreSQL container starts for the first time

-- Create the production database if it doesn't exist
-- (This is handled by the POSTGRES_DB environment variable)

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance
-- (These will be created after the tables are created by the application)

-- Log the initialization
DO $$
BEGIN
    RAISE NOTICE 'Bitcoin Classifier production database initialized successfully';
END $$;












