"use client"

import React, { useEffect, useRef, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

const mockSignals = [
  {
    id: 'SIG-001',
    pair: 'BTC/USDT',
    side: 'BUY',
    confidence: 0.91,
    timeframe: '5m',
    sentAt: '2 min ago',
  },
  {
    id: 'SIG-002',
    pair: 'ETH/USDT',
    side: 'SELL',
    confidence: 0.84,
    timeframe: '15m',
    sentAt: '7 min ago',
  },
  {
    id: 'SIG-003',
    pair: 'SOL/USDT',
    side: 'NEUTRAL',
    confidence: 0.63,
    timeframe: '1h',
    sentAt: '12 min ago',
  },
]

const POPULAR_SYMBOLS = [
  'BTCUSDT',
  'ETHUSDT',
  'SOLUSDT',
  'BNBUSDT',
  'XRPUSDT',
  'ADAUSDT',
  'DOGEUSDT',
  'TONUSDT',
  'LINKUSDT',
  'AVAXUSDT',
]

type NewsItem = {
  id: string
  title: string
  source: string
  url: string
  publishedAt: string
  sentimentLabel?: string
  sentimentScore?: number
  sentimentConfidence?: number
}

type IndicatorSummary = {
  timeframe: '5m' | '15m' | '1h' | '4h' | '1d'
  trend: 'bullish' | 'bearish' | 'range'
  rsi: number
  bias: 'long' | 'short' | 'neutral'
  note: string
}

type IndicatorsData = {
  symbol: string
  scalping: IndicatorSummary[]
  swing: IndicatorSummary[]
}

type TradeSide = 'BUY' | 'SHORT' | 'HOLD'

type TradeSignal = {
  side: TradeSide
  confidence: number // 0..1
  reasons: string[]
}

type StoredSignalNotification = {
  symbol: string
  pair: string
  side: TradeSide
  confidence: number
  entryPrice: number
  takeProfit: number
  stopLoss: number
  createdAt: string
}

type TradingViewWidgetProps = {
  symbol: string
}

function trendIcon(trend: 'bullish' | 'bearish' | 'range') {
  if (trend === 'bullish') return '↑'
  if (trend === 'bearish') return '↓'
  return '↔'
}

function computeTradeSignal(
  indicators: IndicatorsData,
  sentimentLabel: string,
  sentimentScore: number,
): TradeSignal {
  const tfWeights: Record<IndicatorSummary['timeframe'], number> = {
    '5m': 0.5,
    '15m': 0.7,
    '1h': 1,
    '4h': 1.3,
    '1d': 1.5,
  }

  let bullishScore = 0
  let bearishScore = 0

  const allTfs: IndicatorSummary[] = [
    ...(indicators.scalping || []),
    ...(indicators.swing || []),
  ]

  allTfs.forEach((tf) => {
    const w = tfWeights[tf.timeframe] ?? 1

    // Bullish components
    if (tf.trend === 'bullish') bullishScore += 1 * w
    if (tf.bias === 'long') bullishScore += 1 * w
    if (tf.rsi >= 45 && tf.rsi <= 65) bullishScore += 0.5 * w
    if (tf.rsi > 70) bullishScore -= 0.5 * w // overbought risk

    // Bearish components
    if (tf.trend === 'bearish') bearishScore += 1 * w
    if (tf.bias === 'short') bearishScore += 1 * w
    if (tf.rsi >= 35 && tf.rsi <= 55) bearishScore += 0.5 * w
    if (tf.rsi < 30) bearishScore -= 0.5 * w // oversold risk
  })

  // News sentiment adjustment
  if (sentimentLabel === 'Bullish' && sentimentScore > 0.2) {
    bullishScore += 1
    bearishScore -= 0.5
  } else if (sentimentLabel === 'Bearish' && sentimentScore < -0.2) {
    bearishScore += 1
    bullishScore -= 0.5
  }

  let side: TradeSide = 'HOLD'
  let confidence = 0
  const reasons: string[] = []

  const diff = bullishScore - bearishScore

  if (bullishScore >= 3 && diff >= 2) {
    side = 'BUY'
    confidence = Math.min(1, bullishScore / 6)
  } else if (bearishScore >= 3 && -diff >= 2) {
    side = 'SHORT'
    confidence = Math.min(1, bearishScore / 6)
  } else {
    side = 'HOLD'
    confidence = Math.min(1, Math.max(bullishScore, bearishScore) / 5)
  }

  // Build human-readable reasons
  const strongBull = indicators.swing.some(
    (tf) => tf.timeframe === '4h' || tf.timeframe === '1d',
  )
    ? indicators.swing
        .filter((tf) => tf.trend === 'bullish')
        .map((tf) => tf.timeframe)
    : []

  const strongBear = indicators.swing.some(
    (tf) => tf.timeframe === '4h' || tf.timeframe === '1d',
  )
    ? indicators.swing
        .filter((tf) => tf.trend === 'bearish')
        .map((tf) => tf.timeframe)
    : []

  if (strongBull.length) {
    reasons.push(`Higher timeframes bullish trend on ${strongBull.join(', ')}.`)
  }
  if (strongBear.length) {
    reasons.push(`Higher timeframes bearish trend on ${strongBear.join(', ')}.`)
  }

  const intradayBull = indicators.scalping.filter((tf) => tf.trend === 'bullish')
  const intradayBear = indicators.scalping.filter((tf) => tf.trend === 'bearish')

  if (intradayBull.length) {
    reasons.push(
      `Intraday trend bullish on ${intradayBull
        .map((tf) => tf.timeframe)
        .join(', ')} timeframes.`,
    )
  }
  if (intradayBear.length) {
    reasons.push(
      `Intraday trend bearish on ${intradayBear
        .map((tf) => tf.timeframe)
        .join(', ')} timeframes.`,
    )
  }

  if (sentimentLabel === 'Bullish') {
    reasons.push(`News sentiment bullish (score ${sentimentScore.toFixed(2)}).`)
  } else if (sentimentLabel === 'Bearish') {
    reasons.push(`News sentiment bearish (score ${sentimentScore.toFixed(2)}).`)
  } else {
    reasons.push(`News sentiment neutral (score ${sentimentScore.toFixed(2)}).`)
  }

  if (reasons.length === 0) {
    reasons.push('No strong confluence between indicators and sentiment.')
  }

  return { side, confidence, reasons }
}

function computeRsiOverview(indicators: IndicatorsData) {
  // Prefer higher timeframes (4h, 1d) for a more stable picture
  const swingRsis = indicators.swing.map((tf) => tf.rsi)
  const scalpingRsis = indicators.scalping.map((tf) => tf.rsi)

  const values = swingRsis.length
    ? swingRsis
    : scalpingRsis.length
    ? scalpingRsis
    : []

  if (!values.length) {
    return { value: 50, label: 'Neutral' as const }
  }

  const avg = values.reduce((a, b) => a + b, 0) / values.length

  let label: 'Oversold' | 'Neutral' | 'Overbought'
  if (avg <= 35) label = 'Oversold'
  else if (avg >= 65) label = 'Overbought'
  else label = 'Neutral'

  return { value: avg, label }
}

function formatShortTime(isoString: string | null) {
  if (!isoString) return ''
  const d = new Date(isoString)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatNewsTime(dateString: string | null | undefined) {
  if (!dateString) return ''
  const d = new Date(dateString)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function TradingViewWidget({ symbol }: TradingViewWidgetProps): React.JSX.Element {
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    containerRef.current.innerHTML = ''

    const script = document.createElement('script')
    script.src =
      'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol,
      interval: '60',
      timezone: 'Etc/UTC',
      theme: 'dark',
      style: '1',
      locale: 'en',
      enable_publishing: false,
      hide_legend: false,
      hide_top_toolbar: false,
      hide_volume: false,
      withdateranges: true,
      allow_symbol_change: true,
    })

    containerRef.current.appendChild(script)
  }, [symbol])

  return (
    <div className="h-[400px] w-full rounded-2xl border border-gray-900 bg-gray-950/80">
      <div ref={containerRef} className="h-full w-full" />
    </div>
  )
}

export default function TradingDashboardPage(): React.JSX.Element {
  const [searchInput, setSearchInput] = useState('')
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT')
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)
  const router = useRouter()
  const searchParams = useSearchParams()

  const [news, setNews] = useState<NewsItem[]>([])
  const [newsLoading, setNewsLoading] = useState(false)
  const [newsError, setNewsError] = useState<string | null>(null)
  const [newsUpdatedAt, setNewsUpdatedAt] = useState<string | null>(null)
  const [newsSentimentEnabled, setNewsSentimentEnabled] = useState<boolean>(true)

  const [indicators, setIndicators] = useState<IndicatorsData | null>(null)
  const [indicatorsLoading, setIndicatorsLoading] = useState(false)
  const [indicatorsError, setIndicatorsError] = useState<string | null>(null)
  const [indicatorsUpdatedAt, setIndicatorsUpdatedAt] = useState<string | null>(null)

  const [recentSymbols, setRecentSymbols] = useState<string[]>([])

  const [activeSignal, setActiveSignal] = useState<StoredSignalNotification | null>(null)
  const [signalToastVisible, setSignalToastVisible] = useState(false)

  const sentimentNews =
    newsSentimentEnabled && news.length > 0
      ? news.filter((n) => typeof n.sentimentScore === 'number' && !Number.isNaN(n.sentimentScore))
      : []

  const sentimentAvg =
    sentimentNews.length > 0
      ? sentimentNews.reduce((sum, n) => sum + (n.sentimentScore || 0), 0) / sentimentNews.length
      : 0

  const sentimentOverallLabel =
    sentimentAvg > 0.15 ? 'Bullish' : sentimentAvg < -0.15 ? 'Bearish' : 'Neutral'

  const sentimentOverallClasses =
    sentimentOverallLabel === 'Bullish'
      ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/40'
      : sentimentOverallLabel === 'Bearish'
      ? 'bg-red-500/10 text-red-300 border-red-500/40'
      : 'bg-gray-800/70 text-gray-300 border-gray-700'

  const addRecentSymbol = (symbol: string) => {
    const upper = symbol.toUpperCase()
    setRecentSymbols((prev) => {
      const next = [upper, ...prev.filter((s) => s !== upper)]
      return next.slice(0, 5)
    })
  }

  const NOTIFICATION_STORAGE_KEY = 'pos_signal_notifications_v1'

  const persistSignalNotification = (signal: StoredSignalNotification) => {
    if (typeof window === 'undefined') return
    try {
      const raw = window.localStorage.getItem(NOTIFICATION_STORAGE_KEY)
      const existing: StoredSignalNotification[] = raw ? JSON.parse(raw) : []
      const updated = [signal, ...existing].slice(0, 20)
      window.localStorage.setItem(NOTIFICATION_STORAGE_KEY, JSON.stringify(updated))
    } catch (e) {
      console.error('persistSignalNotification error', e)
    }
  }

  // 0) Initialize symbol from ?symbol= query if provided
  useEffect(() => {
    const fromQuery = searchParams.get('symbol')
    if (!fromQuery) return

    const upper = fromQuery.toUpperCase()
    setSelectedSymbol(upper)
    addRecentSymbol(upper)
  }, [searchParams])

  // 1) Auth check
  useEffect(() => {
    if (typeof window === 'undefined') return

    const isAuth = window.localStorage.getItem('pos_is_authenticated') === 'true'

    if (!isAuth) {
      router.replace('/auth/login')
      return
    }

    setIsCheckingAuth(false)
  }, [router])

  // 1b) Load latest stored notification (if any) so user sees it even if it was generated earlier
  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      const raw = window.localStorage.getItem(NOTIFICATION_STORAGE_KEY)
      if (!raw) return

      const stored: StoredSignalNotification[] = JSON.parse(raw)
      if (!Array.isArray(stored) || stored.length === 0) return

      const latest = stored[0]
      setActiveSignal(latest)
      setSignalToastVisible(true)
    } catch (e) {
      console.error('load stored notifications error', e)
    }
  }, [])

  // 2) News loader
  useEffect(() => {
    let cancelled = false

    const loadNews = async () => {
      setNewsLoading(true)
      setNewsError(null)

      try {
        const res = await fetch(`/api/news?symbol=${encodeURIComponent(selectedSymbol)}`)
        if (!res.ok) {
          throw new Error(`Status ${res.status}`)
        }

        const data = await res.json()
        if (cancelled) return

        const items: NewsItem[] = (data.items || []).map((item: any) => ({
          id: item.id,
          title: item.title,
          source: item.source,
          url: item.url,
          publishedAt: item.publishedAt,
          sentimentLabel: item.sentimentLabel,
          sentimentScore: item.sentimentScore,
          sentimentConfidence: item.sentimentConfidence,
        }))

        setNews(items)
        setNewsSentimentEnabled(data.sentimentEnabled !== false)
        setNewsUpdatedAt(new Date().toISOString())
      } catch (e) {
        console.error('loadNews error', e)
        if (!cancelled) {
          setNewsError('Failed to load news.')
          setNews([])
        }
      } finally {
        if (!cancelled) setNewsLoading(false)
      }
    }

    loadNews()

    return () => {
      cancelled = true
    }
  }, [selectedSymbol])

  // 4) Background-style scanner for strong signals on top markets
  useEffect(() => {
    let cancelled = false
    let intervalId: number | undefined

    const scanTopMarkets = async () => {
      try {
        const res = await fetch('/api/markets/top')
        if (!res.ok) return

        const data = await res.json()
        const markets: { pair: string; price: number }[] = data.markets || []

        // Only look at first 10 entries for now
        for (const m of markets.slice(0, 10)) {
          if (cancelled) return

          const symbol = m.pair

          try {
            const indRes = await fetch(`/api/indicators?symbol=${encodeURIComponent(symbol)}`)
            if (!indRes.ok) continue

            const indData = (await indRes.json()) as IndicatorsData

            // Use neutral sentiment for background scan; dashboard view still uses real sentiment
            const trade = computeTradeSignal(indData, 'Neutral', 0)

            const isStrong = trade.side !== 'HOLD' && trade.confidence >= 0.8
            if (!isStrong) continue

            const price = Number(m.price)
            if (!Number.isFinite(price) || price <= 0) continue

            let entryPrice = price
            let takeProfit = price
            let stopLoss = price

            if (trade.side === 'BUY') {
              entryPrice = price * 0.995
              takeProfit = price * 1.02
              stopLoss = price * 0.985
            } else if (trade.side === 'SHORT') {
              entryPrice = price * 1.005
              takeProfit = price * 0.98
              stopLoss = price * 1.015
            }

            if (cancelled) return

            const storedSignal: StoredSignalNotification = {
              symbol,
              pair: symbol.replace('USDT', '/USDT'),
              side: trade.side,
              confidence: trade.confidence,
              entryPrice,
              takeProfit,
              stopLoss,
              createdAt: new Date().toISOString(),
            }

            setActiveSignal(storedSignal)
            persistSignalNotification(storedSignal)
            setSignalToastVisible(true)
            break
          } catch (e) {
            console.error('scanTopMarkets indicator error', symbol, e)
          }
        }
      } catch (e) {
        console.error('scanTopMarkets error', e)
      }
    }

    scanTopMarkets()
    intervalId = window.setInterval(scanTopMarkets, 180000) // ~3 minutes

    return () => {
      cancelled = true
      if (intervalId) window.clearInterval(intervalId)
    }
  }, [])

  // 3) Indicators loader
  useEffect(() => {
    let cancelled = false

    const loadIndicators = async () => {
      try {
        setIndicatorsLoading(true)
        setIndicatorsError(null)

        const res = await fetch(
          `/api/indicators?symbol=${encodeURIComponent(selectedSymbol)}`,
        )
        if (!res.ok) {
          throw new Error(`Status ${res.status}`)
        }

        const data = (await res.json()) as IndicatorsData
        if (cancelled) return

        setIndicators(data)
        setIndicatorsUpdatedAt(new Date().toISOString())
      } catch (e) {
        console.error('loadIndicators error', e)
        if (!cancelled) {
          setIndicatorsError('Failed to load indicators.')
          setIndicators(null)
        }
      } finally {
        if (!cancelled) setIndicatorsLoading(false)
      }
    }

    loadIndicators()

    return () => {
      cancelled = true
    }
  }, [selectedSymbol])

  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmed = searchInput.trim().toUpperCase()
    if (!trimmed) return

    const hasKnownQuote = ['USDT', 'USD', 'USDC', 'BTC', 'ETH', 'EUR', 'PERP'].some((q) =>
      trimmed.endsWith(q),
    )

    const normalized = hasKnownQuote ? trimmed : `${trimmed}USDT`
    setSelectedSymbol(normalized)
    addRecentSymbol(normalized)
  }

  if (isCheckingAuth) {
    return (
      <div className="mx-auto flex min-h-[60vh] max-w-6xl items-center justify-center px-4 py-10 text-sm text-gray-400">
        Checking access...
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <header className="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-gray-50 sm:text-3xl">
            Trading Dashboard
          </h1>
          <p className="mt-2 text-sm text-gray-500">
            Live overview of AI-generated signals, recent market activity, and strategy
            performance.
          </p>
        </div>
      </header>

      {/* TradingView chart + symbol search and Latest news side by side */}
      <section className="mb-8 grid gap-4 lg:grid-cols-[2fr,1.3fr]">
        <div>
          {/* Quick popular symbols */}
          <div className="mb-2 flex items-center gap-1 overflow-x-auto whitespace-nowrap text-[10px] text-gray-300">
            {POPULAR_SYMBOLS.map((sym) => (
              <button
                key={sym}
                type="button"
                onClick={() => {
                  setSelectedSymbol(sym)
                }}
                className={
                  'rounded-full border px-2 py-0.5 transition-colors ' +
                  (selectedSymbol === sym
                    ? 'border-emerald-500/60 bg-emerald-500/10 text-emerald-300'
                    : 'border-gray-800 bg-gray-950/60 hover:border-emerald-500/40 hover:text-emerald-200')
                }
              >
                {sym.replace('USDT', '/USDT')}
              </button>
            ))}
          </div>

          <div className="mb-3 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-sm font-semibold text-gray-100">
                {selectedSymbol} Chart
              </h2>
            </div>
            <form
              onSubmit={handleSearchSubmit}
              className="flex w-full max-w-xs flex-col gap-1.5"
            >
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Search by symbol or coin (e.g. BTC, ETH, BTCUSDT)"
                  className="w-full rounded-lg border border-gray-800 bg-gray-950 px-3 py-1.5 text-xs text-gray-200 placeholder:italic placeholder:text-gray-500 focus:border-emerald-400 focus:outline-none"
                />
                <button
                  type="submit"
                  className="rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-gray-950 hover:bg-emerald-400"
                >
                  Apply
                </button>
              </div>
              {recentSymbols.length > 0 && (
                <div className="flex flex-wrap items-center gap-1 text-[10px] text-gray-400">
                  <span className="mr-1 text-[10px] text-gray-500">
                    Recent:
                  </span>
                  {recentSymbols.map((sym) => (
                    <button
                      key={sym}
                      type="button"
                      onClick={() => {
                        setSearchInput(sym)
                        setSelectedSymbol(sym)
                      }}
                      className={
                        'rounded-full border px-2 py-0.5 text-[10px] font-medium transition-colors ' +
                        (selectedSymbol === sym
                          ? 'border-amber-400 bg-amber-300/90 text-gray-950 shadow-[0_0_4px_rgba(251,191,36,0.6)]'
                          : 'border-gray-800 bg-gray-950/60 text-gray-300 hover:border-emerald-500/40 hover:text-emerald-200')
                      }
                    >
                      {sym.replace('USDT', '/USDT')}
                    </button>
                  ))}
                </div>
              )}
            </form>
          </div>
          <TradingViewWidget symbol={selectedSymbol} />

          {/* AI Trade Signal + Average RSI side by side */}
          {indicators && (
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              {/* AI Trade Signal */}
              {(() => {
                const trade = computeTradeSignal(
                  indicators,
                  sentimentOverallLabel,
                  sentimentAvg,
                )
                const confidencePct = Math.round(trade.confidence * 100)

                let chipClasses =
                  'inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold '
                if (trade.side === 'BUY') {
                  chipClasses +=
                    'border-emerald-500/60 bg-emerald-500/10 text-emerald-300'
                } else if (trade.side === 'SHORT') {
                  chipClasses +=
                    'border-red-500/60 bg-red-500/10 text-red-300'
                } else {
                  chipClasses +=
                    'border-gray-700 bg-gray-900 text-gray-300'
                }

                const isActiveForSymbol =
                  activeSignal && activeSignal.symbol === indicators.symbol

                return (
                  <div
                    id="ai-trade-signal-card"
                    className="rounded-2xl border border-gray-900 bg-gray-950/80 p-4 text-xs"
                  >
                    <div className="mb-3 flex items-center justify-between gap-3">
                      <div>
                        <h2 className="text-sm font-semibold text-gray-100">
                          AI Trade Signal
                        </h2>
                        <p className="text-[11px] text-gray-500">
                          Combined view of multi-timeframe indicators and news sentiment.
                        </p>
                        {indicatorsUpdatedAt && (
                          <p className="mt-0.5 text-[10px] text-gray-500">
                            Updated {formatShortTime(indicatorsUpdatedAt)} (UTC)
                          </p>
                        )}
                      </div>
                      <span className={chipClasses}>{trade.side}</span>
                    </div>

                    <div className="mb-2 flex items-center justify-between text-[11px] text-gray-400">
                      <span>Confidence</span>
                      <span>{confidencePct}%</span>
                    </div>
                    <div className="mb-3 h-1.5 w-full overflow-hidden rounded-full bg-gray-900">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-emerald-500 via-emerald-400 to-emerald-300"
                        style={{ width: `${confidencePct}%` }}
                      />
                    </div>

                    {isActiveForSymbol && activeSignal && (
                      <div className="mb-3 rounded-lg border border-emerald-700/70 bg-emerald-500/5 px-3 py-2 text-[11px] text-gray-100">
                        <div className="mb-1 flex items-center justify-between">
                          <span className="font-semibold">Suggested plan</span>
                          <span className="font-mono text-[10px] text-emerald-300">
                            from background scan
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-[11px]">
                          <div>
                            <div className="text-[10px] text-gray-400">Entry</div>
                            <div className="font-mono text-xs">
                              {activeSignal.entryPrice.toFixed(4)}
                            </div>
                          </div>
                          <div>
                            <div className="text-[10px] text-gray-400">Take profit</div>
                            <div className="font-mono text-xs text-emerald-300">
                              {activeSignal.takeProfit.toFixed(4)}
                            </div>
                          </div>
                          <div>
                            <div className="text-[10px] text-gray-400">Stop loss</div>
                            <div className="font-mono text-xs text-red-300">
                              {activeSignal.stopLoss.toFixed(4)}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    <ul className="space-y-1 text-[11px] text-gray-400">
                      {trade.reasons.map((reason, idx) => (
                        <li key={idx} className="flex gap-1.5">
                          <span className="mt-[3px] h-1 w-1 shrink-0 rounded-full bg-gray-500" />
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )
              })()}

              {/* Average RSI overview */}
              {(() => {
            const { value, label } = computeRsiOverview(indicators)
            const rsiRounded = value.toFixed(1)

            let gradientClass =
              'bg-gradient-to-r from-emerald-500 via-yellow-400 to-red-500'

            // Pointer color: greener for Oversold (left), red for Overbought (right)
            let pointerColor = 'bg-emerald-400'
            if (label === 'Oversold') pointerColor = 'bg-emerald-500'
            else if (label === 'Overbought') pointerColor = 'bg-red-400'

            let valueColor = 'text-gray-50'
            let labelColor = 'text-gray-400'
            if (label === 'Oversold') {
              // Oversold: show as green (matches left side of gradient)
              valueColor = 'text-emerald-400'
              labelColor = 'text-emerald-400'
            } else if (label === 'Overbought') {
              // Overbought: show as red (matches right side of gradient)
              valueColor = 'text-red-400'
              labelColor = 'text-red-400'
            }

            const position = Math.min(100, Math.max(0, ((value - 10) / 80) * 100))

            return (
              <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-4 text-xs">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-sm font-semibold text-gray-100">
                      Average Crypto RSI
                    </h2>
                    <p className="text-[11px] text-gray-500">
                      Based on current multi-timeframe RSI.
                    </p>
                    {indicatorsUpdatedAt && (
                      <p className="mt-0.5 text-[10px] text-gray-500">
                        Updated {formatShortTime(indicatorsUpdatedAt)} (UTC)
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className={"text-base font-semibold " + valueColor}>
                      {rsiRounded}
                    </div>
                    <div className={"text-[11px] " + labelColor}>{label}</div>
                  </div>
                </div>

                <div className="mb-1 flex justify-between text-[10px] text-gray-500">
                  <span>Oversold</span>
                  <span>Overbought</span>
                </div>
                <div className="relative h-2 w-full overflow-visible rounded-full bg-gray-900">
                  <div className={"h-full w-full opacity-80 " + gradientClass} />
                  {/* Vertical pointer line */}
                  <div
                    className={
                      'absolute top-[-4px] h-[18px] w-[4px] rounded-full shadow-[0_0_6px_rgba(0,0,0,0.6)] ' +
                      pointerColor
                    }
                    style={{ left: `${position}%`, transform: 'translateX(-50%)' }}
                  />
                </div>
              </div>
            )
          })()}

            </div>
          )}

          {/* Algo Signals */}
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {/* Scalping Algo Signals */}
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80">
              <div className="flex items-center justify-between border-b border-gray-900 px-4 py-3">
                <div>
                  <h2 className="text-sm font-semibold text-gray-100">
                    Scalping Algo Signals
                  </h2>
                  <p className="mt-0.5 text-[11px] text-gray-500">
                    Short-term intraday view using EMA20/50 and RSI14 on 5m, 15m and 1h timeframes.
                  </p>
                </div>
                {indicatorsUpdatedAt && (
                  <span className="text-[10px] text-gray-500">
                    {formatShortTime(indicatorsUpdatedAt)} UTC
                  </span>
                )}
                {indicatorsLoading && (
                  <span className="text-[11px] text-gray-500">Loading…</span>
                )}
              </div>

              {indicatorsError && (
                <div className="px-4 py-2 text-xs text-red-400">
                  {indicatorsError}
                </div>
              )}

              <div className="divide-y divide-gray-900 text-xs">
                {indicators?.scalping.map((tf) => (
                  <div key={tf.timeframe} className="px-4 py-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] uppercase tracking-wide text-gray-500">
                        {tf.timeframe}
                      </span>
                      <div className="flex items-center gap-2">
                        <span
                          className={
                            'inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ' +
                            (tf.trend === 'bullish'
                              ? 'bg-emerald-500/10 text-emerald-300'
                              : tf.trend === 'bearish'
                              ? 'bg-red-500/10 text-red-300'
                              : 'bg-gray-700/40 text-gray-300')
                          }
                        >
                          <span className="mr-1 text-[11px]">
                            {trendIcon(tf.trend)}
                          </span>
                          <span className="capitalize">{tf.trend}</span>
                        </span>
                        <span className="rounded-full bg-gray-900 px-2 py-0.5 text-[10px] text-gray-300">
                          RSI {tf.rsi.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <p className="mt-1 text-[11px] text-gray-400">{tf.note}</p>
                  </div>
                ))}

                {!indicatorsLoading && indicators?.scalping.length === 0 && (
                  <div className="px-4 py-3 text-[11px] text-gray-500">
                    No scalping signals available.
                  </div>
                )}
              </div>
            </div>

            {/* Swing / Daytrading Algo Signals */}
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80">
              <div className="flex items-center justify-between border-b border-gray-900 px-4 py-3">
                <div>
                  <h2 className="text-sm font-semibold text-gray-100">
                    Swing / Daytrading Algo Signals
                  </h2>
                  <p className="mt-0.5 text-[11px] text-gray-500">
                    Medium-term trend view on 4h and 1D using EMA20/50, RSI14 and our AI signal engine.
                  </p>
                </div>
                {indicatorsUpdatedAt && (
                  <span className="text-[10px] text-gray-500">
                    {formatShortTime(indicatorsUpdatedAt)} UTC
                  </span>
                )}
              </div>

              <div className="divide-y divide-gray-900 text-xs">
                {indicators?.swing.map((tf) => (
                  <div key={tf.timeframe} className="px-4 py-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] uppercase tracking-wide text-gray-500">
                        {tf.timeframe}
                      </span>
                      <div className="flex items-center gap-2">
                        <span
                          className={
                            'inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ' +
                            (tf.trend === 'bullish'
                              ? 'bg-emerald-500/10 text-emerald-300'
                              : tf.trend === 'bearish'
                              ? 'bg-red-500/10 text-red-300'
                              : 'bg-gray-700/40 text-gray-300')
                          }
                        >
                          <span className="mr-1 text-[11px]">
                            {trendIcon(tf.trend)}
                          </span>
                          <span className="capitalize">{tf.trend}</span>
                        </span>
                        <span className="rounded-full bg-gray-900 px-2 py-0.5 text-[10px] text-gray-300">
                          RSI {tf.rsi.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <p className="mt-1 text-[11px] text-gray-400">{tf.note}</p>
                  </div>
                ))}

                {!indicatorsLoading && indicators?.swing.length === 0 && (
                  <div className="px-4 py-3 text-[11px] text-gray-500">
                    No swing/daytrading signals available.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="flex h-[470px] flex-col rounded-2xl border border-gray-900 bg-gray-950/80">
          <div className="flex items-center justify-between border-b border-gray-900 px-4 py-3">
            <div>
              <h2 className="text-sm font-semibold text-gray-100">Latest News</h2>
              <p className="mt-1 text-[11px] text-gray-500">
                Overall score is an average FinBERT sentiment from −1 (very
                bearish) to +1 (very bullish).
              </p>
              {newsUpdatedAt && (
                <p className="mt-0.5 text-[10px] text-gray-500">
                  Updated {formatShortTime(newsUpdatedAt)} (UTC)
                </p>
              )}
            </div>

            {newsSentimentEnabled && sentimentNews.length > 0 && (
              <span
                className={
                  'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold ' +
                  sentimentOverallClasses
                }
              >
                <span>Overall:</span>
                <span className="capitalize">{sentimentOverallLabel.toLowerCase()}</span>
                <span className="font-mono tabular-nums text-[11px]">
                  {Number.isFinite(sentimentAvg) ? sentimentAvg.toFixed(2) : ''}
                </span>
              </span>
            )}
          </div>

          <div className="flex-1 divide-y divide-gray-900 overflow-y-auto">
            {newsLoading && (
              <div className="px-4 py-3 text-xs text-gray-500">Loading news…</div>
            )}

            {newsError && !newsLoading && (
              <div className="px-4 py-3 text-xs text-red-300">{newsError}</div>
            )}

            {!newsLoading && !newsError && news.length === 0 && (
              <div className="px-4 py-3 text-xs text-gray-500">
                No recent news found for this asset.
              </div>
            )}

            {news.map((item) => (
              <article
                key={item.id}
                className="px-4 py-3 text-xs transition-colors hover:bg-gray-900/60"
              >
                <div className="space-y-1.5">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="block text-gray-100 hover:text-emerald-300 line-clamp-2"
                  >
                    {item.title}
                  </a>

                  <div className="flex items-center justify-between text-[11px] text-gray-500">
                    <span className="truncate">{item.source}</span>
                    <span className="ml-2 shrink-0 font-mono tabular-nums text-[10px] text-gray-500">
                      {formatNewsTime(item.publishedAt)}
                    </span>
                  </div>

                  {newsSentimentEnabled && item.sentimentLabel && (
                    <div className="flex items-center justify-between pt-1 border-t border-gray-900/80">
                      <span
                        className={
                          'inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ' +
                          (item.sentimentLabel === 'positive'
                            ? 'bg-emerald-500/10 text-emerald-300'
                            : item.sentimentLabel === 'negative'
                            ? 'bg-red-500/10 text-red-300'
                            : 'bg-gray-800/70 text-gray-300')
                        }
                      >
                        <span className="mr-1 h-1.5 w-1.5 rounded-full bg-current" />
                        <span className="capitalize">{item.sentimentLabel}</span>
                        {typeof item.sentimentScore === 'number' && (
                          <span className="ml-1 font-mono tabular-nums text-[10px]">
                            {item.sentimentScore.toFixed(2)}
                          </span>
                        )}
                      </span>
                    </div>
                  )}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Signals table */}
      {/* keep your existing signals table section below unchanged */}
    </div>
  )
}