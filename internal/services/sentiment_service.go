package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/AndreiMartynenko/ai-sentiment-market-prediction/internal/models"
)

type SentimentService struct {
	baseURL string
	client  *http.Client
}

func NewSentimentService() *SentimentService {
	return &SentimentService{
		baseURL: "http://localhost:8000", // Python ML service URL
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// AnalyzeText performs sentiment analysis on the given text
func (s *SentimentService) AnalyzeText(text string, model string) (*models.AnalyzeTextResponse, error) {
	request := map[string]interface{}{
		"text":  text,
		"model": model,
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := s.client.Post(
		s.baseURL+"/analyze",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	var response models.AnalyzeTextResponse
	if err := json.Unmarshal(body, &response); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return &response, nil
}

// AnalyzeBatch performs sentiment analysis on multiple texts
func (s *SentimentService) AnalyzeBatch(texts []string, model string) ([]models.AnalyzeTextResponse, error) {
	request := map[string]interface{}{
		"texts": texts,
		"model": model,
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := s.client.Post(
		s.baseURL+"/analyze_batch",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	var response []models.AnalyzeTextResponse
	if err := json.Unmarshal(body, &response); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return response, nil
}

// GetAvailableModels returns the list of available sentiment analysis models
func (s *SentimentService) GetAvailableModels() ([]string, error) {
	resp, err := s.client.Get(s.baseURL + "/models")
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	var models []string
	if err := json.Unmarshal(body, &models); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return models, nil
}

// GetModelPerformance returns performance metrics for a specific model
func (s *SentimentService) GetModelPerformance(model string) (*models.PerformanceMetrics, error) {
	resp, err := s.client.Get(s.baseURL + "/models/" + model + "/performance")
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	var performance models.PerformanceMetrics
	if err := json.Unmarshal(body, &performance); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return &performance, nil
}
