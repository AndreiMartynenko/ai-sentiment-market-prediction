import { NextResponse } from 'next/server'

const GO_BACKEND_URL = process.env.GO_BACKEND_URL || 'http://localhost:8080'

export const dynamic = 'force-dynamic'

type Timeframe = '5m' | '15m' | '1h' | '4h' | '1d'

type IndicatorSummary = {
  timeframe: Timeframe
  trend: 'bullish' | 'bearish' | 'range'
  rsi: number
  bias: 'long' | 'short' | 'neutral'
  note: string
}

type IndicatorsResponse = {
  symbol: string
  scalping: IndicatorSummary[]
  swing: IndicatorSummary[]
}

// --- Binance fetch helpers ---

async function fetchKlines(symbol: string, interval: Timeframe, limit = 200) {
  const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`

  const res = await fetch(url, { next: { revalidate: 30 } })
  if (!res.ok) {
    throw new Error(`Binance error ${res.status}`)
  }

  // each kline: [openTime, open, high, low, close, volume, ...]
  const data = (await res.json()) as any[]
  return data.map((k) => ({
    openTime: k[0] as number,
    open: parseFloat(k[1]),
    high: parseFloat(k[2]),
    low: parseFloat(k[3]),
    close: parseFloat(k[4]),
    volume: parseFloat(k[5]),
  }))
}

// --- Indicator math ---

function ema(values: number[], period: number): number[] {
  const k = 2 / (period + 1)
  const result: number[] = []
  let prevEma: number | null = null

  values.forEach((v, i) => {
    if (i === 0) {
      prevEma = v
    } else if (prevEma != null) {
      prevEma = v * k + prevEma * (1 - k)
    }
    result.push(prevEma ?? v)
  })

  return result
}

function rsi(values: number[], period = 14): number[] {
  const result: number[] = []
  if (values.length <= period) {
    return values.map(() => 50) // fallback neutral
  }

  let gains = 0
  let losses = 0

  for (let i = 1; i <= period; i++) {
    const change = values[i] - values[i - 1]
    if (change >= 0) gains += change
    else losses -= change
  }

  let avgGain = gains / period
  let avgLoss = losses / period

  const firstRS = avgLoss === 0 ? 100 : avgGain / avgLoss
  result[period] = 100 - 100 / (1 + firstRS)

  for (let i = period + 1; i < values.length; i++) {
    const change = values[i] - values[i - 1]
    const gain = change > 0 ? change : 0
    const loss = change < 0 ? -change : 0

    avgGain = (avgGain * (period - 1) + gain) / period
    avgLoss = (avgLoss * (period - 1) + loss) / period

    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss
    result[i] = 100 - 100 / (1 + rs)
  }

  // fill undefined at start with neutral
  for (let i = 0; i < period; i++) {
    result[i] = 50
  }

  return result
}

function summarize(
  timeframe: Timeframe,
  closes: number[],
): IndicatorSummary | null {
  if (closes.length < 50) return null

  const ema20 = ema(closes, 20)
  const ema50 = ema(closes, 50)
  const rsi14 = rsi(closes, 14)

  const lastClose = closes[closes.length - 1]
  const lastEma20 = ema20[ema20.length - 1]
  const lastEma50 = ema50[ema50.length - 1]
  const lastRsi = rsi14[rsi14.length - 1]

  let trend: IndicatorSummary['trend'] = 'range'
  if (lastClose > lastEma20 && lastEma20 > lastEma50) trend = 'bullish'
  else if (lastClose < lastEma20 && lastEma20 < lastEma50) trend = 'bearish'

  let bias: IndicatorSummary['bias'] = 'neutral'
  let note = ''

  if (trend === 'bullish') {
    if (lastRsi > 70) {
      bias = 'long'
      note =
        'Bullish trend but overbought – momentum strong, risk of pullback.'
    } else if (lastRsi >= 50) {
      bias = 'long'
      note = 'Bullish trend, RSI supportive – pullback long setups.'
    } else {
      bias = 'neutral'
      note = 'Bullish trend, but RSI has cooled – wait for confirmation.'
    }
  } else if (trend === 'bearish') {
    if (lastRsi < 30) {
      bias = 'short'
      note = 'Bearish trend but oversold – risk of short squeeze.'
    } else if (lastRsi <= 50) {
      bias = 'short'
      note = 'Bearish trend, RSI supportive – bounce short setups.'
    } else {
      bias = 'neutral'
      note = 'Bearish trend, but RSI has recovered – wait for confirmation.'
    }
  } else {
    bias = 'neutral'
    if (lastRsi > 60) {
      note = 'Range with bullish skew – breakouts possible.'
    } else if (lastRsi < 40) {
      note = 'Range with bearish skew – breakdowns possible.'
    } else {
      note = 'No strong directional edge – range conditions.'
    }
  }

  return {
    timeframe,
    trend,
    rsi: Math.round(lastRsi * 10) / 10,
    bias,
    note,
  }
}

// --- Route handler ---

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const symbol = searchParams.get('symbol') || 'BTCUSDT'

    const res = await fetch(`${GO_BACKEND_URL}/api/v1/indicators?symbol=${encodeURIComponent(symbol)}`, {
      cache: 'no-store',
    })
    const text = await res.text()
    if (!res.ok) {
      return NextResponse.json({ error: 'Gateway request failed', status: res.status, body: text }, { status: 502 })
    }
    return new NextResponse(text, { status: 200, headers: { 'Content-Type': 'application/json' } })
  } catch (e: any) {
    console.error('Indicators API error:', e)
    return NextResponse.json(
      { error: 'Failed to compute indicators' },
      { status: 500 },
    )
  }
}