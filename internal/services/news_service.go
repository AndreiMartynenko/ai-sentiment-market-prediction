//go:build legacy
// +build legacy

package services

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"time"

	"ai_sentiment-market-prediction/internal/models"
)

type NewsService struct {
	apiKey string
	client *http.Client
}

func NewNewsService() *NewsService {
	return &NewsService{
		apiKey: "", // Will be loaded from config
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// FetchNews retrieves news articles from external APIs
func (s *NewsService) FetchNews(request models.NewsRequest) (*models.NewsResponse, error) {
	// Build NewsAPI URL
	url := "https://newsapi.org/v2/everything"

	// Add query parameters
	params := make(map[string]string)
	if request.Query != "" {
		params["q"] = request.Query
	}
	if request.Sources != "" {
		params["sources"] = request.Sources
	}
	if request.From != "" {
		params["from"] = request.From
	}
	if request.To != "" {
		params["to"] = request.To
	}
	if request.SortBy != "" {
		params["sortBy"] = request.SortBy
	}
	if request.PageSize > 0 {
		params["pageSize"] = strconv.Itoa(request.PageSize)
	}
	if request.Page > 0 {
		params["page"] = strconv.Itoa(request.Page)
	}

	// Add API key
	params["apiKey"] = s.apiKey

	// Build URL with parameters
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Add query parameters
	q := req.URL.Query()
	for key, value := range params {
		q.Add(key, value)
	}
	req.URL.RawQuery = q.Encode()

	// Make request
	resp, err := s.client.Do(req)
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

	// Parse NewsAPI response
	var newsAPIResponse struct {
		Status       string `json:"status"`
		TotalResults int    `json:"totalResults"`
		Articles     []struct {
			Title       string `json:"title"`
			Description string `json:"description"`
			URL         string `json:"url"`
			PublishedAt string `json:"publishedAt"`
			Source      struct {
				Name string `json:"name"`
			} `json:"source"`
		} `json:"articles"`
	}

	if err := json.Unmarshal(body, &newsAPIResponse); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	// Convert to our models
	var articles []models.NewsArticle
	for _, article := range newsAPIResponse.Articles {
		publishedAt, _ := time.Parse(time.RFC3339, article.PublishedAt)

		articles = append(articles, models.NewsArticle{
			Title:       article.Title,
			Content:     article.Description,
			Source:      article.Source.Name,
			URL:         article.URL,
			PublishedAt: publishedAt,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		})
	}

	return &models.NewsResponse{
		Articles: articles,
		Total:    newsAPIResponse.TotalResults,
		Page:     request.Page,
		PageSize: request.PageSize,
	}, nil
}

// GetNews retrieves stored news articles from database
func (s *NewsService) GetNews(symbol string, limit int) ([]models.NewsArticle, error) {
	// TODO: Implement database query
	return []models.NewsArticle{}, nil
}

// SaveNews saves news articles to database
func (s *NewsService) SaveNews(articles []models.NewsArticle) error {
	// TODO: Implement database insert
	return nil
}

// GetNewsByDateRange retrieves news articles within a date range
func (s *NewsService) GetNewsByDateRange(startDate, endDate time.Time, symbol string) ([]models.NewsArticle, error) {
	// TODO: Implement database query with date filtering
	return []models.NewsArticle{}, nil
}

// SearchNews performs full-text search on news articles
func (s *NewsService) SearchNews(query string, limit int) ([]models.NewsArticle, error) {
	// TODO: Implement full-text search
	return []models.NewsArticle{}, nil
}

// GetNewsSources returns available news sources
func (s *NewsService) GetNewsSources() ([]string, error) {
	// TODO: Implement sources retrieval
	return []string{"Reuters", "Bloomberg", "CNN", "BBC", "Financial Times"}, nil
}
