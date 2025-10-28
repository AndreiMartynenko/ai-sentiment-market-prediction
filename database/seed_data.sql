-- Seed Data for AI-Driven Sentiment Market Prediction System
-- Optional sample data for development and testing

-- Seed market data for Bitcoin
INSERT INTO market_data (symbol, open, high, low, close, volume, timestamp) VALUES
('BTCUSDT', 45000.00, 46500.00, 44800.00, 46200.00, 1234567890.00, NOW() - INTERVAL '7 days'),
('BTCUSDT', 46200.00, 47000.00, 46000.00, 46800.00, 1250000000.00, NOW() - INTERVAL '6 days'),
('BTCUSDT', 46800.00, 47500.00, 46500.00, 47300.00, 1300000000.00, NOW() - INTERVAL '5 days'),
('BTCUSDT', 47300.00, 48000.00, 47000.00, 47800.00, 1280000000.00, NOW() - INTERVAL '4 days'),
('BTCUSDT', 47800.00, 48500.00, 47500.00, 48300.00, 1350000000.00, NOW() - INTERVAL '3 days'),
('BTCUSDT', 48300.00, 49000.00, 48000.00, 48800.00, 1400000000.00, NOW() - INTERVAL '2 days'),
('BTCUSDT', 48800.00, 49500.00, 48500.00, 49300.00, 1450000000.00, NOW() - INTERVAL '1 day'),
('BTCUSDT', 49300.00, 50000.00, 49000.00, 49800.00, 1500000000.00, NOW())
ON CONFLICT (symbol, timestamp) DO NOTHING;

-- Seed market data for Ethereum
INSERT INTO market_data (symbol, open, high, low, close, volume, timestamp) VALUES
('ETHUSDT', 3200.00, 3280.00, 3180.00, 3250.00, 567890123.00, NOW() - INTERVAL '7 days'),
('ETHUSDT', 3250.00, 3320.00, 3230.00, 3300.00, 580000000.00, NOW() - INTERVAL '6 days'),
('ETHUSDT', 3300.00, 3380.00, 3280.00, 3350.00, 590000000.00, NOW() - INTERVAL '5 days'),
('ETHUSDT', 3350.00, 3420.00, 3330.00, 3400.00, 600000000.00, NOW() - INTERVAL '4 days'),
('ETHUSDT', 3400.00, 3480.00, 3380.00, 3450.00, 610000000.00, NOW() - INTERVAL '3 days'),
('ETHUSDT', 3450.00, 3520.00, 3430.00, 3500.00, 620000000.00, NOW() - INTERVAL '2 days'),
('ETHUSDT', 3500.00, 3580.00, 3480.00, 3550.00, 630000000.00, NOW() - INTERVAL '1 day'),
('ETHUSDT', 3550.00, 3620.00, 3530.00, 3600.00, 640000000.00, NOW())
ON CONFLICT (symbol, timestamp) DO NOTHING;

-- Seed news articles
INSERT INTO news_raw (symbol, title, text, source, timestamp) VALUES
('BTCUSDT', 'Institutional Investors Increasing Bitcoin Holdings', 'Large institutional investors have significantly increased their Bitcoin holdings this quarter, driving up demand and prices.', 'CryptoNews', NOW() - INTERVAL '1 day'),
('BTCUSDT', 'Bitcoin ETF Approval Boosts Market Confidence', 'The approval of new Bitcoin ETFs has significantly boosted investor confidence in the cryptocurrency market.', 'CoinDesk', NOW() - INTERVAL '18 hours'),
('BTCUSDT', 'Regulatory Clarity Improves Bitcoin Outlook', 'Recent regulatory clarity from government agencies has improved the long-term outlook for Bitcoin investments.', 'Reuters', NOW() - INTERVAL '12 hours'),
('ETHUSDT', 'Ethereum 2.0 Upgrade Successful', 'The Ethereum network successfully completed its 2.0 upgrade, improving scalability and reducing energy consumption.', 'CoinTelegraph', NOW() - INTERVAL '1 day'),
('ETHUSDT', 'Major DeFi Protocol Launches on Ethereum', 'A major decentralized finance protocol launched on Ethereum, attracting billions in liquidity.', 'DeFi Pulse', NOW() - INTERVAL '16 hours')
ON CONFLICT DO NOTHING;

-- Seed sentiment results
INSERT INTO sentiment_results (symbol, sentiment_score, label, confidence, timestamp) VALUES
('BTCUSDT', 0.75, 'POSITIVE', 0.92, NOW() - INTERVAL '1 day'),
('BTCUSDT', 0.82, 'POSITIVE', 0.88, NOW() - INTERVAL '18 hours'),
('BTCUSDT', 0.68, 'POSITIVE', 0.85, NOW() - INTERVAL '12 hours'),
('ETHUSDT', 0.70, 'POSITIVE', 0.90, NOW() - INTERVAL '1 day'),
('ETHUSDT', 0.78, 'POSITIVE', 0.87, NOW() - INTERVAL '16 hours')
ON CONFLICT DO NOTHING;

-- Seed technical indicators
INSERT INTO technical_indicators (symbol, ema20, ema50, rsi, macd, technical_score, timestamp) VALUES
('BTCUSDT', 48500.00, 47000.00, 65.5, 1250.50, 0.68, NOW() - INTERVAL '1 day'),
('BTCUSDT', 48800.00, 47200.00, 68.2, 1350.75, 0.72, NOW() - INTERVAL '12 hours'),
('BTCUSDT', 49200.00, 47500.00, 70.8, 1450.00, 0.75, NOW()),
('ETHUSDT', 3450.00, 3350.00, 62.3, 48.25, 0.65, NOW() - INTERVAL '1 day'),
('ETHUSDT', 3500.00, 3370.00, 64.7, 52.30, 0.68, NOW())
ON CONFLICT (symbol, timestamp) DO NOTHING;

-- Seed hybrid signals
INSERT INTO hybrid_signals (symbol, signal, hybrid_score, confidence, reason, timestamp) VALUES
('BTCUSDT', 'BUY', 0.71, 0.82, 'Strong positive sentiment with favorable technical setup suggesting bullish momentum', NOW() - INTERVAL '1 day'),
('BTCUSDT', 'BUY', 0.77, 0.85, 'Strong positive sentiment with strong technical indicators suggesting bullish momentum', NOW() - INTERVAL '12 hours'),
('ETHUSDT', 'BUY', 0.67, 0.78, 'Moderately positive sentiment with favorable technical setup suggesting bullish momentum', NOW() - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

