#!/bin/bash
# This script initializes PostgreSQL with the proper database and user
# It will be run automatically when the container starts

set -e

echo "🗄️  Initializing PostgreSQL..."

# Create the wakanda_DB database and user
echo "Creating database and user..."
psql -U postgres <<EOF
-- Drop old user/db if they exist with old password
DROP DATABASE IF EXISTS wakanda_DB;
DROP ROLE IF EXISTS national_Unity;

-- Create new database
CREATE DATABASE wakanda_DB;

-- Create new user with correct password
CREATE ROLE national_Unity WITH LOGIN PASSWORD 'northeastMv@10111';

-- Grant all privileges
ALTER DATABASE wakanda_DB OWNER TO national_Unity;
GRANT ALL PRIVILEGES ON DATABASE wakanda_DB TO national_Unity;
GRANT ALL PRIVILEGES ON SCHEMA public TO national_Unity;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO national_Unity;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO national_Unity;

echo "✅ Database and user created"
EOF
