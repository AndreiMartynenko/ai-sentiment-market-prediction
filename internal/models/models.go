package models

import "time"

// Signal represents a trading signal with hybrid decision
type Signal struct {
	ID          int       `json:"id" db:"id"`
	Symbol      string    `json:"symbol" db:"symbol"`
	Signal      string    `json:"signal" db:"signal"` // BUY, SELL, HOLD
	HybridScore float64   `json:"hybrid_score" db:"hybrid_score"`
	Confidence  float64   `json:"confidence" db:"confidence"`
	Reason      string    `json:"reason" db:"reason"`
	Timestamp   time.Time `json:"timestamp" db:"timestamp"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

// Sentiment represents sentiment analysis results
type Sentiment struct {
	ID             int       `json:"id" db:"id"`
	Symbol         string    `json:"symbol" db:"symbol"`
	SentimentScore float64   `json:"sentiment_score" db:"sentiment_score"`
	Label          string    `json:"label" db:"label"` // POSITIVE, NEGATIVE, NEUTRAL
	Confidence     float64   `json:"confidence" db:"confidence"`
	Timestamp      time.Time `json:"timestamp" db:"timestamp"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
}

// Technical represents technical indicator calculations
type Technical struct {
	ID             int       `json:"id" db:"id"`
	Symbol         string    `json:"symbol" db:"symbol"`
	EMA20          float64   `json:"ema20" db:"ema20"`
	EMA50          float64   `json:"ema50" db:"ema50"`
	RSI            float64   `json:"rsi" db:"rsi"`
	MACD           float64   `json:"macd" db:"macd"`
	TechnicalScore float64   `json:"technical_score" db:"technical_score"`
	Timestamp      time.Time `json:"timestamp" db:"timestamp"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
}

// NewsRaw represents raw news articles
type NewsRaw struct {
	ID        int       `json:"id" db:"id"`
	Symbol    string    `json:"symbol" db:"symbol"`
	Title     string    `json:"title" db:"title"`
	Text      string    `json:"text" db:"text"`
	Source    string    `json:"source" db:"source"`
	Timestamp time.Time `json:"timestamp" db:"timestamp"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// MarketData represents OHLCV market data
type MarketData struct {
	ID        int       `json:"id" db:"id"`
	Symbol    string    `json:"symbol" db:"symbol"`
	Open      float64   `json:"open" db:"open"`
	High      float64   `json:"high" db:"high"`
	Low       float64   `json:"low" db:"low"`
	Close     float64   `json:"close" db:"close"`
	Volume    float64   `json:"volume" db:"volume"`
	Timestamp time.Time `json:"timestamp" db:"timestamp"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// APIRequest represents common API request structure
type APIRequest struct {
	Symbol string `json:"symbol" binding:"required"`
}

// HealthResponse represents health check response
type HealthResponse struct {
	Status    string `json:"status"`
	Service   string `json:"service"`
	Version   string `json:"version"`
	Database  string `json:"database"`
	MLService string `json:"ml_service"`
}

type NewsRequest struct {
	Query    string `json:"query"`
	Sources  string `json:"sources"`
	From     string `json:"from"`
	To       string `json:"to"`
	SortBy   string `json:"sortBy"`
	PageSize int    `json:"pageSize"`
	Page     int    `json:"page"`
}

type NewsArticle struct {
	Title       string    `json:"title"`
	Content     string    `json:"content"`
	Source      string    `json:"source"`
	URL         string    `json:"url"`
	PublishedAt time.Time `json:"publishedAt"`
	CreatedAt   time.Time `json:"createdAt"`
	UpdatedAt   time.Time `json:"updatedAt"`
}

type NewsResponse struct {
	Articles []NewsArticle `json:"articles"`
	Total    int           `json:"total"`
	Page     int           `json:"page"`
	PageSize int           `json:"pageSize"`
}

type AnalyzeTextRequest struct {
	Text  string `json:"text" binding:"required"`
	Model string `json:"model,omitempty"`
}

type AnalyzeTextResponse struct {
	Sentiment  string  `json:"sentiment"`
	Confidence float64 `json:"confidence"`
	Model      string  `json:"model"`
	Text       string  `json:"text"`
}

type PerformanceMetrics struct {
	Accuracy  float64 `json:"accuracy"`
	Precision float64 `json:"precision"`
	Recall    float64 `json:"recall"`
	F1        float64 `json:"f1"`
}

type GenerateSignalsRequest struct {
	Symbols   []string `json:"symbols" binding:"required"`
	Timeframe string   `json:"timeframe,omitempty"`
	Lookback  int      `json:"lookback,omitempty"`
}

type SignalResponse struct {
	Symbol         string     `json:"symbol"`
	Action         string     `json:"action"`
	Strength       float64    `json:"strength"`
	Confidence     float64    `json:"confidence"`
	Reasoning      string     `json:"reasoning"`
	SentimentScore float64    `json:"sentiment_score"`
	PriceTarget    *float64   `json:"price_target,omitempty"`
	StopLoss       *float64   `json:"stop_loss,omitempty"`
	CreatedAt      time.Time  `json:"created_at"`
	ExpiresAt      *time.Time `json:"expires_at,omitempty"`
}

type PerformanceResponse struct {
	Symbol     string  `json:"symbol"`
	From       string  `json:"from"`
	To         string  `json:"to"`
	Total      int     `json:"total"`
	Winning    int     `json:"winning"`
	Losing     int     `json:"losing"`
	WinRatePct float64 `json:"win_rate_pct"`
}
