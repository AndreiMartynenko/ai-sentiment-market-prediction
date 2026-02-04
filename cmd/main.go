package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"

	"ai_sentiment-market-prediction/internal/api"
	"ai_sentiment-market-prediction/internal/config"
	"ai_sentiment-market-prediction/internal/db"
	"ai_sentiment-market-prediction/internal/services"
)

// Where should I add WS
func main() {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatal("Failed to load configuration:", err)
	}

	// Initialize database connection (optional in NO_DB mode)
	var database *db.Connection
	if os.Getenv("NO_DB") != "true" {
		database, err = db.NewConnection(cfg.DatabaseURL)
		if err != nil {
			log.Printf("Database unavailable, starting without DB: %v", err)
			database = nil
		}
	} else {
		log.Printf("NO_DB=true -> starting without database")
	}
	if database != nil {
		defer database.Close()
	}

	// Initialize router
	router := gin.Default()

	// Start 24/7 institutional signal runner (in-memory)
	var runner *services.InstitutionalSignalRunner
	if os.Getenv("ENABLE_INSTITUTIONAL_RUNNER") == "true" {
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()

		shutdownCh := make(chan os.Signal, 1)
		signal.Notify(shutdownCh, syscall.SIGINT, syscall.SIGTERM)
		go func() {
			<-shutdownCh
			cancel()
		}()

		runner = services.NewInstitutionalSignalRunner(cfg.MLServiceURL)
		go runner.Run(ctx)
	}

	// Setup API routes
	api.SetupRoutes(router, database, cfg.MLServiceURL, runner)

	// Get port from environment or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Start server
	log.Printf("Starting server on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
