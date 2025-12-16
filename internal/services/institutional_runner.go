package services

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"sort"
	"strings"
	"sync"
	"time"
)

type InstitutionalSignal struct {
	Symbol          string   `json:"symbol"`
	Signal          string   `json:"signal"` // LONG | SHORT | NO_TRADE
	ConfidenceScore int      `json:"confidence_score"`
	MarketRegime    string   `json:"market_regime"`
	SentimentScore  float64  `json:"sentiment_score"`
	Structure       string   `json:"structure"`
	EntryReason     []string `json:"entry_reason"`
	EntryPrice      float64  `json:"entry_price"`
	StopLoss        float64  `json:"stop_loss"`
	TakeProfit      float64  `json:"take_profit"`
	RiskReward      string   `json:"risk_reward"`
	Timeframe       string   `json:"timeframe"`
	InvalidateIf    []string `json:"invalidate_if"`

	CreatedAt time.Time `json:"created_at"`
}

type mlInstitutionalRequest struct {
	Symbol       string `json:"symbol"`
	Timeframe    string `json:"timeframe"`
	UseSentiment bool   `json:"use_sentiment"`
}

type mlNoTradeResponse struct {
	Signal string `json:"signal"`
	Reason string `json:"reason"`
}

type binanceTicker struct {
	Symbol      string `json:"symbol"`
	QuoteVolume string `json:"quoteVolume"`
}

// InstitutionalSignalRunner runs 24/7 scans and stores the latest valid signals in memory.
// It is intentionally conservative: NO_TRADE is ignored.
//
// This is meant as an always-on worker inside the Go backend.
// Later you can persist signals to Postgres instead of in-memory.
//
// Thread-safe.
//
// NOTE: This runner will make external network calls (Binance + ML service).
// Use a sensible Interval + per-symbol delay to avoid rate limiting.
//
// Default behavior:
// - scans top N USDT symbols by quote volume
// - calls ML /signal/institutional with use_sentiment=false
// - cooldown per symbol to avoid spam
//
// You can tune these fields via setters or by changing construction.

type InstitutionalSignalRunner struct {
	mlServiceURL string

	timeframe    string
	topN         int
	interval     time.Duration
	perSymbolGap time.Duration
	cooldown     time.Duration

	mu          sync.RWMutex
	latest      []InstitutionalSignal
	lastEmitted map[string]time.Time
	lastScanAt  time.Time
	lastError   string
	lastStats   RunnerStats
	httpClient  *http.Client
}

type RunnerStats struct {
	Scanned    int `json:"scanned"`
	Emitted    int `json:"emitted"`
	NoTrade    int `json:"no_trade"`
	Errors     int `json:"errors"`
	InCooldown int `json:"in_cooldown"`
}

func NewInstitutionalSignalRunner(mlServiceURL string) *InstitutionalSignalRunner {
	return &InstitutionalSignalRunner{
		mlServiceURL: strings.TrimRight(mlServiceURL, "/"),
		timeframe:    "15m",
		topN:         10,
		interval:     5 * time.Minute,
		perSymbolGap: 350 * time.Millisecond,
		cooldown:     45 * time.Minute,
		latest:       []InstitutionalSignal{},
		lastEmitted:  map[string]time.Time{},
		httpClient: &http.Client{
			Timeout: 20 * time.Second,
		},
	}
}

func (r *InstitutionalSignalRunner) SetInterval(d time.Duration) { r.interval = d }
func (r *InstitutionalSignalRunner) SetTopN(n int)               { r.topN = n }
func (r *InstitutionalSignalRunner) SetTimeframe(tf string)      { r.timeframe = tf }
func (r *InstitutionalSignalRunner) SetCooldown(d time.Duration) { r.cooldown = d }

func (r *InstitutionalSignalRunner) Latest() (signals []InstitutionalSignal, lastScan time.Time, lastErr string) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	copied := make([]InstitutionalSignal, len(r.latest))
	copy(copied, r.latest)
	return copied, r.lastScanAt, r.lastError
}

func (r *InstitutionalSignalRunner) Stats() RunnerStats {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return r.lastStats
}

func (r *InstitutionalSignalRunner) Run(ctx context.Context) {
	ticker := time.NewTicker(r.interval)
	defer ticker.Stop()

	// Do one scan immediately.
	r.scanOnce(ctx)

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			r.scanOnce(ctx)
		}
	}
}

func (r *InstitutionalSignalRunner) scanOnce(ctx context.Context) {
	symbols, err := r.fetchTopSymbols(ctx, r.topN)
	if err != nil {
		r.setError(fmt.Sprintf("fetchTopSymbols: %v", err))
		return
	}

	var found []InstitutionalSignal
	stats := RunnerStats{}
	for i, sym := range symbols {
		stats.Scanned++
		if i > 0 {
			select {
			case <-ctx.Done():
				return
			case <-time.After(r.perSymbolGap):
			}
		}

		if r.inCooldown(sym) {
			stats.InCooldown++
			continue
		}

		sig, ok, callErr := r.callInstitutional(ctx, sym)
		if callErr != nil {
			// keep going; record last error
			stats.Errors++
			r.setError(fmt.Sprintf("callInstitutional %s: %v", sym, callErr))
			continue
		}
		if !ok {
			stats.NoTrade++
			continue
		}

		sig.CreatedAt = time.Now().UTC()
		found = append(found, sig)
		r.markEmitted(sym)
		stats.Emitted++
	}

	// Sort by confidence desc.
	sort.Slice(found, func(i, j int) bool {
		return found[i].ConfidenceScore > found[j].ConfidenceScore
	})

	r.mu.Lock()
	r.latest = found
	r.lastScanAt = time.Now().UTC()
	r.lastStats = stats
	// Clear error if we had a successful scan cycle.
	if err == nil {
		r.lastError = ""
	}
	r.mu.Unlock()
}

func (r *InstitutionalSignalRunner) setError(msg string) {
	r.mu.Lock()
	r.lastError = msg
	r.lastScanAt = time.Now().UTC()
	r.mu.Unlock()
}

func (r *InstitutionalSignalRunner) inCooldown(symbol string) bool {
	r.mu.RLock()
	last, ok := r.lastEmitted[symbol]
	cd := r.cooldown
	r.mu.RUnlock()

	if !ok {
		return false
	}
	return time.Since(last) < cd
}

func (r *InstitutionalSignalRunner) markEmitted(symbol string) {
	r.mu.Lock()
	r.lastEmitted[symbol] = time.Now().UTC()
	r.mu.Unlock()
}

func (r *InstitutionalSignalRunner) fetchTopSymbols(ctx context.Context, topN int) ([]string, error) {
	// Binance 24hr tickers endpoint.
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, "https://api.binance.com/api/v3/ticker/24hr", nil)
	if err != nil {
		return nil, err
	}
	resp, err := r.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		b, _ := io.ReadAll(io.LimitReader(resp.Body, 1024))
		return nil, fmt.Errorf("binance status %d: %s", resp.StatusCode, string(b))
	}

	var tickers []binanceTicker
	if err := json.NewDecoder(resp.Body).Decode(&tickers); err != nil {
		return nil, err
	}

	type ranked struct {
		symbol string
		vol    float64
	}

	candidates := make([]ranked, 0, len(tickers))
	for _, t := range tickers {
		// Keep USDT quote pairs only.
		if !strings.HasSuffix(t.Symbol, "USDT") {
			continue
		}
		vol, _ := parseFloat(t.QuoteVolume)
		candidates = append(candidates, ranked{symbol: t.Symbol, vol: vol})
	}

	sort.Slice(candidates, func(i, j int) bool { return candidates[i].vol > candidates[j].vol })
	if topN <= 0 {
		topN = 10
	}
	if len(candidates) < topN {
		topN = len(candidates)
	}

	out := make([]string, 0, topN)
	for i := 0; i < topN; i++ {
		out = append(out, candidates[i].symbol)
	}
	if len(out) == 0 {
		return nil, errors.New("no USDT symbols from Binance")
	}
	return out, nil
}

func (r *InstitutionalSignalRunner) callInstitutional(ctx context.Context, symbol string) (InstitutionalSignal, bool, error) {
	url := r.mlServiceURL + "/signal/institutional"
	payload := mlInstitutionalRequest{Symbol: symbol, Timeframe: r.timeframe, UseSentiment: false}
	b, _ := json.Marshal(payload)

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(b))
	if err != nil {
		return InstitutionalSignal{}, false, err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := r.httpClient.Do(req)
	if err != nil {
		return InstitutionalSignal{}, false, err
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		bb, _ := io.ReadAll(io.LimitReader(resp.Body, 1024))
		return InstitutionalSignal{}, false, fmt.Errorf("ml status %d: %s", resp.StatusCode, string(bb))
	}

	// Read body once; may be NO_TRADE or full signal.
	body, err := io.ReadAll(io.LimitReader(resp.Body, 64*1024))
	if err != nil {
		return InstitutionalSignal{}, false, err
	}

	var noTrade mlNoTradeResponse
	if err := json.Unmarshal(body, &noTrade); err == nil {
		if strings.EqualFold(noTrade.Signal, "NO_TRADE") {
			return InstitutionalSignal{}, false, nil
		}
	}

	var sig InstitutionalSignal
	if err := json.Unmarshal(body, &sig); err != nil {
		return InstitutionalSignal{}, false, err
	}

	if !strings.EqualFold(sig.Signal, "LONG") && !strings.EqualFold(sig.Signal, "SHORT") {
		return InstitutionalSignal{}, false, nil
	}

	// Ensure symbol field is present even if ML omits it.
	if sig.Symbol == "" {
		sig.Symbol = symbol
	}

	return sig, true, nil
}

func parseFloat(s string) (float64, error) {
	// Fast-ish parse without importing strconv in a big way.
	// We'll use fmt.Sscanf which is slower but fine here.
	var f float64
	_, err := fmt.Sscanf(s, "%f", &f)
	return f, err
}
