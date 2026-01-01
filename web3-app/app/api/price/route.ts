import { NextResponse } from 'next/server'

const GO_BACKEND_URL = process.env.GO_BACKEND_URL || 'http://localhost:8080'
const BINANCE_BASE = 'https://data-api.binance.vision'

export const dynamic = 'force-dynamic'

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const symbol = (searchParams.get('symbol') || '').trim().toUpperCase()

    if (!symbol) {
      return NextResponse.json({ error: 'Missing symbol' }, { status: 400 })
    }

    try {
      const res = await fetch(
        `${GO_BACKEND_URL}/api/v1/price?symbol=${encodeURIComponent(symbol)}`,
        { cache: 'no-store' },
      )

      if (res.ok) {
        const data = (await res.json()) as any
        return NextResponse.json(data)
      }
    } catch (e) {
      console.error('Go backend price fetch failed, falling back to Binance', e)
    }

    const fallbackRes = await fetch(
      `${BINANCE_BASE}/api/v3/ticker/price?symbol=${encodeURIComponent(symbol)}`,
      { cache: 'no-store' },
    )

    if (!fallbackRes.ok) {
      return NextResponse.json(
        { error: `Binance error ${fallbackRes.status}` },
        { status: 502 },
      )
    }

    const fallbackData = (await fallbackRes.json()) as any
    const price = Number(fallbackData?.price)
    if (!Number.isFinite(price)) {
      return NextResponse.json({ error: 'Invalid price from Binance' }, { status: 502 })
    }

    return NextResponse.json({ price })
  } catch (err) {
    console.error('Failed to fetch price', err)
    return NextResponse.json({ error: 'Failed to fetch price' }, { status: 502 })
  }
}
