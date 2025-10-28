package api

import (
	"ai_sentiment-market-prediction/internal/db"

	"github.com/gin-gonic/gin"
)

// SetupRoutes configures all API routes
func SetupRoutes(router *gin.Engine, database *db.Connection, mlServiceURL string) {
	// Health check endpoint
	router.GET("/health", HealthCheck(database))

	// API v1 group
	v1 := router.Group("/api/v1")
	{
		// Signals endpoints
		v1.GET("/signals", GetSignals(database))
		v1.GET("/signals/:symbol", GetSignalsBySymbol(database))
		v1.POST("/signals/generate", GenerateSignals(database, mlServiceURL))

		// Sentiment endpoints
		v1.GET("/sentiment", GetSentiment(database))
		v1.GET("/sentiment/:symbol", GetSentimentBySymbol(database))

		// Technical indicators endpoints
		v1.GET("/technical", GetTechnical(database))
		v1.GET("/technical/:symbol", GetTechnicalBySymbol(database))

		// News endpoints
		v1.GET("/news", GetNews(database))
		v1.GET("/news/:symbol", GetNewsBySymbol(database))

		// Market data endpoints
		v1.GET("/market", GetMarketData(database))
		v1.GET("/market/:symbol", GetMarketDataBySymbol(database))
	}
}
