package config

import (
	"os"
	"strconv"
)

// Struct
type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
	API      APIConfig
	ML       MLConfig
}

// Server configuration
type ServerConfig struct {
	Port string
	Host string
}

// Database configuration
type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
	SSLMode  string
}

type APIConfig struct {
	NewsAPIKey    string
	TwitterAPIKey string
	TelegramToken string
}

type MLConfig struct {
	ModelPath           string
	BatchSize           int
	ConfidenceThreshold float64
}

func Load() *Config {
	return &Config{
		Server: ServerConfig{
			Port: getEnv("PORT", "8080"),
			Host: getEnv("HOST", "localhost"),
		},
		Database: DatabaseConfig{
			Host:     getEnv("DB_HOST", "localhost"),
			Port:     getEnvAsInt("DB_PORT", 5432),
			User:     getEnv("DB_USER", "postgres"),
			Password: getEnv("DB_PASSWORD", ""),
			DBName:   getEnv("DB_NAME", "sentiment_prediction"),
			SSLMode:  getEnv("DB_SSLMODE", "disable"),
		},
		API: APIConfig{
			NewsAPIKey:    getEnv("NEWS_API_KEY", ""),
			TwitterAPIKey: getEnv("TWITTER_API_KEY", ""),
			TelegramToken: getEnv("TELEGRAM_TOKEN", ""),
		},
		ML: MLConfig{
			ModelPath:           getEnv("MODEL_PATH", "./models"),
			BatchSize:           getEnvAsInt("BATCH_SIZE", 32),
			ConfidenceThreshold: getEnvAsFloat("CONFIDENCE_THRESHOLD", 0.7),
		},
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvAsFloat(key string, defaultValue float64) float64 {
	if value := os.Getenv(key); value != "" {
		if floatValue, err := strconv.ParseFloat(value, 64); err == nil {
			return floatValue
		}
	}
	return defaultValue
}
