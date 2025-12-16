-- ============================================================
-- ResearchAnalyst Backend - PostgreSQL Schema Migration
-- Version: 1.0
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. USERS TABLE
-- ============================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    cognito_sub TEXT UNIQUE,
    plan_tier TEXT NOT NULL DEFAULT 'trial',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_cognito_sub ON users (cognito_sub);

-- ============================================================
-- 2. COMPANIES TABLE
-- ============================================================
CREATE TABLE companies (
    id BIGSERIAL PRIMARY KEY,
    isin VARCHAR(12) NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    ticker TEXT,
    exchange TEXT,
    sector_name TEXT,
    slug TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_companies_isin ON companies (isin);
CREATE INDEX idx_companies_ticker ON companies (ticker);
CREATE INDEX idx_companies_sector_name ON companies (sector_name);
CREATE INDEX idx_companies_display_name ON companies (display_name);

-- ============================================================
-- 3. WATCHLISTS TABLE
-- ============================================================
CREATE TYPE watchlist_type AS ENUM ('NORMAL', 'SECTOR');

CREATE TABLE watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type watchlist_type NOT NULL DEFAULT 'NORMAL',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_watchlists_user_id ON watchlists (user_id);
CREATE INDEX idx_watchlists_type ON watchlists (type);

-- ============================================================
-- 4. CONCALLS TABLE
-- ============================================================
CREATE TYPE concall_status AS ENUM ('UPCOMING', 'COMPLETED');

CREATE TABLE concalls (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    concall_event_time TIMESTAMPTZ NOT NULL,
    status concall_status NOT NULL,
    recording_link TEXT,
    management_consistency TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_concalls_company_id ON concalls (company_id);
CREATE INDEX idx_concalls_status ON concalls (status);
CREATE INDEX idx_concalls_company_time ON concalls (company_id, concall_event_time DESC);

-- ============================================================
-- 5. FILES TABLE
-- ============================================================
CREATE TYPE file_type AS ENUM ('AUDIO', 'TRANSCRIPT', 'ANALYSIS');

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id BIGINT REFERENCES companies(id) ON DELETE SET NULL,
    concall_id BIGINT REFERENCES concalls(id) ON DELETE SET NULL,
    isin TEXT,
    file_type file_type NOT NULL,
    s3_bucket TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_files_s3_bucket_key ON files (s3_bucket, s3_key);
CREATE INDEX idx_files_company_id ON files (company_id);
CREATE INDEX idx_files_concall_id ON files (concall_id);
CREATE INDEX idx_files_isin ON files (isin);
CREATE INDEX idx_files_file_type ON files (file_type);

-- ============================================================
-- 6. WATCHLIST_ITEMS TABLE
-- ============================================================
CREATE TABLE watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    company_id BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    stock_name TEXT NOT NULL,
    stock_isin TEXT NOT NULL,
    position_order INT,
    last_analysis_file_id UUID REFERENCES files(id) ON DELETE SET NULL,
    last_analysis_updated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_watchlist_items_list_company 
    ON watchlist_items (watchlist_id, company_id);
CREATE INDEX idx_watchlist_items_watchlist_id ON watchlist_items (watchlist_id);
CREATE INDEX idx_watchlist_items_company_id ON watchlist_items (company_id);
CREATE INDEX idx_watchlist_items_last_analysis_updated_at 
    ON watchlist_items (last_analysis_updated_at);

-- ============================================================
-- 7. TRIGGERS FOR UPDATED_AT
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_watchlists_updated_at BEFORE UPDATE ON watchlists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_concalls_updated_at BEFORE UPDATE ON concalls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_watchlist_items_updated_at BEFORE UPDATE ON watchlist_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 8. SAMPLE DATA (Optional - for testing)
-- ============================================================

-- Insert a test user (uncomment if needed)
-- INSERT INTO users (email, cognito_sub, plan_tier) 
-- VALUES ('test@example.com', 'test-cognito-sub-123', 'trial');

-- Insert a test company (uncomment if needed)
-- INSERT INTO companies (isin, display_name, ticker, exchange, sector_name, slug)
-- VALUES ('INE123A01016', 'Tata Consultancy Services Ltd', 'TCS', 'NSE', 'IT Services', 'tcs');

-- ============================================================
-- END OF MIGRATION
-- ============================================================

