-- AI-Driven Sentiment Market Prediction System
-- PostgreSQL Database Schema

-- Create database (run separately if needed)
-- CREATE DATABASE sentiment_market;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: news_raw
-- Stores raw news articles from various sources
CREATE TABLE IF NOT EXISTS news_raw (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    text TEXT,
    source VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_news_symbol (symbol),
    INDEX idx_news_timestamp (timestamp),
    INDEX idx_news_created (created_at)
);

-- Table: market_data
-- Stores OHLCV market data
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicates
    UNIQUE(symbol, timestamp),
    
    -- Indexes
    INDEX idx_market_symbol (symbol),
    INDEX idx_market_timestamp (timestamp),
    INDEX idx_market_symbol_timestamp (symbol, timestamp)
);

-- Table: sentiment_results
-- Stores sentiment analysis results from FinBERT
CREATE TABLE IF NOT EXISTS sentiment_results (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    sentiment_score DECIMAL(10, 8) NOT NULL CHECK (sentiment_score >= 0 AND sentiment_score <= 1),
    label VARCHAR(20) NOT NULL CHECK (label IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')),
    confidence DECIMAL(5, 4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_sentiment_symbol (symbol),
    INDEX idx_sentiment_label (label),
    INDEX idx_sentiment_timestamp (timestamp)
);

-- Table: technical_indicators
-- Stores technical indicator calculations
CREATE TABLE IF NOT EXISTS technical_indicators (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    ema20 DECIMAL(20, 8),
    ema50 DECIMAL(20, 8),
    rsi DECIMAL(10, 4) CHECK (rsi >= 0 AND rsi <= 100),
    macd DECIMAL(20, 8),
    technical_score DECIMAL(10, 8) NOT NULL CHECK (technical_score >= 0 AND technical_score <= 1),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(symbol, timestamp),
    
    -- Indexes
    INDEX idx_technical_symbol (symbol),
    INDEX idx_technical_timestamp (timestamp)
);

-- Table: hybrid_signals
-- Stores final trading signals from hybrid decision engine
CREATE TABLE IF NOT EXISTS hybrid_signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    signal VARCHAR(10) NOT NULL CHECK (signal IN ('BUY', 'SELL', 'HOLD')),
    hybrid_score DECIMAL(10, 8) NOT NULL CHECK (hybrid_score >= 0 AND hybrid_score <= 1),
    confidence DECIMAL(5, 4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    reason TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_signals_symbol (symbol),
    INDEX idx_signals_signal (signal),
    INDEX idx_signals_timestamp (timestamp),
    INDEX idx_signals_created (created_at)
);

-- View: latest_signals
-- Get the most recent signal for each symbol
CREATE OR REPLACE VIEW latest_signals AS
SELECT DISTINCT ON (symbol)
    id, symbol, signal, hybrid_score, confidence, reason, timestamp, created_at
FROM hybrid_signals
ORDER BY symbol, timestamp DESC;

-- View: sentiment_summary
-- Aggregate sentiment analysis by symbol
CREATE OR REPLACE VIEW sentiment_summary AS
SELECT 
    symbol,
    AVG(sentiment_score) as avg_sentiment_score,
    COUNT(*) as total_analyses,
    COUNT(CASE WHEN label = 'POSITIVE' THEN 1 END) as positive_count,
    COUNT(CASE WHEN label = 'NEGATIVE' THEN 1 END) as negative_count,
    COUNT(CASE WHEN label = 'NEUTRAL' THEN 1 END) as neutral_count,
    MAX(timestamp) as last_updated
FROM sentiment_results
GROUP BY symbol;

-- View: technical_summary
-- Aggregate technical indicators by symbol
CREATE OR REPLACE VIEW technical_summary AS
SELECT 
    symbol,
    AVG(technical_score) as avg_technical_score,
    AVG(ema20) as avg_ema20,
    AVG(ema50) as avg_ema50,
    AVG(rsi) as avg_rsi,
    AVG(macd) as avg_macd,
    COUNT(*) as total_analyses,
    MAX(timestamp) as last_updated
FROM technical_indicators
GROUP BY symbol;

-- View: hybrid_summary
-- Aggregate hybrid signals by symbol
CREATE OR REPLACE VIEW hybrid_summary AS
SELECT 
    symbol,
    AVG(hybrid_score) as avg_hybrid_score,
    AVG(confidence) as avg_confidence,
    COUNT(*) as total_signals,
    COUNT(CASE WHEN signal = 'BUY' THEN 1 END) as buy_count,
    COUNT(CASE WHEN signal = 'SELL' THEN 1 END) as sell_count,
    COUNT(CASE WHEN signal = 'HOLD' THEN 1 END) as hold_count,
    MAX(timestamp) as last_updated
FROM hybrid_signals
GROUP BY symbol;

-- Function: clean_old_data
-- Remove data older than specified days
CREATE OR REPLACE FUNCTION clean_old_data(days_to_keep INTEGER DEFAULT 90)
RETURNS TABLE(deleted_news INTEGER, deleted_market INTEGER, deleted_sentiment INTEGER, deleted_technical INTEGER, deleted_signals INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    news_count INTEGER;
    market_count INTEGER;
    sentiment_count INTEGER;
    technical_count INTEGER;
    signals_count INTEGER;
BEGIN
    -- Delete old news
    DELETE FROM news_raw WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS news_count = ROW_COUNT;
    
    -- Delete old market data
    DELETE FROM market_data WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS market_count = ROW_COUNT;
    
    -- Delete old sentiment results
    DELETE FROM sentiment_results WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS sentiment_count = ROW_COUNT;
    
    -- Delete old technical indicators
    DELETE FROM technical_indicators WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS technical_count = ROW_COUNT;
    
    -- Delete old signals
    DELETE FROM hybrid_signals WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    GET DIAGNOSTICS signals_count = ROW_COUNT;
    
    RETURN QUERY SELECT news_count, market_count, sentiment_count, technical_count, signals_count;
END;
$$;

-- Sample seed data
INSERT INTO market_data (symbol, open, high, low, close, volume, timestamp) VALUES
('BTCUSDT', 95000.00, 97000.00, 94000.00, 96500.00, 123456789.00, NOW() - INTERVAL '1 day'),
('BTCUSDT', 96500.00, 97500.00, 95000.00, 97000.00, 125000000.00, NOW() - INTERVAL '12 hours'),
('BTCUSDT', 97000.00, 98000.00, 96500.00, 97500.00, 120000000.00, NOW())
ON CONFLICT (symbol, timestamp) DO NOTHING;

INSERT INTO news_raw (symbol, title, text, source, timestamp) VALUES
('BTCUSDT', 'Bitcoin Reaches New All-Time High', 'Bitcoin surged past $97,000 today as institutional adoption continues to grow.', 'CryptoNews', NOW() - INTERVAL '6 hours'),
('BTCUSDT', 'Major Exchange Announces Bitcoin ETF', 'A leading crypto exchange announced plans for a new Bitcoin ETF product.', 'CoinDesk', NOW() - INTERVAL '3 hours')
ON CONFLICT DO NOTHING;
