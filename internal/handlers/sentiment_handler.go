package handlers

import (
	"net/http"

	"ai_sentiment-market-prediction/internal/models"
	"ai_sentiment-market-prediction/internal/services"

	"github.com/gin-gonic/gin"
)

type SentimentHandler struct {
	service *services.SentimentService
}

// NewSentimentHandler creates a new SentimentHandler with the given SentimentService
func NewSentimentHandler(service *services.SentimentService) *SentimentHandler {
	return &SentimentHandler{
		service: service,
	}
}

// AnalyzeText handles POST /api/v1/sentiment/analyze
func (h *SentimentHandler) AnalyzeText(c *gin.Context) {
	var request models.AnalyzeTextRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}

	// Set default model if not specified
	model := request.Model
	if model == "" {
		model = "finbert"
	}

	response, err := h.service.AnalyzeText(request.Text, model)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to analyze sentiment",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    response,
	})
}

// GetBatchResults handles GET /api/v1/sentiment/batch
func (h *SentimentHandler) GetBatchResults(c *gin.Context) {
	// Get query parameters
	model := c.DefaultQuery("model", "finbert")
	limit := c.DefaultQuery("limit", "100")

	// TODO: Implement batch results retrieval from database
	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    []models.AnalyzeTextResponse{},
		"message": "Batch results endpoint - implementation pending",
		"model":   model,
		"limit":   limit,
	})
}

// GetModels handles GET /api/v1/sentiment/models
func (h *SentimentHandler) GetModels(c *gin.Context) {
	models, err := h.service.GetAvailableModels()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get available models",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    models,
	})
}

// GetModelPerformance handles GET /api/v1/sentiment/models/:model/performance
func (h *SentimentHandler) GetModelPerformance(c *gin.Context) {
	model := c.Param("model")

	performance, err := h.service.GetModelPerformance(model)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get model performance",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    performance,
	})
}
