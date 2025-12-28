package api

import (
	"encoding/json"
	"fmt"
	"math"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type gatewayTimeframe string

const (
	tf5m  gatewayTimeframe = "5m"
	tf15m gatewayTimeframe = "15m"
	tf1h  gatewayTimeframe = "1h"
	tf4h  gatewayTimeframe = "4h"
	tf1d  gatewayTimeframe = "1d"
)

type indicatorSummary struct {
	Timeframe string  `json:"timeframe"`
	Trend     string  `json:"trend"`
	RSI       float64 `json:"rsi"`
	Bias      string  `json:"bias"`
	Note      string  `json:"note"`
}

type indicatorsResponse struct {
	Symbol   string             `json:"symbol"`
	Scalping []indicatorSummary `json:"scalping"`
	Swing    []indicatorSummary `json:"swing"`
}

func ema(values []float64, period int) []float64 {
	if len(values) == 0 {
		return []float64{}
	}
	k := 2.0 / float64(period+1)
	out := make([]float64, len(values))
	prev := values[0]
	out[0] = prev
	for i := 1; i < len(values); i++ {
		prev = values[i]*k + prev*(1.0-k)
		out[i] = prev
	}
	return out
}

func rsi(values []float64, period int) []float64 {
	out := make([]float64, len(values))
	if len(values) <= period {
		for i := range out {
			out[i] = 50
		}
		return out
	}

	gains := 0.0
	losses := 0.0
	for i := 1; i <= period; i++ {
		change := values[i] - values[i-1]
		if change >= 0 {
			gains += change
		} else {
			losses -= change
		}
	}

	avgGain := gains / float64(period)
	avgLoss := losses / float64(period)

	rs := 100.0
	if avgLoss != 0 {
		rs = avgGain / avgLoss
	}
	out[period] = 100.0 - 100.0/(1.0+rs)

	for i := period + 1; i < len(values); i++ {
		change := values[i] - values[i-1]
		gain := 0.0
		loss := 0.0
		if change > 0 {
			gain = change
		}
		if change < 0 {
			loss = -change
		}

		avgGain = (avgGain*float64(period-1) + gain) / float64(period)
		avgLoss = (avgLoss*float64(period-1) + loss) / float64(period)

		rs2 := 100.0
		if avgLoss != 0 {
			rs2 = avgGain / avgLoss
		}
		out[i] = 100.0 - 100.0/(1.0+rs2)
	}

	for i := 0; i < period; i++ {
		out[i] = 50
	}
	return out
}

func summarize(tf gatewayTimeframe, closes []float64) *indicatorSummary {
	if len(closes) < 50 {
		return nil
	}

	ema20 := ema(closes, 20)
	ema50 := ema(closes, 50)
	rsi14 := rsi(closes, 14)

	lastClose := closes[len(closes)-1]
	lastEma20 := ema20[len(ema20)-1]
	lastEma50 := ema50[len(ema50)-1]
	lastRsi := rsi14[len(rsi14)-1]

	trend := "range"
	if lastClose > lastEma20 && lastEma20 > lastEma50 {
		trend = "bullish"
	} else if lastClose < lastEma20 && lastEma20 < lastEma50 {
		trend = "bearish"
	}

	bias := "neutral"
	note := ""

	if trend == "bullish" {
		if lastRsi > 70 {
			bias = "long"
			note = "Bullish trend but overbought – momentum strong, risk of pullback."
		} else if lastRsi >= 50 {
			bias = "long"
			note = "Bullish trend, RSI supportive – pullback long setups."
		} else {
			bias = "neutral"
			note = "Bullish trend, but RSI has cooled – wait for confirmation."
		}
	} else if trend == "bearish" {
		if lastRsi < 30 {
			bias = "short"
			note = "Bearish trend but oversold – risk of short squeeze."
		} else if lastRsi <= 50 {
			bias = "short"
			note = "Bearish trend, RSI supportive – bounce short setups."
		} else {
			bias = "neutral"
			note = "Bearish trend, but RSI has recovered – wait for confirmation."
		}
	} else {
		bias = "neutral"
		if lastRsi > 60 {
			note = "Range with bullish skew – breakouts possible."
		} else if lastRsi < 40 {
			note = "Range with bearish skew – breakdowns possible."
		} else {
			note = "No strong directional edge – range conditions."
		}
	}

	return &indicatorSummary{
		Timeframe: string(tf),
		Trend:     trend,
		RSI:       math.Round(lastRsi*10) / 10,
		Bias:      bias,
		Note:      note,
	}
}

func fetchKlines(client *http.Client, symbol string, tf gatewayTimeframe, limit int) ([]float64, error) {
	binanceBase := "https://api.binance.com"
	url := fmt.Sprintf("%s/api/v3/klines?symbol=%s&interval=%s&limit=%d", binanceBase, symbol, tf, limit)
	resp, err := client.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("binance error %d", resp.StatusCode)
	}

	var raw [][]any
	if err := json.NewDecoder(resp.Body).Decode(&raw); err != nil {
		return nil, err
	}

	closes := make([]float64, 0, len(raw))
	for _, k := range raw {
		if len(k) < 5 {
			continue
		}
		// close is index 4, typically string
		s, ok := k[4].(string)
		if !ok {
			continue
		}
		v, err := strconvParseFloat(s)
		if err != nil {
			continue
		}
		closes = append(closes, v)
	}
	return closes, nil
}

func strconvParseFloat(s string) (float64, error) {
	// local helper to avoid importing strconv in many places
	var f float64
	_, err := fmt.Sscan(s, &f)
	return f, err
}

func GetGatewayIndicators() gin.HandlerFunc {
	client := &http.Client{Timeout: 15 * time.Second}

	return func(c *gin.Context) {
		symbol := strings.ToUpper(strings.TrimSpace(c.Query("symbol")))
		if symbol == "" {
			symbol = "BTCUSDT"
		}

		tfs := []gatewayTimeframe{tf5m, tf15m, tf1h, tf4h, tf1d}

		scalping := make([]indicatorSummary, 0, 3)
		swing := make([]indicatorSummary, 0, 2)

		for _, tf := range tfs {
			closes, err := fetchKlines(client, symbol, tf, 200)
			if err != nil {
				// Skip timeframe on failure; keep endpoint resilient for demo.
				continue
			}
			s := summarize(tf, closes)
			if s == nil {
				continue
			}
			if tf == tf5m || tf == tf15m || tf == tf1h {
				scalping = append(scalping, *s)
			}
			if tf == tf4h || tf == tf1d {
				swing = append(swing, *s)
			}
		}

		c.JSON(http.StatusOK, indicatorsResponse{Symbol: symbol, Scalping: scalping, Swing: swing})
	}
}
