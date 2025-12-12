package services

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq"
)

// DatabaseService handles database operations
type DatabaseService struct {
	DB *sql.DB
}

// NewDatabaseService initializes a new DatabaseService
func NewDatabaseService(host, port, user, password, dbname, sslmode string) (*DatabaseService, error) {
	// Build connection string
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		host, port, user, password, dbname, sslmode)

	// Open database connection
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// Test connection
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	log.Println("✅ Database connection established")

	return &DatabaseService{DB: db}, nil
}

// Close closes the database connection
func (d *DatabaseService) Close() error {
	if d.DB != nil {
		return d.DB.Close()
	}
	return nil
}

// Health check for database
func (d *DatabaseService) HealthCheck() error {
	if d.DB == nil {
		return fmt.Errorf("database connection is nil")
	}
	return d.DB.Ping()
}
