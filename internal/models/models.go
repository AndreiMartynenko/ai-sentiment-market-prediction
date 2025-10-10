package models

import (
	"time"
)

// NewsArticle represents a news article with metadata
type NewsArticle struct {
	ID          int       `json:"id" db:"id"`
	Title       string    `json:"title" db:"title"`
	Content     string    `json:"content" db:"content"`
	Source      string    `json:"source" db:"source"`
	URL         string    `json:"url" db:"url"`
	PublishedAt time.Time `json:"published_at" db:"published_at"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
}

// SentimentAnalysis represents sentiment analysis results
type SentimentAnalysis struct {
	ID         int       `json:"id" db:"id"`
	ArticleID  int       `json:"article_id" db:"article_id"`
	Text       string    `json:"text" db:"text"`
	Sentiment  string    `json:"sentiment" db:"sentiment"` // POSITIVE, NEGATIVE, NEUTRAL
	Confidence float64   `json:"confidence" db:"confidence"`
	Model      string    `json:"model" db:"model"` // finbert, roberta, etc.
	CreatedAt  time.Time `json:"created_at" db:"created_at"`
}

// TradingSignal represents a generated trading signal
type TradingSignal struct {
	ID             int        `json:"id" db:"id"`
	Symbol         string     `json:"symbol" db:"symbol"`
	Action         string     `json:"action" db:"action"`     // BUY, SELL, HOLD
	Strength       float64    `json:"strength" db:"strength"` // 0.0 to 1.0
	Confidence     float64    `json:"confidence" db:"confidence"`
	Reasoning      string     `json:"reasoning" db:"reasoning"`
	SentimentScore float64    `json:"sentiment_score" db:"sentiment_score"`
	PriceTarget    *float64   `json:"price_target,omitempty" db:"price_target"`
	StopLoss       *float64   `json:"stop_loss,omitempty" db:"stop_loss"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	ExpiresAt      *time.Time `json:"expires_at,omitempty" db:"expires_at"`
}

// MarketData represents market price data
type MarketData struct {
	ID        int       `json:"id" db:"id"`
	Symbol    string    `json:"symbol" db:"symbol"`
	Price     float64   `json:"price" db:"price"`
	Volume    int64     `json:"volume" db:"volume"`
	High      float64   `json:"high" db:"high"`
	Low       float64   `json:"low" db:"low"`
	Open      float64   `json:"open" db:"open"`
	Close     float64   `json:"close" db:"close"`
	Timestamp time.Time `json:"timestamp" db:"timestamp"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// PerformanceMetrics represents backtesting performance
type PerformanceMetrics struct {
	ID             int       `json:"id" db:"id"`
	Symbol         string    `json:"symbol" db:"symbol"`
	TotalSignals   int       `json:"total_signals" db:"total_signals"`
	CorrectSignals int       `json:"correct_signals" db:"correct_signals"`
	Accuracy       float64   `json:"accuracy" db:"accuracy"`
	TotalReturn    float64   `json:"total_return" db:"total_return"`
	SharpeRatio    float64   `json:"sharpe_ratio" db:"sharpe_ratio"`
	MaxDrawdown    float64   `json:"max_drawdown" db:"max_drawdown"`
	WinRate        float64   `json:"win_rate" db:"win_rate"`
	AverageReturn  float64   `json:"average_return" db:"average_return"`
	Volatility     float64   `json:"volatility" db:"volatility"`
	StartDate      time.Time `json:"start_date" db:"start_date"`
	EndDate        time.Time `json:"end_date" db:"end_date"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
}

// API Request/Response models

// AnalyzeTextRequest represents a request to analyze text sentiment
type AnalyzeTextRequest struct {
	Text  string `json:"text" binding:"required"`
	Model string `json:"model,omitempty"` // Optional model selection
}

// AnalyzeTextResponse represents the response from sentiment analysis
type AnalyzeTextResponse struct {
	Sentiment  string  `json:"sentiment"`
	Confidence float64 `json:"confidence"`
	Model      string  `json:"model"`
	Text       string  `json:"text"`
}

// GenerateSignalsRequest represents a request to generate trading signals
type GenerateSignalsRequest struct {
	Symbols   []string `json:"symbols" binding:"required"`
	Timeframe string   `json:"timeframe,omitempty"` // 1h, 4h, 1d, etc.
	Lookback  int      `json:"lookback,omitempty"`  // Days to look back
}

// SignalResponse represents a trading signal response
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

// NewsRequest represents a request to fetch news
type NewsRequest struct {
	Query    string `json:"query,omitempty"`
	Sources  string `json:"sources,omitempty"`
	From     string `json:"from,omitempty"`
	To       string `json:"to,omitempty"`
	SortBy   string `json:"sort_by,omitempty"`
	PageSize int    `json:"page_size,omitempty"`
	Page     int    `json:"page,omitempty"`
}

// NewsResponse represents news articles response
type NewsResponse struct {
	Articles []NewsArticle `json:"articles"`
	Total    int           `json:"total"`
	Page     int           `json:"page"`
	PageSize int           `json:"page_size"`
}

// PerformanceResponse represents performance metrics response
type PerformanceResponse struct {
	Metrics   PerformanceMetrics `json:"metrics"`
	Signals   []SignalResponse   `json:"recent_signals"`
	ChartData []ChartDataPoint   `json:"chart_data,omitempty"`
}

// ChartDataPoint represents a data point for performance charts
type ChartDataPoint struct {
	Date   time.Time `json:"date"`
	Value  float64   `json:"value"`
	Signal string    `json:"signal,omitempty"`
}
