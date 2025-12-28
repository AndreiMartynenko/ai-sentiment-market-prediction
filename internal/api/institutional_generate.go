package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type institutionalGenerateRequest struct {
	Symbol       string         `json:"symbol" binding:"required"`
	Timeframe    string         `json:"timeframe"`
	UseSentiment bool           `json:"use_sentiment"`
	Preset       string         `json:"preset"`
	Rules        map[string]any `json:"rules"`
	Debug        bool           `json:"debug"`
}

func GenerateInstitutionalSignal(mlServiceURL string) gin.HandlerFunc {
	mlBase := strings.TrimRight(mlServiceURL, "/")
	client := &http.Client{Timeout: 25 * time.Second}

	return func(c *gin.Context) {
		var reqBody institutionalGenerateRequest
		if err := c.ShouldBindJSON(&reqBody); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		if reqBody.Timeframe == "" {
			reqBody.Timeframe = "15m"
		}

		mlPath := "/signal/institutional"
		if reqBody.Debug {
			mlPath = "/signal/institutional/debug"
		}

		payload := map[string]any{
			"symbol":        reqBody.Symbol,
			"timeframe":     reqBody.Timeframe,
			"use_sentiment": reqBody.UseSentiment,
			"preset":        reqBody.Preset,
			"rules":         reqBody.Rules,
		}

		b, err := json.Marshal(payload)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to encode request"})
			return
		}

		mlReq, err := http.NewRequest(http.MethodPost, mlBase+mlPath, bytes.NewReader(b))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create request"})
			return
		}
		mlReq.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(mlReq)
		if err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": fmt.Sprintf("ml request failed: %v", err)})
			return
		}
		defer resp.Body.Close()

		raw, err := io.ReadAll(io.LimitReader(resp.Body, 256*1024))
		if err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": "failed to read ml response"})
			return
		}

		if resp.StatusCode < 200 || resp.StatusCode >= 300 {
			c.JSON(http.StatusBadGateway, gin.H{
				"error":     "ml service returned error",
				"ml_status": resp.StatusCode,
				"body":      string(raw),
			})
			return
		}

		var out any
		if err := json.Unmarshal(raw, &out); err != nil {
			c.JSON(http.StatusBadGateway, gin.H{
				"error": "failed to decode ml json",
				"body":  string(raw),
			})
			return
		}

		c.JSON(http.StatusOK, out)
	}
}
