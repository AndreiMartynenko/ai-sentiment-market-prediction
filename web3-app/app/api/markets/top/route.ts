import { NextResponse } from 'next/server'

const BINANCE_BASE = 'https://data-api.binance.vision'

export const dynamic = 'force-dynamic'

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

    // Only keep markets where we have an exact icon configured for the base asset
    const ICON_BASES = new Set([
      'BTC',
      'ETH',
      'USDT',
      'XRP',
      'BNB',
      'USDC',
      'SOL',
      'TRX',
      'DOGE',
      'ADA',
      'TON',
      'DOT',
      'LINK',
      'LTC',
      'AVAX',
      'UNI',
    ])

    const iconMarkets = usdtMarkets.filter((t) => {
      const symbol: string = t.symbol
      const base = symbol.replace(/USDT$/, '')
      return ICON_BASES.has(base)
    })

    // Sort by quote volume (largest first) and keep only top 10 among icon-backed markets
    iconMarkets.sort((a, b) => Number(b.quoteVolume) - Number(a.quoteVolume))

    const top = iconMarkets.slice(0, 10)

    // Compute top gainers/losers (top 3 each) across all USDT markets by 24h percent change
    const sortedByChangeDesc = [...usdtMarkets].sort(
      (a, b) => Number(b.priceChangePercent) - Number(a.priceChangePercent),
    )
    const sortedByChangeAsc = [...usdtMarkets].sort(
      (a, b) => Number(a.priceChangePercent) - Number(b.priceChangePercent),
    )

    const topGainersRaw = sortedByChangeDesc.slice(0, 3)
    const topLosersRaw = sortedByChangeAsc.slice(0, 3)

    const mapTicker = async (t: any) => {
      const symbol: string = t.symbol
      const base = symbol.replace(/USDT$/, '')

      let sparkline: number[] = []
      try {
        const klinesRes = await fetch(
          `${BINANCE_BASE}/api/v3/klines?symbol=${symbol}&interval=1d&limit=7`,
          { cache: 'no-store' },
        )

        if (klinesRes.ok) {
          const klines = (await klinesRes.json()) as any[]
          // Each kline: [openTime, open, high, low, close, ...]
          sparkline = klines.map((k) => Number(k[4])).filter((v) => Number.isFinite(v))
        }
      } catch (e) {
        console.error('Failed to fetch 7d klines for', symbol, e)
      }

      return {
        coin: base,
        pair: symbol,
        name: base, // can be improved with a metadata map later
        price: Number(t.lastPrice),
        changePercent: Number(t.priceChangePercent),
        volumeQuote: Number(t.quoteVolume),
        highPrice: Number(t.highPrice),
        lowPrice: Number(t.lowPrice),
        sparkline,
      }
    }

    // For table: only icon-backed top markets (top 10 by volume)
    let markets = await Promise.all(top.map(mapTicker))

    // Explicitly include TON and DOT in the table, even if they are not in the top 10 by volume
    const desiredExtras = ['TONUSDT', 'DOTUSDT']
    const existingPairs = new Set(markets.map((m) => m.pair))

    for (const symbol of desiredExtras) {
      if (!existingPairs.has(symbol)) {
        const extraRaw = iconMarkets.find((t) => t.symbol === symbol)
        if (extraRaw) {
          const extraMapped = await mapTicker(extraRaw)
          markets.push(extraMapped)
          existingPairs.add(symbol)
        }
      }
    }

    // For gainers/losers sections: use all USDT markets (no icon restriction)
    const topGainers = await Promise.all(topGainersRaw.map(mapTicker))
    const topLosers = await Promise.all(topLosersRaw.map(mapTicker))

    return NextResponse.json({ markets, topGainers, topLosers })
  } catch (err) {
    console.error('Failed to fetch top Binance markets', err)
    return NextResponse.json(
      { error: 'Failed to load market overview.' },
      { status: 502 },
    )
  }
}
