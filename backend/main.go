package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	// Setup Gin router
	router := gin.Default()

	// CORS middleware
	router.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// API routes
	api := router.Group("/api/v1")
	{
		// Health check
		api.GET("/health", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"status":  "healthy",
				"service": "ai-sentiment-market-prediction",
				"version": "1.0.0",
			})
		})

		// Simple sentiment analysis endpoint
		api.POST("/sentiment/analyze", func(c *gin.Context) {
			var request struct {
				Text  string `json:"text" binding:"required"`
				Model string `json:"model,omitempty"`
			}

			if err := c.ShouldBindJSON(&request); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{
					"error": "Invalid request format",
				})
				return
			}

			// For now, return a mock response
			response := gin.H{
				"success": true,
				"data": gin.H{
					"sentiment":  "POSITIVE",
					"confidence": 0.85,
					"model":      "mock",
					"text":       request.Text,
				},
			}

			c.JSON(http.StatusOK, response)
		})

		// Simple signal generation
		api.POST("/signals/generate", func(c *gin.Context) {
			var request struct {
				Symbols   []string `json:"symbols" binding:"required"`
				Timeframe string   `json:"timeframe,omitempty"`
				Lookback  int      `json:"lookback,omitempty"`
			}
			// If error in binding JSON
			if err := c.ShouldBindJSON(&request); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{
					"error": "Invalid request format",
				})
				return
			}

			// Generate mock signals
			var signals []gin.H
			for _, symbol := range request.Symbols {
				signals = append(signals, gin.H{
					"symbol":          symbol,
					"action":          "BUY",
					"strength":        0.75,
					"confidence":      0.80,
					"reasoning":       fmt.Sprintf("Positive sentiment detected for %s", symbol),
					"sentiment_score": 0.85,
				})
			}

			c.JSON(http.StatusOK, gin.H{
				"success": true,
				"data":    signals,
				"count":   len(signals),
			})
		})
	}

	// Start server
	port := "8080"
	log.Printf("🚀 Server starting on port %s", port)
	log.Printf("📊 AI Sentiment Market Prediction API v1.0.0")
	log.Printf("🔗 Health check: http://localhost:%s/api/v1/health", port)

	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
