import { NextResponse } from 'next/server'

const TWELVEDATA_API_KEY = process.env.TWELVEDATA_API_KEY
const API_NINJAS_API_KEY = process.env.API_NINJAS_API_KEY

export const dynamic = 'force-dynamic'

// Session-scoped baseline prices for indices to compute recent percent change
const ninjasIndexBaselines = new Map<string, number>()

if (!TWELVEDATA_API_KEY) {
  console.warn('TWELVEDATA_API_KEY is not set. /api/global/overview will return an error.')
}

async function fetchStooqQuote(
  ticker: string,
  displaySymbol: string,
  displayName: string,
): Promise<GlobalAsset | null> {
  try {
    const url = `https://stooq.com/q/l/?s=${encodeURIComponent(ticker)}&f=sd2t2ohlcv&h&e=csv`
    const res = await fetch(url, { cache: 'no-store' })
    if (!res.ok) {
      console.error('Stooq HTTP error', ticker, res.status)
      return null
    }

    const text = await res.text()
    const lines = text.trim().split(/\r?\n/)
    if (lines.length < 2) return null

    const headers = lines[0].split(',').map((h) => h.trim().toLowerCase())
    const values = lines[1].split(',').map((v) => v.trim())
    const idx = (name: string) => headers.indexOf(name)

    const open = Number(values[idx('open')])
    const close = Number(values[idx('close')])

    const price = Number.isFinite(close) ? close : Number(values[idx('last')])
    if (!Number.isFinite(price)) return null

    let changePercent = 0
    if (Number.isFinite(open) && open > 0) {
      changePercent = ((price - open) / open) * 100
    }

    return {
      symbol: displaySymbol,
      name: displayName,
      price,
      changePercent,
    }
  } catch (e) {
    console.error('Stooq fetch failed', ticker, e)
    return null
  }
}

type GlobalAsset = {
  symbol: string
  name: string
  price: number
  changePercent: number
}

async function fetchQuote(
  providerSymbol: string,
  displaySymbol: string,
  displayName: string,
): Promise<GlobalAsset | null> {
  if (!TWELVEDATA_API_KEY) return null

  const url = `https://api.twelvedata.com/quote?symbol=${encodeURIComponent(
    providerSymbol,
  )}&apikey=${TWELVEDATA_API_KEY}`

  const res = await fetch(url, { cache: 'no-store' })
  if (!res.ok) {
    console.error('Twelve Data quote HTTP error', providerSymbol, res.status)
    return null
  }

  const data = await res.json()

  // Handle Twelve Data error shape: { code, message }
  if (data && typeof data === 'object' && (data.code || data.message) && !data.price) {
    console.error('Twelve Data error for', providerSymbol, data)
    return null
  }

  const priceRaw = data.price ?? data.close
  const pctRaw = data.percent_change ?? data.change_percent

  const price = Number(priceRaw)
  const changePct = Number(pctRaw)
  if (!Number.isFinite(price)) return null

  return {
    symbol: displaySymbol,
    name: displayName,
    price,
    changePercent: Number.isFinite(changePct) ? changePct : 0,
  }
}

async function fetchNinjasIndex(
  ticker: string,
  displaySymbol: string,
  displayName: string,
): Promise<GlobalAsset | null> {
  if (!API_NINJAS_API_KEY) return null

  const url = `https://api.api-ninjas.com/v1/stockprice?ticker=${encodeURIComponent(ticker)}`

  const res = await fetch(url, {
    cache: 'no-store',
    headers: {
      'X-Api-Key': API_NINJAS_API_KEY,
    },
  })

  if (!res.ok) {
    console.error('API Ninjas index HTTP error', ticker, res.status)
    return null
  }

  const data = await res.json()

  if (!data || typeof data !== 'object') {
    console.error('API Ninjas index unexpected response', ticker, data)
    return null
  }

  const price = Number(data.price)
  if (!Number.isFinite(price)) return null

  // API Ninjas stockprice API does not provide 24h percent change.
  // Compute a session-based change relative to the first price seen for this ticker
  let changePercent = 0
  const baseline = ninjasIndexBaselines.get(ticker)
  if (baseline === undefined) {
    ninjasIndexBaselines.set(ticker, price)
  } else if (baseline > 0) {
    changePercent = ((price - baseline) / baseline) * 100
  }

  return {
    symbol: displaySymbol,
    name: displayName,
    price,
    changePercent,
  }
}

export async function GET() {
  try {
    const assets: GlobalAsset[] = []

    // Prefer Twelve Data for gold when configured
    if (TWELVEDATA_API_KEY) {
      const twelveQuotes = await Promise.all([
        fetchQuote('XAU/USD', 'XAUUSD', 'Gold (XAUUSD)'),
      ])
      for (const q of twelveQuotes) {
        if (q) assets.push(q)
      }
    }

    // Fallback: Stooq (free) for gold + indices
    // Note: Stooq tickers may vary by exchange; these cover common US indices.
    const stooqQuotes = await Promise.all([
      fetchStooqQuote('xauusd', 'XAUUSD', 'Gold (XAUUSD)'),
      fetchStooqQuote('^spx', 'US500', 'S&P 500'),
      fetchStooqQuote('^ndx', 'NAS100', 'Nasdaq 100'),
      fetchStooqQuote('^dji', 'US30', 'Dow Jones 30'),
    ])
    for (const q of stooqQuotes) {
      if (q && !assets.some((a) => a.symbol === q.symbol)) assets.push(q)
    }

    // Indices via API Ninjas if available
    if (API_NINJAS_API_KEY) {
      const ninjasQuotes = await Promise.all([
        fetchNinjasIndex('^GSPC', 'US500', 'S&P 500'),
        fetchNinjasIndex('^IXIC', 'NAS100', 'Nasdaq 100'),
        fetchNinjasIndex('^DJI', 'US30', 'Dow Jones 30'),
      ])
      for (const q of ninjasQuotes) {
        if (q && !assets.some((a) => a.symbol === q.symbol)) assets.push(q)
      }
    }

    if (assets.length === 0) {
      return NextResponse.json(
        { error: 'No macro assets could be fetched from providers.' },
        { status: 502 },
      )
    }

    return NextResponse.json({ assets })
  } catch (err) {
    console.error('Failed to fetch global overview from providers', err)
    return NextResponse.json(
      { error: 'Failed to load global overview.' },
      { status: 502 },
    )
  }
}
