package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestSetupRoutes_RegistersGatewayEndpoints(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Mock Binance
	mock := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/api/v3/ticker/price":
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(map[string]string{"symbol": "BTCUSDT", "price": "1.00"})
			return
		case "/api/v3/klines":
			// Minimal klines response with enough points (60) for summarize
			klines := make([][]any, 0, 60)
			close := 100.0
			for i := 0; i < 60; i++ {
				close += 0.5
				klines = append(klines, []any{float64(i), "1", "1", "1", "100.0", "1"})
			}
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(klines)
			return
		default:
			w.WriteHeader(http.StatusNotFound)
			return
		}
	}))
	defer mock.Close()

	old := binanceBaseURL
	binanceBaseURL = mock.URL
	defer func() { binanceBaseURL = old }()

	r := gin.New()
	SetupRoutes(r, nil, "http://example-ml", nil)

	// health endpoint exists
	wHealth := httptest.NewRecorder()
	reqHealth := httptest.NewRequest(http.MethodGet, "/health", nil)
	r.ServeHTTP(wHealth, reqHealth)
	if wHealth.Code != http.StatusOK {
		t.Fatalf("expected health 200, got %d", wHealth.Code)
	}

	// gateway price
	wPrice := httptest.NewRecorder()
	reqPrice := httptest.NewRequest(http.MethodGet, "/api/v1/price?symbol=BTCUSDT", nil)
	r.ServeHTTP(wPrice, reqPrice)
	if wPrice.Code != http.StatusOK {
		t.Fatalf("expected price 200, got %d: %s", wPrice.Code, wPrice.Body.String())
	}

	// gateway indicators
	wInd := httptest.NewRecorder()
	reqInd := httptest.NewRequest(http.MethodGet, "/api/v1/indicators?symbol=BTCUSDT", nil)
	r.ServeHTTP(wInd, reqInd)
	if wInd.Code != http.StatusOK {
		t.Fatalf("expected indicators 200, got %d: %s", wInd.Code, wInd.Body.String())
	}

	// mock proof endpoint exists
	wProof := httptest.NewRecorder()
	reqProof := httptest.NewRequest(http.MethodPost, "/api/v1/proof/mock", nil)
	r.ServeHTTP(wProof, reqProof)
	if wProof.Code != http.StatusBadRequest {
		t.Fatalf("expected proof missing-body 400, got %d", wProof.Code)
	}
}
