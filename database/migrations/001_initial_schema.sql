-- AI-Assisted Options Trading Platform
-- Initial Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    discord_user_id VARCHAR(255) UNIQUE,
    trading_mode VARCHAR(20) DEFAULT 'paper' CHECK (trading_mode IN ('paper', 'live')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User configuration table
CREATE TABLE user_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Position sizing
    max_position_size_pct DECIMAL(5,2) DEFAULT 10.00 CHECK (max_position_size_pct > 0 AND max_position_size_pct <= 100),
    max_daily_trades INTEGER DEFAULT 20 CHECK (max_daily_trades > 0),
    
    -- Risk parameters
    default_profit_target_pct DECIMAL(5,2) DEFAULT 50.00,
    default_stop_loss_pct DECIMAL(5,2) DEFAULT 50.00,
    max_portfolio_delta DECIMAL(10,2) DEFAULT 100.00,
    max_portfolio_gamma DECIMAL(10,2) DEFAULT 50.00,
    max_portfolio_vega DECIMAL(10,2) DEFAULT 500.00,
    max_concentration_pct DECIMAL(5,2) DEFAULT 25.00,
    
    -- Liquidity requirements
    min_option_volume INTEGER DEFAULT 100,
    min_open_interest INTEGER DEFAULT 500,
    max_bid_ask_spread_pct DECIMAL(5,2) DEFAULT 5.00,
    min_liquidity_score DECIMAL(3,2) DEFAULT 0.60,
    
    -- Strategy preferences
    allowed_strategies JSONB DEFAULT '["credit_spread", "debit_spread", "iron_condor", "covered_call"]'::jsonb,
    allowed_expirations JSONB DEFAULT '["weekly", "monthly"]'::jsonb,
    
    -- Feature flags
    auto_sell_enabled BOOLEAN DEFAULT true,
    trailing_stop_enabled BOOLEAN DEFAULT false,
    news_sentiment_enabled BOOLEAN DEFAULT true,
    discord_notifications_enabled BOOLEAN DEFAULT true,
    web_notifications_enabled BOOLEAN DEFAULT true,
    
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, version)
);

-- Watchlist table
CREATE TABLE watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, symbol)
);

-- Trade signals table
CREATE TABLE trade_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Signal details
    symbol VARCHAR(10) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    signal_type VARCHAR(20) NOT NULL CHECK (signal_type IN ('buy', 'sell')),
    
    -- Option details
    option_symbol VARCHAR(50) NOT NULL,
    strike_price DECIMAL(10,2) NOT NULL,
    expiration_date DATE NOT NULL,
    option_type VARCHAR(4) NOT NULL CHECK (option_type IN ('call', 'put')),
    
    -- Pricing
    quantity INTEGER NOT NULL,
    limit_price DECIMAL(10,2),
    max_spread_pct DECIMAL(5,2),
    
    -- Fallback strikes
    fallback_strikes JSONB,
    
    -- AI reasoning
    confidence_score DECIMAL(5,2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    reasoning TEXT,
    market_conditions JSONB,
    
    -- State management
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'rejected', 'expired', 'executing', 'executed', 'failed')),
    confirmation_source VARCHAR(20) CHECK (confirmation_source IN ('discord', 'web', 'auto')),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    confirmed_by UUID REFERENCES users(id),
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Executions table
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id UUID NOT NULL REFERENCES trade_signals(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Order details
    broker_order_id VARCHAR(255),
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('market', 'limit', 'stop', 'stop_limit')),
    side VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell')),
    
    -- Execution details
    filled_quantity INTEGER NOT NULL,
    filled_price DECIMAL(10,2) NOT NULL,
    commission DECIMAL(10,2) DEFAULT 0.00,
    fees DECIMAL(10,2) DEFAULT 0.00,
    
    -- Timing
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    filled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Quality metrics
    slippage_pct DECIMAL(5,2),
    execution_quality_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Positions table
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    signal_id UUID REFERENCES trade_signals(id),
    execution_id UUID REFERENCES executions(id),
    
    -- Position details
    symbol VARCHAR(10) NOT NULL,
    option_symbol VARCHAR(50) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    
    -- Option details
    strike_price DECIMAL(10,2) NOT NULL,
    expiration_date DATE NOT NULL,
    option_type VARCHAR(4) NOT NULL CHECK (option_type IN ('call', 'put')),
    
    -- Position sizing
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    
    -- P&L
    unrealized_pnl DECIMAL(10,2) DEFAULT 0.00,
    unrealized_pnl_pct DECIMAL(5,2) DEFAULT 0.00,
    realized_pnl DECIMAL(10,2),
    realized_pnl_pct DECIMAL(5,2),
    
    -- Greeks
    delta DECIMAL(10,4),
    gamma DECIMAL(10,4),
    theta DECIMAL(10,4),
    vega DECIMAL(10,4),
    iv DECIMAL(5,2),
    
    -- Exit parameters
    profit_target_pct DECIMAL(5,2) NOT NULL,
    stop_loss_pct DECIMAL(5,2) NOT NULL,
    trailing_stop_pct DECIMAL(5,2),
    
    -- State
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed', 'expired')),
    close_reason VARCHAR(50) CHECK (close_reason IN ('profit_target', 'stop_loss', 'manual', 'expiration', 'auto_exit')),
    
    -- Timing
    opened_at TIMESTAMP WITH TIME ZONE NOT NULL,
    closed_at TIMESTAMP WITH TIME ZONE,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Position history (for tracking updates)
CREATE TABLE position_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id UUID NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
    
    -- Snapshot data
    current_price DECIMAL(10,2) NOT NULL,
    unrealized_pnl DECIMAL(10,2) NOT NULL,
    unrealized_pnl_pct DECIMAL(5,2) NOT NULL,
    
    -- Greeks snapshot
    delta DECIMAL(10,4),
    gamma DECIMAL(10,4),
    theta DECIMAL(10,4),
    vega DECIMAL(10,4),
    iv DECIMAL(5,2),
    
    snapshot_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Market data cache
CREATE TABLE market_data_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    
    -- Data
    data JSONB NOT NULL,
    
    -- Metadata
    source VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol, data_type)
);

-- News sentiment cache
CREATE TABLE news_sentiment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    
    -- News details
    headline TEXT NOT NULL,
    source VARCHAR(255),
    url TEXT,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Sentiment analysis
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    sentiment_label VARCHAR(20) CHECK (sentiment_label IN ('very_negative', 'negative', 'neutral', 'positive', 'very_positive')),
    impact_level VARCHAR(20) CHECK (impact_level IN ('low', 'medium', 'high')),
    news_category VARCHAR(50),
    
    -- Processing
    processed BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol, url)
);

-- Analytics and performance tracking
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Time period
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'yearly', 'all_time')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Performance metrics
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    
    -- P&L metrics
    total_pnl DECIMAL(10,2) DEFAULT 0.00,
    total_pnl_pct DECIMAL(5,2) DEFAULT 0.00,
    avg_win DECIMAL(10,2),
    avg_loss DECIMAL(10,2),
    profit_factor DECIMAL(5,2),
    
    -- Risk metrics
    max_drawdown DECIMAL(5,2),
    max_drawdown_date DATE,
    sharpe_ratio DECIMAL(5,2),
    sortino_ratio DECIMAL(5,2),
    
    -- Strategy breakdown
    strategy_performance JSONB,
    
    -- Greeks exposure
    avg_delta DECIMAL(10,2),
    avg_gamma DECIMAL(10,2),
    avg_vega DECIMAL(10,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, period_type, period_start)
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Action details
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    
    -- Changes
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    source VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System configuration
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_sensitive BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_trade_signals_user_status ON trade_signals(user_id, status);
CREATE INDEX idx_trade_signals_expires_at ON trade_signals(expires_at) WHERE status = 'pending';
CREATE INDEX idx_positions_user_status ON positions(user_id, status);
CREATE INDEX idx_positions_symbol ON positions(symbol) WHERE status = 'open';
CREATE INDEX idx_position_history_position_id ON position_history(position_id, snapshot_at DESC);
CREATE INDEX idx_market_data_cache_symbol ON market_data_cache(symbol, data_type);
CREATE INDEX idx_news_sentiment_symbol ON news_sentiment(symbol, published_at DESC);
CREATE INDEX idx_audit_log_user_created ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_executions_signal_id ON executions(signal_id);
CREATE INDEX idx_watchlists_user_active ON watchlists(user_id, is_active);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_configs_updated_at BEFORE UPDATE ON user_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_watchlists_updated_at BEFORE UPDATE ON watchlists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trade_signals_updated_at BEFORE UPDATE ON trade_signals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default system configuration
INSERT INTO system_config (key, value, description) VALUES
    ('signal_generation_interval', '300', 'Interval in seconds between signal generation runs'),
    ('signal_expiration_time', '300', 'Time in seconds before a signal expires'),
    ('position_update_interval', '3', 'Interval in seconds for position updates'),
    ('max_concurrent_signals', '10', 'Maximum number of concurrent pending signals'),
    ('trading_hours_start', '"09:30"', 'Market open time (ET)'),
    ('trading_hours_end', '"16:00"', 'Market close time (ET)'),
    ('maintenance_mode', 'false', 'System maintenance mode flag');

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts and authentication';
COMMENT ON TABLE user_configs IS 'User-specific trading configuration and risk parameters';
COMMENT ON TABLE trade_signals IS 'AI-generated trade signals awaiting confirmation';
COMMENT ON TABLE executions IS 'Order execution records';
COMMENT ON TABLE positions IS 'Open and closed trading positions';
COMMENT ON TABLE position_history IS 'Historical snapshots of position values';
COMMENT ON TABLE market_data_cache IS 'Cached market data to reduce API calls';
COMMENT ON TABLE news_sentiment IS 'News articles with sentiment analysis';
COMMENT ON TABLE performance_metrics IS 'Aggregated performance metrics by time period';
COMMENT ON TABLE audit_log IS 'Audit trail of all system actions';
COMMENT ON TABLE system_config IS 'System-wide configuration parameters';
