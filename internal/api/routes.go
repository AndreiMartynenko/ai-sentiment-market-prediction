package api

import (
	"ai_sentiment-market-prediction/internal/db"
	"ai_sentiment-market-prediction/internal/services"

	"github.com/gin-gonic/gin"
)

// SetupRoutes configures all API routes
func SetupRoutes(router *gin.Engine, database *db.Connection, mlServiceURL string, runner *services.InstitutionalSignalRunner) {
	// Health check endpoint
	router.GET("/health", HealthCheck(database))

	// API v1 group
	v1 := router.Group("/api/v1")
	{
		// Demo gateway endpoints (no DB required)
		v1.GET("/price", GetGatewayPrice())
		v1.GET("/indicators", GetGatewayIndicators())
		v1.POST("/proof/mock", PublishMockProof())

		// Signals endpoints
		if database != nil {
			v1.GET("/signals", GetSignals(database))
			v1.GET("/signals/:symbol", GetSignalsBySymbol(database))
			v1.POST("/signals/generate", GenerateSignals(database, mlServiceURL))
		}
		v1.POST("/signals/institutional/generate", GenerateInstitutionalSignal(mlServiceURL))
		v1.POST("/signals/institutional/proof", PublishInstitutionalSignalProof(mlServiceURL))
		if runner != nil {
			v1.GET("/signals/institutional/latest", GetLatestInstitutionalSignals(runner))
		}

		// Sentiment endpoints
		if database != nil {
			v1.GET("/sentiment", GetSentiment(database))
			v1.GET("/sentiment/:symbol", GetSentimentBySymbol(database))
		}

		// Technical indicators endpoints
		if database != nil {
			v1.GET("/technical", GetTechnical(database))
			v1.GET("/technical/:symbol", GetTechnicalBySymbol(database))
		}

		// News endpoints
		if database != nil {
			v1.GET("/news", GetNews(database))
			v1.GET("/news/:symbol", GetNewsBySymbol(database))
		}

		// Market data endpoints
		if database != nil {
			v1.GET("/market", GetMarketData(database))
			v1.GET("/market/:symbol", GetMarketDataBySymbol(database))
		}
	}
}
