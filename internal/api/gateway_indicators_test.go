package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestGatewayIndicators_Schema_MockedBinance(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Create a mock klines response with enough points.
	// Each kline: [openTime, open, high, low, close, volume, ...]
	klines := make([][]any, 0, 60)
	close := 100.0
	for i := 0; i < 60; i++ {
		close += 0.5
		klines = append(klines, []any{float64(i), "1", "1", "1", formatFloat(close), "1"})
	}

	mock := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !strings.HasPrefix(r.URL.Path, "/api/v3/klines") {
			w.WriteHeader(http.StatusNotFound)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(klines)
	}))
	defer mock.Close()

	old := binanceBaseURL
	binanceBaseURL = mock.URL
	defer func() { binanceBaseURL = old }()

	r := gin.New()
	r.GET("/api/v1/indicators", GetGatewayIndicators())

	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/indicators?symbol=BTCUSDT", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d: %s", w.Code, w.Body.String())
	}

	var out map[string]any
	_ = json.Unmarshal(w.Body.Bytes(), &out)

	if out["symbol"] != "BTCUSDT" {
		t.Fatalf("expected symbol BTCUSDT, got %v", out["symbol"])
	}
	if _, ok := out["scalping"]; !ok {
		t.Fatalf("expected scalping in response")
	}
	if _, ok := out["swing"]; !ok {
		t.Fatalf("expected swing in response")
	}
}

func formatFloat(f float64) string {
	// minimal formatting for test JSON
	return strings.TrimRight(strings.TrimRight(fmt.Sprintf("%.2f", f), "0"), ".")
}
