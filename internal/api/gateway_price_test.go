package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestGatewayPrice_MissingSymbol(t *testing.T) {
	gin.SetMode(gin.TestMode)

	r := gin.New()
	r.GET("/api/v1/price", GetGatewayPrice())

	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/price", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d", w.Code)
	}
}

func TestGatewayPrice_Success_MockedBinance(t *testing.T) {
	gin.SetMode(gin.TestMode)

	mock := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/v3/ticker/price" {
			w.WriteHeader(http.StatusNotFound)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"symbol": "BTCUSDT", "price": "123.45"})
	}))
	defer mock.Close()

	old := binanceBaseURL
	binanceBaseURL = mock.URL
	defer func() { binanceBaseURL = old }()

	r := gin.New()
	r.GET("/api/v1/price", GetGatewayPrice())

	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/price?symbol=btcusdt", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d: %s", w.Code, w.Body.String())
	}

	var out map[string]any
	_ = json.Unmarshal(w.Body.Bytes(), &out)
	if out["symbol"] != "BTCUSDT" {
		t.Fatalf("expected symbol BTCUSDT, got %v", out["symbol"])
	}
	if out["price"] != "123.45" {
		t.Fatalf("expected price 123.45, got %v", out["price"])
	}
}
