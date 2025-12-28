//go:build legacy
// +build legacy

// handlers/signals.go
package handlers

import (
	"encoding/csv"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
)

type Signal struct {
	Action    string `json:"action"`
	Sentiment string `json:"sentiment"`
	Headline  string `json:"headline"`
}

func GetSignals(c *gin.Context) {
	file, err := os.Open("../data/processed/trading_signals.txt")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to load signals"})
		return
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.Comma = '|'

	lines, err := reader.ReadAll()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse signals"})
		return
	}

	var signals []Signal
	for _, line := range lines {
		if len(line) == 3 {
			signals = append(signals, Signal{
				Action:    strings.TrimSpace(line[0]),
				Sentiment: strings.TrimSpace(line[1]),
				Headline:  strings.TrimSpace(line[2]),
			})
		}
	}

	c.JSON(http.StatusOK, signals)
}
