-- PostgreSQL Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create database (already created by POSTGRES_DB environment variable)
-- CREATE DATABASE position_tracker;

-- Connect to the database
\c position_tracker;

-- Create enum types
CREATE TYPE lot_status AS ENUM ('OPEN', 'PARTIAL', 'CLOSED');

-- Create tax_lots table
CREATE TABLE tax_lots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    security_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    open_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    close_date TIMESTAMP WITH TIME ZONE,
    open_qty NUMERIC(19,4) NOT NULL,
    close_qty NUMERIC(19,4) NOT NULL DEFAULT 0,
    remaining_qty NUMERIC(19,4) NOT NULL,
    open_price NUMERIC(19,4) NOT NULL,
    close_price NUMERIC(19,4),
    charges NUMERIC(19,4) NOT NULL DEFAULT 0,
    realized_pnl NUMERIC(19,4) NOT NULL DEFAULT 0,
    stcg NUMERIC(19,4) NOT NULL DEFAULT 0,
    ltcg NUMERIC(19,4) NOT NULL DEFAULT 0,
    status lot_status NOT NULL DEFAULT 'OPEN',
    
    -- Constraints
    CONSTRAINT check_open_qty_positive CHECK (open_qty > 0),
    CONSTRAINT check_close_qty_non_negative CHECK (close_qty >= 0),
    CONSTRAINT check_remaining_qty_non_negative CHECK (remaining_qty >= 0),
    CONSTRAINT check_remaining_qty_not_exceed_open CHECK (remaining_qty <= open_qty),
    CONSTRAINT check_open_price_positive CHECK (open_price > 0),
    CONSTRAINT check_close_price_positive CHECK (close_price IS NULL OR close_price > 0),
    CONSTRAINT check_charges_non_negative CHECK (charges >= 0),
    CONSTRAINT check_version_positive CHECK (version > 0)
);

-- Create security_prices table
CREATE TABLE security_prices (
    security_id INTEGER PRIMARY KEY,
    price NUMERIC(19,4) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_price_positive CHECK (price > 0)
);

-- Create portfolio_summary table (deprecated but kept for compatibility)
CREATE TABLE portfolio_summary (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    security_id INTEGER NOT NULL,
    quantity NUMERIC(19,4) NOT NULL DEFAULT 0,
    avg_cost_basis NUMERIC(19,4) NOT NULL DEFAULT 0,
    current_price NUMERIC(19,4) NOT NULL DEFAULT 0,
    unrealized_pnl NUMERIC(19,4) NOT NULL DEFAULT 0,
    realized_pnl_ytd NUMERIC(19,4) NOT NULL DEFAULT 0,
    stcg_ytd NUMERIC(19,4) NOT NULL DEFAULT 0,
    ltcg_ytd NUMERIC(19,4) NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_quantity_non_negative CHECK (quantity >= 0),
    CONSTRAINT check_avg_cost_basis_non_negative CHECK (avg_cost_basis >= 0),
    CONSTRAINT check_current_price_non_negative CHECK (current_price >= 0),
    CONSTRAINT check_stcg_ytd_non_negative CHECK (stcg_ytd >= 0),
    CONSTRAINT check_ltcg_ytd_non_negative CHECK (ltcg_ytd >= 0),
    CONSTRAINT unique_user_security UNIQUE (user_id, security_id)
);

-- Create indexes for tax_lots
CREATE INDEX idx_tax_lots_user_id ON tax_lots(user_id);
CREATE INDEX idx_tax_lots_security_id ON tax_lots(security_id);
CREATE INDEX idx_user_security_status ON tax_lots(user_id, security_id, status);
CREATE INDEX idx_user_security_date ON tax_lots(user_id, security_id, open_date);
CREATE INDEX idx_security_status_date ON tax_lots(security_id, status, open_date);
CREATE INDEX idx_user_date ON tax_lots(user_id, open_date);
CREATE INDEX idx_close_date ON tax_lots(close_date);

-- Create indexes for security_prices
CREATE INDEX idx_updated_at ON security_prices(updated_at);

-- Create indexes for portfolio_summary
CREATE INDEX idx_portfolio_user_id ON portfolio_summary(user_id);
CREATE INDEX idx_portfolio_security_id ON portfolio_summary(security_id);
CREATE INDEX idx_user_security ON portfolio_summary(user_id, security_id);
CREATE INDEX idx_user_last_updated ON portfolio_summary(user_id, last_updated);
CREATE INDEX idx_last_updated ON portfolio_summary(last_updated);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tracker_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tracker_user;

-- Insert some sample data for testing
INSERT INTO security_prices (security_id, price) VALUES 
(1, 150.0),
(2, 200.0),
(501, 175.0),
(502, 220.0);

-- Log completion
\echo 'Database initialization completed successfully!'
