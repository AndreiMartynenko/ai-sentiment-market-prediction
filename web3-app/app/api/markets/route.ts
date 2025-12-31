import { NextResponse } from 'next/server'

// Simple Binance 24h ticker client for a few core symbols
const BINANCE_BASE = 'https://api.binance.com'
const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'] as const

export const dynamic = 'force-dynamic'

type SymbolInfo = {
  symbol: string
  coin: string
  name: string
}

const SYMBOL_META: Record<(typeof SYMBOLS)[number], SymbolInfo> = {
  BTCUSDT: { symbol: 'BTCUSDT', coin: 'BTC', name: 'Bitcoin' },
  ETHUSDT: { symbol: 'ETHUSDT', coin: 'ETH', name: 'Ethereum' },
  SOLUSDT: { symbol: 'SOL', coin: 'SOL', name: 'Solana' },
  BNBUSDT: { symbol: 'BNBUSDT', coin: 'BNB', name: 'Binance Coin' },
}

export async function GET() {
  try {
    const results = await Promise.all(
      SYMBOLS.map(async (symbol) => {
        const url = `${BINANCE_BASE}/api/v3/ticker/24hr?symbol=${symbol}`
        const res = await fetch(url, { cache: 'no-store' })

        if (!res.ok) {
          throw new Error(`Binance error ${res.status} for ${symbol}`)
        }

        const data = (await res.json()) as any
        const meta = SYMBOL_META[symbol]

        const lastPrice = Number(data.lastPrice)
        const priceChangePercent = Number(data.priceChangePercent)
        const quoteVolume = Number(data.quoteVolume)

        return {
          symbol: meta.symbol,
          coin: meta.coin,
          name: meta.name,
          price: lastPrice,
          changePercent: priceChangePercent,
          volumeQuote: quoteVolume,
        }
      }),
    )

    return NextResponse.json({ markets: results })
  } catch (err) {
    console.error('Failed to fetch Binance market snapshot', err)
    return NextResponse.json({ error: 'Failed to load market snapshot.' }, { status: 502 })
  }
}
