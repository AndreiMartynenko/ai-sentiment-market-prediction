import { NextResponse } from 'next/server'

const GO_BACKEND_URL = process.env.GO_BACKEND_URL || 'http://localhost:8080'

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const symbol = (searchParams.get('symbol') || '').trim().toUpperCase()

    if (!symbol) {
      return NextResponse.json({ error: 'Missing symbol' }, { status: 400 })
    }

    const res = await fetch(`${GO_BACKEND_URL}/api/v1/price?symbol=${encodeURIComponent(symbol)}`, { cache: 'no-store' })

    if (!res.ok) {
      return NextResponse.json(
        { error: `Binance error ${res.status}` },
        { status: 502 },
      )
    }

    const data = (await res.json()) as any
    return NextResponse.json(data)
  } catch (err) {
    console.error('Failed to fetch price', err)
    return NextResponse.json({ error: 'Failed to fetch price' }, { status: 502 })
  }
}
