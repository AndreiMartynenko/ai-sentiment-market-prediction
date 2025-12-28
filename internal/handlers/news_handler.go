//go:build legacy
// +build legacy

package handlers

import (
	"net/http"
	"strconv"
	"time"

	"ai_sentiment-market-prediction/internal/models"
	"ai_sentiment-market-prediction/internal/services"

	"github.com/gin-gonic/gin"
)

// NewsHandler handles news-related requests

type NewsHandler struct {
	service *services.NewsService
}

// NewNewsHandler creates a new NewsHandler with the given NewsService
func NewNewsHandler(service *services.NewsService) *NewsHandler {
	return &NewsHandler{
		service: service,
	}
}

// GetNews handles GET /api/v1/news
func (h *NewsHandler) GetNews(c *gin.Context) {
	symbol := c.Query("symbol")
	limitStr := c.DefaultQuery("limit", "50")

	limit, err := strconv.Atoi(limitStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid limit parameter",
		})
		return
	}

	news, err := h.service.GetNews(symbol, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get news",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    news,
		"count":   len(news),
	})
}

// FetchNews handles POST /api/v1/news/fetch
func (h *NewsHandler) FetchNews(c *gin.Context) {
	var request models.NewsRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request format",
			"details": err.Error(),
		})
		return
	}

	// Set defaults
	if request.PageSize == 0 {
		request.PageSize = 20
	}
	if request.Page == 0 {
		request.Page = 1
	}
	if request.SortBy == "" {
		request.SortBy = "publishedAt"
	}

	response, err := h.service.FetchNews(request)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to fetch news",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success":    true,
		"data":       response,
		"fetched_at": time.Now(),
	})
}

// SearchNews handles GET /api/v1/news/search
func (h *NewsHandler) SearchNews(c *gin.Context) {
	query := c.Query("q")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Query parameter 'q' is required",
		})
		return
	}

	limitStr := c.DefaultQuery("limit", "20")
	limit, err := strconv.Atoi(limitStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid limit parameter",
		})
		return
	}

	news, err := h.service.SearchNews(query, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to search news",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    news,
		"query":   query,
		"count":   len(news),
	})
}

// GetNewsByDateRange handles GET /api/v1/news/date-range
func (h *NewsHandler) GetNewsByDateRange(c *gin.Context) {
	startDateStr := c.Query("start_date")
	endDateStr := c.Query("end_date")
	symbol := c.Query("symbol")

	if startDateStr == "" || endDateStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Both start_date and end_date are required",
		})
		return
	}

	startDate, err := time.Parse("2006-01-02", startDateStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid start_date format. Use YYYY-MM-DD",
		})
		return
	}

	endDate, err := time.Parse("2006-01-02", endDateStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid end_date format. Use YYYY-MM-DD",
		})
		return
	}

	news, err := h.service.GetNewsByDateRange(startDate, endDate, symbol)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get news by date range",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    news,
		"count":   len(news),
		"period": gin.H{
			"start_date": startDate.Format("2006-01-02"),
			"end_date":   endDate.Format("2006-01-02"),
		},
	})
}

// GetNewsSources handles GET /api/v1/news/sources
func (h *NewsHandler) GetNewsSources(c *gin.Context) {
	sources, err := h.service.GetNewsSources()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to get news sources",
			"details": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    sources,
		"count":   len(sources),
	})
}
