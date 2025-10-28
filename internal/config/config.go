package config

import (
	"os"
)

// Config holds all configuration for the application
type Config struct {
	DatabaseURL   string
	MLServiceURL  string
	Port          string
	NewsAPIKey    string
	BinanceAPIKey string
}

// Load retrieves configuration from environment variables
func Load() (*Config, error) {
	return &Config{
		DatabaseURL:   getEnv("DATABASE_URL", "postgres://postgres:postgres@postgres:5432/sentiment_market?sslmode=disable"),
		MLServiceURL:  getEnv("ML_SERVICE_URL", "http://ml-service:8000"),
		Port:          getEnv("PORT", "8080"),
		NewsAPIKey:    getEnv("NEWS_API_KEY", ""),
		BinanceAPIKey: getEnv("BINANCE_API_KEY", ""),
	}, nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
