import { NextResponse } from 'next/server'

const NEWS_API_KEY = process.env.NEWS_API_KEY
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000'

export const dynamic = 'force-dynamic'

// Only compute detailed sentiment for a curated set of majors.
const TOP_SENTIMENT_BASES = new Set([
  'BTC',
  'ETH',
  'SOL',
  'BNB',
  'XRP',
  'ADA',
  'DOGE',
  'TON',
  'LINK',
  'AVAX',
])

function symbolToKeyword(symbol: string): string {
  const base = symbol.replace(/(USDT|USD|USDC|BTC|ETH|EUR|PERP)$/i, '') || 'BTC'

  const map: Record<string, string> = {
    BTC: 'bitcoin',
    ETH: 'ethereum',
    SOL: 'solana',
    BNB: 'binance coin',
  }

  return map[base] || base
}

async function fetchWithTimeout(
  input: RequestInfo,
  init: RequestInit & { timeoutMs?: number } = {},
): Promise<Response> {
  const { timeoutMs = 8000, ...rest } = init

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)

  try {
    return await fetch(input, { ...rest, signal: controller.signal })
  } finally {
    clearTimeout(timeout)
  }
}

async function getSentimentForText(symbol: string, text: string) {
  // Render can cold-start; do a couple quick retries.
  let lastError: unknown = null
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await fetchWithTimeout(`${ML_SERVICE_URL}/sentiment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, text }),
        timeoutMs: 12000,
      })

      if (!res.ok) {
        throw new Error(`ML service status ${res.status}`)
      }

      const sentiment = (await res.json()) as any
      return {
        sentimentLabel: sentiment.label as string,
        sentimentScore: sentiment.sentiment_score as number,
        sentimentConfidence: sentiment.confidence as number,
      }
    } catch (e) {
      lastError = e
      // tiny backoff: 250ms, 500ms
      if (attempt < 2) await new Promise((r) => setTimeout(r, 250 * (attempt + 1)))
    }
  }
  throw lastError
}

async function mapWithConcurrency<T, R>(
  items: T[],
  concurrency: number,
  mapper: (item: T, index: number) => Promise<R>,
): Promise<R[]> {
  const results: R[] = new Array(items.length)
  let nextIndex = 0

  async function worker() {
    while (true) {
      const idx = nextIndex
      nextIndex += 1
      if (idx >= items.length) return
      results[idx] = await mapper(items[idx], idx)
    }
  }

  const workers = Array.from({ length: Math.max(1, concurrency) }, () => worker())
  await Promise.all(workers)
  return results
}

export async function GET(req: Request) {
  if (!NEWS_API_KEY) {
    return NextResponse.json({
      items: [],
      sentimentEnabled: false,
      warning: 'NEWS_API_KEY is not configured on the server.',
    })
  }

  const { searchParams } = new URL(req.url)
  const symbol = searchParams.get('symbol') || 'BTCUSDT'
  const base = symbol.replace(/(USDT|USD|USDC|BTC|ETH|EUR|PERP)$/i, '') || 'BTC'
  const keyword = symbolToKeyword(symbol)

  const shouldAnalyzeSentiment = TOP_SENTIMENT_BASES.has(base.toUpperCase())

  const url = new URL('https://newsapi.org/v2/everything')
  url.searchParams.set('q', keyword)
  url.searchParams.set('language', 'en')
  url.searchParams.set('sortBy', 'publishedAt')
  url.searchParams.set('pageSize', '10')

  const res = await fetch(url.toString(), {
    headers: {
      'X-Api-Key': NEWS_API_KEY,
    },
    cache: 'no-store',
  })

  if (!res.ok) {
    const text = await res.text()
    console.error('NewsAPI error', res.status, text)
    return NextResponse.json(
      { error: 'Failed to load news from NewsAPI.' },
      { status: 502 },
    )
  }

  const data = await res.json()

  const baseItems = (data.articles || []).map((a: any, idx: number) => ({
    id: a.url || String(idx),
    title: a.title as string,
    description: (a.description as string) || '',
    source: a.source?.name ?? 'Unknown',
    url: a.url as string,
    publishedAt: a.publishedAt as string,
  }))

  // If symbol is outside the top majors, return plain news without sentiment.
  if (!shouldAnalyzeSentiment) {
    return NextResponse.json({
      items: baseItems,
      sentimentEnabled: false,
    })
  }

  // Call FinBERT ML service for each title (optionally title + description)
  const enrichedItems = await mapWithConcurrency(
    baseItems,
    2,
    async (item: any) => {
      try {
        const s = await getSentimentForText(symbol, item.title || item.description)
        return { ...item, ...s }
      } catch (e) {
        console.error('ML sentiment error for news item', item.title, e)
        return {
          ...item,
          sentimentLabel: 'neutral',
          sentimentScore: 0,
          sentimentConfidence: 0,
        }
      }
    },
  )

  return NextResponse.json({ items: enrichedItems, sentimentEnabled: true })
}