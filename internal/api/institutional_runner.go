package api

import (
	"net/http"
	"strconv"

	"ai_sentiment-market-prediction/internal/services"

	"github.com/gin-gonic/gin"
)

// GetLatestInstitutionalSignals returns the latest in-memory institutional signals
// produced by the background runner.
func GetLatestInstitutionalSignals(runner *services.InstitutionalSignalRunner) gin.HandlerFunc {
	return func(c *gin.Context) {
		limitStr := c.DefaultQuery("limit", "10")
		limit, _ := strconv.Atoi(limitStr)
		if limit <= 0 {
			limit = 10
		}
		if limit > 50 {
			limit = 50
		}

		signals, lastScanAt, lastErr := runner.Latest()
		if len(signals) > limit {
			signals = signals[:limit]
		}
		stats := runner.Stats()

		c.JSON(http.StatusOK, gin.H{
			"success":      true,
			"last_scan_at": lastScanAt,
			"runner_error": lastErr,
			"stats":        stats,
			"count":        len(signals),
			"data":         signals,
		})
	}
}
