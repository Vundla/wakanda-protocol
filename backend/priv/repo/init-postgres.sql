-- Initialize PostgreSQL for Wakanda Protocol
-- Runs automatically on first container startup as superuser (postgres)

-- Create the wakanda_DB database
CREATE DATABASE wakanda_DB;

-- Create the national_Unity role with password
CREATE ROLE national_Unity WITH LOGIN PASSWORD 'northeastMv@10111';

-- Grant all privileges to national_Unity on wakanda_DB
ALTER DATABASE wakanda_DB OWNER TO national_Unity;
GRANT ALL PRIVILEGES ON DATABASE wakanda_DB TO national_Unity;

-- Set default privileges for future objects in public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO national_Unity;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO national_Unity;
