package api

import (
	"net/http"
	"strconv"

	"ai_sentiment-market-prediction/internal/db"
	"ai_sentiment-market-prediction/internal/models"

	"github.com/gin-gonic/gin"
)

// HealthCheck verifies the health of the API and database
func HealthCheck(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		if database == nil || database.DB == nil {
			c.JSON(http.StatusOK, models.HealthResponse{
				Status:    "healthy",
				Service:   "AI Sentiment Market Prediction API",
				Version:   "1.0.0",
				Database:  "disconnected",
				MLService: "unknown",
			})
			return
		}

		if err := database.DB.Ping(); err != nil {
			c.JSON(http.StatusServiceUnavailable, models.HealthResponse{
				Status:    "unhealthy",
				Service:   "AI Sentiment Market Prediction API",
				Version:   "1.0.0",
				Database:  "disconnected",
				MLService: "unknown",
			})
			return
		}

		c.JSON(http.StatusOK, models.HealthResponse{
			Status:    "healthy",
			Service:   "AI Sentiment Market Prediction API",
			Version:   "1.0.0",
			Database:  "connected",
			MLService: "unknown",
		})
	}
}

// GetSignals retrieves all trading signals
func GetSignals(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		limit := c.DefaultQuery("limit", "50")
		limitInt, _ := strconv.Atoi(limit)

		query := `SELECT id, symbol, signal, hybrid_score, confidence, reason, timestamp, created_at 
		          FROM hybrid_signals 
		          ORDER BY timestamp DESC 
		          LIMIT $1`

		rows, err := database.DB.Query(query, limitInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var signals []models.Signal
		for rows.Next() {
			var s models.Signal
			if err := rows.Scan(&s.ID, &s.Symbol, &s.Signal, &s.HybridScore, &s.Confidence, &s.Reason, &s.Timestamp, &s.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			signals = append(signals, s)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    signals,
			"count":   len(signals),
		})
	}
}

// GetSignalsBySymbol retrieves signals for a specific symbol
func GetSignalsBySymbol(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		symbol := c.Param("symbol")

		query := `SELECT id, symbol, signal, hybrid_score, confidence, reason, timestamp, created_at 
		          FROM hybrid_signals 
		          WHERE symbol = $1 
		          ORDER BY timestamp DESC 
		          LIMIT 100`

		rows, err := database.DB.Query(query, symbol)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var signals []models.Signal
		for rows.Next() {
			var s models.Signal
			if err := rows.Scan(&s.ID, &s.Symbol, &s.Signal, &s.HybridScore, &s.Confidence, &s.Reason, &s.Timestamp, &s.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			signals = append(signals, s)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    signals,
			"count":   len(signals),
		})
	}
}

// GenerateSignals triggers signal generation through ML service
func GenerateSignals(database *db.Connection, mlServiceURL string) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req models.APIRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// This would call the ML service to generate signals
		// For now, return a placeholder response
		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"message": "Signal generation triggered",
			"symbol":  req.Symbol,
			"note":    "Integration with ML service pending",
		})
	}
}

// GetSentiment retrieves sentiment analysis results
func GetSentiment(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		limit := c.DefaultQuery("limit", "100")
		limitInt, _ := strconv.Atoi(limit)

		query := `SELECT id, symbol, sentiment_score, label, confidence, timestamp, created_at 
		          FROM sentiment_results 
		          ORDER BY timestamp DESC 
		          LIMIT $1`

		rows, err := database.DB.Query(query, limitInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var sentiments []models.Sentiment
		for rows.Next() {
			var s models.Sentiment
			if err := rows.Scan(&s.ID, &s.Symbol, &s.SentimentScore, &s.Label, &s.Confidence, &s.Timestamp, &s.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			sentiments = append(sentiments, s)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    sentiments,
			"count":   len(sentiments),
		})
	}
}

// GetSentimentBySymbol retrieves sentiment for a specific symbol
func GetSentimentBySymbol(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		symbol := c.Param("symbol")

		query := `SELECT id, symbol, sentiment_score, label, confidence, timestamp, created_at 
		          FROM sentiment_results 
		          WHERE symbol = $1 
		          ORDER BY timestamp DESC 
		          LIMIT 100`

		rows, err := database.DB.Query(query, symbol)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var sentiments []models.Sentiment
		for rows.Next() {
			var s models.Sentiment
			if err := rows.Scan(&s.ID, &s.Symbol, &s.SentimentScore, &s.Label, &s.Confidence, &s.Timestamp, &s.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			sentiments = append(sentiments, s)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    sentiments,
			"count":   len(sentiments),
		})
	}
}

// GetTechnical retrieves technical indicator data
func GetTechnical(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		limit := c.DefaultQuery("limit", "100")
		limitInt, _ := strconv.Atoi(limit)

		query := `SELECT id, symbol, ema20, ema50, rsi, macd, technical_score, timestamp, created_at 
		          FROM technical_indicators 
		          ORDER BY timestamp DESC 
		          LIMIT $1`

		rows, err := database.DB.Query(query, limitInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var technicals []models.Technical
		for rows.Next() {
			var t models.Technical
			if err := rows.Scan(&t.ID, &t.Symbol, &t.EMA20, &t.EMA50, &t.RSI, &t.MACD, &t.TechnicalScore, &t.Timestamp, &t.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			technicals = append(technicals, t)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    technicals,
			"count":   len(technicals),
		})
	}
}

// GetTechnicalBySymbol retrieves technical indicators for a specific symbol
func GetTechnicalBySymbol(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		symbol := c.Param("symbol")

		query := `SELECT id, symbol, ema20, ema50, rsi, macd, technical_score, timestamp, created_at 
		          FROM technical_indicators 
		          WHERE symbol = $1 
		          ORDER BY timestamp DESC 
		          LIMIT 100`

		rows, err := database.DB.Query(query, symbol)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var technicals []models.Technical
		for rows.Next() {
			var t models.Technical
			if err := rows.Scan(&t.ID, &t.Symbol, &t.EMA20, &t.EMA50, &t.RSI, &t.MACD, &t.TechnicalScore, &t.Timestamp, &t.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			technicals = append(technicals, t)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    technicals,
			"count":   len(technicals),
		})
	}
}

// GetNews retrieves raw news articles
func GetNews(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		limit := c.DefaultQuery("limit", "50")
		limitInt, _ := strconv.Atoi(limit)

		query := `SELECT id, symbol, title, text, source, timestamp, created_at 
		          FROM news_raw 
		          ORDER BY timestamp DESC 
		          LIMIT $1`

		rows, err := database.DB.Query(query, limitInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var news []models.NewsRaw
		for rows.Next() {
			var n models.NewsRaw
			if err := rows.Scan(&n.ID, &n.Symbol, &n.Title, &n.Text, &n.Source, &n.Timestamp, &n.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			news = append(news, n)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    news,
			"count":   len(news),
		})
	}
}

// GetNewsBySymbol retrieves news for a specific symbol
func GetNewsBySymbol(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		symbol := c.Param("symbol")

		query := `SELECT id, symbol, title, text, source, timestamp, created_at 
		          FROM news_raw 
		          WHERE symbol = $1 
		          ORDER BY timestamp DESC 
		          LIMIT 100`

		rows, err := database.DB.Query(query, symbol)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var news []models.NewsRaw
		for rows.Next() {
			var n models.NewsRaw
			if err := rows.Scan(&n.ID, &n.Symbol, &n.Title, &n.Text, &n.Source, &n.Timestamp, &n.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			news = append(news, n)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    news,
			"count":   len(news),
		})
	}
}

// GetMarketData retrieves OHLCV market data
func GetMarketData(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		limit := c.DefaultQuery("limit", "100")
		limitInt, _ := strconv.Atoi(limit)

		query := `SELECT id, symbol, open, high, low, close, volume, timestamp, created_at 
		          FROM market_data 
		          ORDER BY timestamp DESC 
		          LIMIT $1`

		rows, err := database.DB.Query(query, limitInt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var marketData []models.MarketData
		for rows.Next() {
			var m models.MarketData
			if err := rows.Scan(&m.ID, &m.Symbol, &m.Open, &m.High, &m.Low, &m.Close, &m.Volume, &m.Timestamp, &m.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			marketData = append(marketData, m)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    marketData,
			"count":   len(marketData),
		})
	}
}

// GetMarketDataBySymbol retrieves market data for a specific symbol
func GetMarketDataBySymbol(database *db.Connection) gin.HandlerFunc {
	return func(c *gin.Context) {
		symbol := c.Param("symbol")

		query := `SELECT id, symbol, open, high, low, close, volume, timestamp, created_at 
		          FROM market_data 
		          WHERE symbol = $1 
		          ORDER BY timestamp DESC 
		          LIMIT 1000`

		rows, err := database.DB.Query(query, symbol)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var marketData []models.MarketData
		for rows.Next() {
			var m models.MarketData
			if err := rows.Scan(&m.ID, &m.Symbol, &m.Open, &m.High, &m.Low, &m.Close, &m.Volume, &m.Timestamp, &m.CreatedAt); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			marketData = append(marketData, m)
		}

		c.JSON(http.StatusOK, gin.H{
			"success": true,
			"data":    marketData,
			"count":   len(marketData),
		})
	}
}
