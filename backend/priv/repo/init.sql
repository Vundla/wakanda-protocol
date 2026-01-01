-- Initialize wakanda_DB database with national_Unity schema owner
-- All tables and objects will be in the public schema

-- Create national_Unity user if it doesn't exist
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'national_Unity') THEN
      CREATE ROLE "national_Unity" WITH LOGIN PASSWORD 'northeastMv@10111';
   END IF;
END
$$;

-- Grant all privileges to national_Unity user on public schema
GRANT ALL PRIVILEGES ON SCHEMA public TO "national_Unity";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "national_Unity";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "national_Unity";

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO "national_Unity";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO "national_Unity";
