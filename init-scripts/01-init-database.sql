-- Create database and user (if not exists)
DO $$
BEGIN
    -- Create user if not exists
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'portfolio_user') THEN
        CREATE USER portfolio_user WITH PASSWORD 'portfolio_password';
    END IF;

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO portfolio_user;
    GRANT ALL ON SCHEMA public TO portfolio_user;
    GRANT ALL ON ALL TABLES IN SCHEMA public TO portfolio_user;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO portfolio_user;

    -- Set default privileges for future tables
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO portfolio_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO portfolio_user;
END
$$;