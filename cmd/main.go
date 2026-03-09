package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/rs/zerolog"

	"github.com/AndreiMartynenko/proof-of-signal/internal/api"
	"github.com/AndreiMartynenko/proof-of-signal/internal/config"
	"github.com/AndreiMartynenko/proof-of-signal/internal/db"
	"github.com/AndreiMartynenko/proof-of-signal/internal/middleware"
	"github.com/AndreiMartynenko/proof-of-signal/internal/services"
)

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

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

	logger := zerolog.New(os.Stdout).With().Timestamp().Logger()

	// Initialize router
	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(middleware.RequestID())
	router.Use(middleware.AccessLog(logger))

	// Metrics endpoint
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// Start 24/7 institutional signal runner (in-memory)
	var runner *services.InstitutionalSignalRunner
	if os.Getenv("ENABLE_INSTITUTIONAL_RUNNER") == "true" {
		runner = services.NewInstitutionalSignalRunner(cfg.MLServiceURL)
		go runner.Run(ctx)
	}

	// Setup API routes
	api.SetupRoutes(router, database, cfg.MLServiceURL, runner)

	server := &http.Server{
		Addr:              ":" + cfg.Port,
		Handler:           router,
		ReadTimeout:       5 * time.Second,
		ReadHeaderTimeout: 5 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	log.Printf("Starting server on port %s", cfg.Port)
	go func() {
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Printf("HTTP server error: %v", err)
			stop()
		}
	}()

	<-ctx.Done()

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Printf("HTTP server shutdown error: %v", err)
	}
}
