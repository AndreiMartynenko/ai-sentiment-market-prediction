package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestPublishMockProof_Deterministic(t *testing.T) {
	gin.SetMode(gin.TestMode)

	r := gin.New()
	r.POST("/api/v1/proof/mock", PublishMockProof())

	payload := map[string]any{
		"signal": map[string]any{
			"symbol": "BTCUSDT",
			"side":   "BUY",
			"entry":  100.0,
		},
	}

	b, _ := json.Marshal(payload)

	req1 := httptest.NewRequest(http.MethodPost, "/api/v1/proof/mock", bytes.NewReader(b))
	req1.Header.Set("Content-Type", "application/json")
	w1 := httptest.NewRecorder()
	r.ServeHTTP(w1, req1)
	if w1.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d: %s", w1.Code, w1.Body.String())
	}

	req2 := httptest.NewRequest(http.MethodPost, "/api/v1/proof/mock", bytes.NewReader(b))
	req2.Header.Set("Content-Type", "application/json")
	w2 := httptest.NewRecorder()
	r.ServeHTTP(w2, req2)
	if w2.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d: %s", w2.Code, w2.Body.String())
	}

	var out1 map[string]any
	var out2 map[string]any
	_ = json.Unmarshal(w1.Body.Bytes(), &out1)
	_ = json.Unmarshal(w2.Body.Bytes(), &out2)

	if out1["proof_hash"] != out2["proof_hash"] {
		t.Fatalf("proof_hash should be deterministic")
	}
	if out1["tx_signature"] != out2["tx_signature"] {
		t.Fatalf("tx_signature should be deterministic")
	}
}

func TestPublishMockProof_RequiresSignal(t *testing.T) {
	gin.SetMode(gin.TestMode)

	r := gin.New()
	r.POST("/api/v1/proof/mock", PublishMockProof())

	req := httptest.NewRequest(http.MethodPost, "/api/v1/proof/mock", bytes.NewReader([]byte(`{}`)))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d: %s", w.Code, w.Body.String())
	}
}
