-- Migration: Add tx_signature and additional fields to hybrid_signals table
-- Run this if you have an existing database

-- Add new columns if they don't exist
DO $$ 
BEGIN
    -- Add sentiment_score if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='hybrid_signals' AND column_name='sentiment_score') THEN
        ALTER TABLE hybrid_signals ADD COLUMN sentiment_score DECIMAL(10, 8);
    END IF;

    -- Add technical_score if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='hybrid_signals' AND column_name='technical_score') THEN
        ALTER TABLE hybrid_signals ADD COLUMN technical_score DECIMAL(10, 8);
    END IF;

    -- Add tx_signature if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='hybrid_signals' AND column_name='tx_signature') THEN
        ALTER TABLE hybrid_signals ADD COLUMN tx_signature VARCHAR(128);
    END IF;
END $$;

-- Add index for tx_signature if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_signals_tx_signature ON hybrid_signals(tx_signature);

-- Update existing records to have NULL for new fields (they will be populated as new signals are generated)

