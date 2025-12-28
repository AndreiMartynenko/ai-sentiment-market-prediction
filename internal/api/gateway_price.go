package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

var binanceBaseURL = "https://api.binance.com"

type binancePriceResponse struct {
	Symbol string `json:"symbol"`
	Price  string `json:"price"`
}

func GetGatewayPrice() gin.HandlerFunc {
	client := &http.Client{Timeout: 10 * time.Second}

	return func(c *gin.Context) {
		symbol := strings.ToUpper(strings.TrimSpace(c.Query("symbol")))
		if symbol == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "missing symbol"})
			return
		}

		url := fmt.Sprintf("%s/api/v3/ticker/price?symbol=%s", strings.TrimRight(binanceBaseURL, "/"), symbol)
		req, err := http.NewRequest(http.MethodGet, url, nil)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create request"})
			return
		}

		resp, err := client.Do(req)
		if err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": fmt.Sprintf("binance request failed: %v", err)})
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode < 200 || resp.StatusCode >= 300 {
			c.JSON(http.StatusBadGateway, gin.H{"error": fmt.Sprintf("binance error %d", resp.StatusCode)})
			return
		}

		var out binancePriceResponse
		if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": "failed to decode binance response"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"symbol": symbol, "price": out.Price})
	}
}
