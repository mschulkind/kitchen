-- Supabase Foundation SQL 🏗️
-- Sets up roles and schemas for self-hosted Supabase stack.

-- =============================================================================
-- Schemas
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS _realtime;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS extensions;

-- =============================================================================
-- Roles
-- =============================================================================

-- We use the same password for all internal roles for simplicity in this self-hosted setup.
-- In production, these should be distinct and managed securely.

DO $$
BEGIN
    -- Supabase Admin (Superuser-like)
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'supabase_admin') THEN
        CREATE ROLE supabase_admin WITH LOGIN SUPERUSER PASSWORD 'postgres';
    END IF;

    -- Auth Admin
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'supabase_auth_admin') THEN
        CREATE ROLE supabase_auth_admin WITH LOGIN CREATEROLE PASSWORD 'postgres';
    END IF;

    -- Storage Admin
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'supabase_storage_admin') THEN
        CREATE ROLE supabase_storage_admin WITH LOGIN PASSWORD 'postgres';
    END IF;

    -- Authenticator (Proxy for PostgREST)
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'authenticator') THEN
        CREATE ROLE authenticator WITH LOGIN NOINHERIT PASSWORD 'postgres';
    END IF;

    -- App Roles
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'anon') THEN
        CREATE ROLE anon NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'authenticated') THEN
        CREATE ROLE authenticated NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'service_role') THEN
        CREATE ROLE service_role NOLOGIN;
    END IF;

    -- Permissions
    GRANT ALL ON DATABASE postgres TO supabase_admin;
    GRANT ALL ON DATABASE postgres TO supabase_auth_admin;
    GRANT ALL ON DATABASE postgres TO supabase_storage_admin;

    GRANT anon, authenticated, service_role TO authenticator;
    
    GRANT ALL ON SCHEMA auth TO supabase_auth_admin;
    GRANT ALL ON SCHEMA _realtime TO supabase_admin;
    GRANT ALL ON SCHEMA storage TO supabase_storage_admin;
    
END $$;

-- Enable UUID extension in the right place
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA extensions;
ALTER USER supabase_admin SET search_path TO _realtime, public, extensions;
ALTER USER supabase_auth_admin SET search_path TO auth, public, extensions;

-- =============================================================================
-- Auth Helpers
-- =============================================================================

CREATE OR REPLACE FUNCTION auth.uid() 
RETURNS uuid 
LANGUAGE sql STABLE
AS $$
  SELECT COALESCE(
    current_setting('request.jwt.claim.sub', true),
    (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
  )::uuid
$$;

CREATE OR REPLACE FUNCTION auth.role() 
RETURNS text 
LANGUAGE sql STABLE
AS $$
  SELECT COALESCE(
    current_setting('request.jwt.claim.role', true),
    (current_setting('request.jwt.claims', true)::jsonb ->> 'role')
  )::text
$$;

ALTER FUNCTION auth.uid() OWNER TO supabase_auth_admin;
ALTER FUNCTION auth.role() OWNER TO supabase_auth_admin;
