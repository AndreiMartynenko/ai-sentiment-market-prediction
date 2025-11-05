package handlers

import (
	"net/http"
	"strconv"
	"time"

	"github.com/AndreiMartynenko/ai-sentiment-market-prediction/internal/models"
	"github.com/AndreiMartynenko/ai-sentiment-market-prediction/internal/services"
	"github.com/gin-gonic/gin"
)

// SignalHandler handles signal-related requests
type SignalHandler struct {
	service *services.SignalService
}

func NewSignalHandler(service *services.SignalService) *SignalHandler {
	return &SignalHandler{
		service: service,
	}
}

// GetSignals handles GET /api/v1/signals
func (h *SignalHandler) GetSignals(c *gin.Context) {
	symbol := c.Query("symbol")
	limitStr := c.DefaultQuery("limit", "50")

	limit, err := strconv.Atoi(limitStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid limit parameter",
		})
		return
	}

	signals, err := h.service.GetSignals(symbol, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get signals",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    signals,
		"count":   len(signals),
	})
}

// GenerateSignals handles POST /api/v1/signals/generate
func (h *SignalHandler) GenerateSignals(c *gin.Context) {
	var request models.GenerateSignalsRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}

	// Set defaults
	if request.Timeframe == "" {
		request.Timeframe = "1d"
	}
	if request.Lookback == 0 {
		request.Lookback = 7 // 7 days default
	}

	signals, err := h.service.GenerateSignals(request.Symbols, request.Timeframe, request.Lookback)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to generate signals",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":      true,
		"data":         signals,
		"count":        len(signals),
		"generated_at": time.Now(),
	})
}

// GetPerformance handles GET /api/v1/signals/performance
func (h *SignalHandler) GetPerformance(c *gin.Context) {
	symbol := c.Query("symbol")
	startDateStr := c.Query("start_date")
	endDateStr := c.Query("end_date")

	// Parse dates
	var startDate, endDate time.Time
	var err error

	if startDateStr != "" {
		startDate, err = time.Parse("2006-01-02", startDateStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Invalid start_date format. Use YYYY-MM-DD",
			})
			return
		}
	} else {
		startDate = time.Now().AddDate(0, 0, -30) // Default to 30 days ago
	}

	if endDateStr != "" {
		endDate, err = time.Parse("2006-01-02", endDateStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Invalid end_date format. Use YYYY-MM-DD",
			})
			return
		}
	} else {
		endDate = time.Now() // Default to now
	}

	performance, err := h.service.GetPerformance(symbol, startDate, endDate)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get performance data",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    performance,
		"period": gin.H{
			"start_date": startDate.Format("2006-01-02"),
			"end_date":   endDate.Format("2006-01-02"),
		},
	})
}

// GetSignalAccuracy handles GET /api/v1/signals/accuracy
func (h *SignalHandler) GetSignalAccuracy(c *gin.Context) {
	symbol := c.Query("symbol")
	startDateStr := c.Query("start_date")
	endDateStr := c.Query("end_date")

	// Parse dates
	var startDate, endDate time.Time
	var err error

	if startDateStr != "" {
		startDate, err = time.Parse("2006-01-02", startDateStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Invalid start_date format. Use YYYY-MM-DD",
			})
			return
		}
	} else {
		startDate = time.Now().AddDate(0, 0, -30)
	}

	if endDateStr != "" {
		endDate, err = time.Parse("2006-01-02", endDateStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Invalid end_date format. Use YYYY-MM-DD",
			})
			return
		}
	} else {
		endDate = time.Now()
	}

	accuracy, err := h.service.GetSignalAccuracy(symbol, startDate, endDate)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to calculate accuracy",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": gin.H{
			"symbol":   symbol,
			"accuracy": accuracy,
			"period": gin.H{
				"start_date": startDate.Format("2006-01-02"),
				"end_date":   endDate.Format("2006-01-02"),
			},
		},
	})
}
