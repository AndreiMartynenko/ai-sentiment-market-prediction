package config

import (
	"os"
	"testing"
)

func TestLoad_Defaults(t *testing.T) {
	// Ensure defaults are used when env vars are absent.
	_ = os.Unsetenv("DATABASE_URL")
	_ = os.Unsetenv("ML_SERVICE_URL")
	_ = os.Unsetenv("PORT")
	_ = os.Unsetenv("NEWS_API_KEY")
	_ = os.Unsetenv("BINANCE_API_KEY")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("expected nil error, got %v", err)
	}
	if cfg.Port != "8080" {
		t.Fatalf("expected default port 8080, got %s", cfg.Port)
	}
	if cfg.MLServiceURL == "" {
		t.Fatalf("expected default MLServiceURL")
	}
	if cfg.DatabaseURL == "" {
		t.Fatalf("expected default DatabaseURL")
	}
}

func TestLoad_Overrides(t *testing.T) {
	// Ensure env vars override defaults.
	_ = os.Setenv("DATABASE_URL", "postgres://example")
	_ = os.Setenv("ML_SERVICE_URL", "http://localhost:8000")
	_ = os.Setenv("PORT", "9999")
	_ = os.Setenv("NEWS_API_KEY", "news")
	_ = os.Setenv("BINANCE_API_KEY", "binance")
	defer func() {
		_ = os.Unsetenv("DATABASE_URL")
		_ = os.Unsetenv("ML_SERVICE_URL")
		_ = os.Unsetenv("PORT")
		_ = os.Unsetenv("NEWS_API_KEY")
		_ = os.Unsetenv("BINANCE_API_KEY")
	}()

	cfg, err := Load()
	if err != nil {
		t.Fatalf("expected nil error, got %v", err)
	}
	if cfg.DatabaseURL != "postgres://example" {
		t.Fatalf("expected override DatabaseURL, got %s", cfg.DatabaseURL)
	}
	if cfg.MLServiceURL != "http://localhost:8000" {
		t.Fatalf("expected override MLServiceURL, got %s", cfg.MLServiceURL)
	}
	if cfg.Port != "9999" {
		t.Fatalf("expected override port 9999, got %s", cfg.Port)
	}
	if cfg.NewsAPIKey != "news" {
		t.Fatalf("expected override NewsAPIKey, got %s", cfg.NewsAPIKey)
	}
	if cfg.BinanceAPIKey != "binance" {
		t.Fatalf("expected override BinanceAPIKey, got %s", cfg.BinanceAPIKey)
	}
}
