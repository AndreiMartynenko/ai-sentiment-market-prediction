import { NextResponse } from 'next/server'

const TWELVEDATA_API_KEY = process.env.TWELVEDATA_API_KEY
const API_NINJAS_API_KEY = process.env.API_NINJAS_API_KEY

if (!TWELVEDATA_API_KEY) {
  console.warn('TWELVEDATA_API_KEY is not set. /api/global/overview will return an error.')
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

  // API Ninjas stockprice API does not provide percent change directly in docs; set 0 for now.
  const changePercent = 0

  return {
    symbol: displaySymbol,
    name: displayName,
    price,
    changePercent,
  }
}

export async function GET() {
  if (!TWELVEDATA_API_KEY) {
    return NextResponse.json(
      { error: 'TWELVEDATA_API_KEY is not configured on the server.' },
      { status: 500 },
    )
  }

  try {
    // Gold via Twelve Data
    const twelveQuotes = await Promise.all([
      fetchQuote('XAU/USD', 'XAUUSD', 'Gold (XAUUSD)'),
    ])
    const assets: GlobalAsset[] = twelveQuotes.filter((q): q is GlobalAsset => q !== null)

    // Indices via API Ninjas if available
    if (API_NINJAS_API_KEY) {
      const ninjasQuotes = await Promise.all([
        fetchNinjasIndex('^GSPC', 'US500', 'S&P 500'),
        fetchNinjasIndex('^IXIC', 'NAS100', 'Nasdaq 100'),
        fetchNinjasIndex('^DJI', 'US30', 'Dow Jones 30'),
      ])
      for (const q of ninjasQuotes) {
        if (q) assets.push(q)
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
