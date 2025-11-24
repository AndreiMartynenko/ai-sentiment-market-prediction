import { NextResponse } from 'next/server'

const BINANCE_BASE = 'https://api.binance.com'

export async function GET() {
  try {
    const res = await fetch(`${BINANCE_BASE}/api/v3/ticker/24hr`, {
      cache: 'no-store',
    })

    if (!res.ok) {
      throw new Error(`Binance 24hr ticker error ${res.status}`)
    }

    const all = (await res.json()) as any[]

    // Filter for liquid USDT pairs, skip leveraged / weird tokens
    const usdtMarkets = all.filter((t) => {
      const s = String(t.symbol)
      return (
        s.endsWith('USDT') &&
        !s.includes('UPUSDT') &&
        !s.includes('DOWNUSDT') &&
        !s.includes('BULLUSDT') &&
        !s.includes('BEARUSDT')
      )
    })

    // Sort by quote volume (largest first)
    usdtMarkets.sort((a, b) => Number(b.quoteVolume) - Number(a.quoteVolume))

    const top = usdtMarkets.slice(0, 100)

    const markets = top.map((t) => {
      const symbol: string = t.symbol
      const base = symbol.replace(/USDT$/, '')

      return {
        coin: base,
        pair: symbol,
        name: base, // can be improved with a metadata map later
        price: Number(t.lastPrice),
        changePercent: Number(t.priceChangePercent),
        volumeQuote: Number(t.quoteVolume),
        highPrice: Number(t.highPrice),
        lowPrice: Number(t.lowPrice),
      }
    })

    return NextResponse.json({ markets })
  } catch (err) {
    console.error('Failed to fetch top Binance markets', err)
    return NextResponse.json(
      { error: 'Failed to load market overview.' },
      { status: 502 },
    )
  }
}
