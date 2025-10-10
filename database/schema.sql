-- AI Sentiment Market Prediction Database Schema
-- PostgreSQL Database Schema for Dissertation Project

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if not exists (run this separately)
-- CREATE DATABASE sentiment_prediction;

-- News Articles Table
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    source VARCHAR(255) NOT NULL,
    url TEXT UNIQUE,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sentiment Analysis Results Table
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES news_articles(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')),
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    model VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trading Signals Table
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('BUY', 'SELL', 'HOLD')),
    strength DECIMAL(5,4) NOT NULL CHECK (strength >= 0 AND strength <= 1),
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    reasoning TEXT,
    sentiment_score DECIMAL(8,4),
    price_target DECIMAL(12,4),
    stop_loss DECIMAL(12,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Market Data Table
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(12,4) NOT NULL,
    volume BIGINT,
    high DECIMAL(12,4),
    low DECIMAL(12,4),
    open DECIMAL(12,4),
    close DECIMAL(12,4),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Metrics Table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    total_signals INTEGER NOT NULL DEFAULT 0,
    correct_signals INTEGER NOT NULL DEFAULT 0,
    accuracy DECIMAL(5,4) NOT NULL DEFAULT 0,
    total_return DECIMAL(10,4) NOT NULL DEFAULT 0,
    sharpe_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    win_rate DECIMAL(5,4),
    average_return DECIMAL(10,4),
    volatility DECIMAL(8,4),
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Subscriptions Table (for Telegram notifications)
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    subscribed_symbols TEXT[], -- Array of symbols user wants to track
    notification_frequency VARCHAR(20) DEFAULT 'daily' CHECK (notification_frequency IN ('realtime', 'hourly', 'daily', 'weekly')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model Performance Tracking Table
CREATE TABLE IF NOT EXISTS model_performance (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    accuracy DECIMAL(5,4) NOT NULL,
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    test_date TIMESTAMP WITH TIME ZONE NOT NULL,
    dataset_size INTEGER,
    training_time_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_source ON news_articles(source);
CREATE INDEX IF NOT EXISTS idx_news_articles_created_at ON news_articles(created_at);

CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_article_id ON sentiment_analysis(article_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_sentiment ON sentiment_analysis(sentiment);
CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_created_at ON sentiment_analysis(created_at);
CREATE INDEX IF NOT EXISTS idx_sentiment_analysis_model ON sentiment_analysis(model);

CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_signals_action ON trading_signals(action);
CREATE INDEX IF NOT EXISTS idx_trading_signals_created_at ON trading_signals(created_at);
CREATE INDEX IF NOT EXISTS idx_trading_signals_expires_at ON trading_signals(expires_at);

CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_symbol ON performance_metrics(symbol);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_created_at ON performance_metrics(created_at);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_telegram_id ON user_subscriptions(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_active ON user_subscriptions(is_active);

CREATE INDEX IF NOT EXISTS idx_model_performance_model ON model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_model_performance_test_date ON model_performance(test_date);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_news_articles_title_gin ON news_articles USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_news_articles_content_gin ON news_articles USING gin(to_tsvector('english', content));

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_news_articles_updated_at 
    BEFORE UPDATE ON news_articles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at 
    BEFORE UPDATE ON user_subscriptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW recent_signals AS
SELECT 
    ts.*,
    sa.sentiment,
    sa.confidence as sentiment_confidence,
    na.title as news_title,
    na.source as news_source
FROM trading_signals ts
LEFT JOIN sentiment_analysis sa ON ts.id = sa.id
LEFT JOIN news_articles na ON sa.article_id = na.id
WHERE ts.created_at >= NOW() - INTERVAL '7 days'
ORDER BY ts.created_at DESC;

CREATE OR REPLACE VIEW sentiment_summary AS
SELECT 
    DATE(created_at) as date,
    sentiment,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM sentiment_analysis
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at), sentiment
ORDER BY date DESC, sentiment;

CREATE OR REPLACE VIEW signal_performance AS
SELECT 
    symbol,
    action,
    COUNT(*) as total_signals,
    AVG(confidence) as avg_confidence,
    AVG(strength) as avg_strength
FROM trading_signals
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY symbol, action
ORDER BY symbol, action;

-- Sample data insertion (for testing)
INSERT INTO news_articles (title, content, source, url, published_at) VALUES
('Bitcoin Reaches New All-Time High', 'Bitcoin has reached a new all-time high of $100,000, driven by institutional adoption and positive market sentiment.', 'CoinDesk', 'https://coindesk.com/bitcoin-ath', NOW() - INTERVAL '1 hour'),
('Tesla Stock Surges on Strong Q4 Earnings', 'Tesla reported better-than-expected earnings, leading to a 15% surge in stock price during after-hours trading.', 'Reuters', 'https://reuters.com/tesla-earnings', NOW() - INTERVAL '2 hours'),
('Federal Reserve Hints at Interest Rate Cuts', 'The Federal Reserve signaled potential interest rate cuts in the coming months, boosting market optimism.', 'Bloomberg', 'https://bloomberg.com/fed-rate-cuts', NOW() - INTERVAL '3 hours')
ON CONFLICT (url) DO NOTHING;
