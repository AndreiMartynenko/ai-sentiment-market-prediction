'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

interface MarketRow {
  coin: string
  pair: string
  name: string
  price: number
  changePercent: number
  volumeQuote: number
  highPrice: number
  lowPrice: number
}

export default function MarketPage() {
  const [rows, setRows] = useState<MarketRow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const [view, setView] = useState<'coins' | 'tokens'>('coins')

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        setError(null)

        const res = await fetch('/api/markets/top', { cache: 'no-store' })
        if (!res.ok) throw new Error('Failed to load markets')
        const data = await res.json()
        if (cancelled) return

        const mapped: MarketRow[] = (data.markets || []).map((m: any) => ({
          coin: m.coin as string,
          pair: m.pair as string,
          name: m.name as string,
          price: Number(m.price),
          changePercent: Number(m.changePercent),
          volumeQuote: Number(m.volumeQuote),
          highPrice: Number(m.highPrice),
          lowPrice: Number(m.lowPrice),
        }))

        setRows(mapped)
      } catch (e) {
        if (!cancelled) setError('Failed to load markets.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  const majors = new Set(['BTC', 'ETH', 'SOL', 'BNB'])
  const tokensOnly = rows.filter((r) => !majors.has(r.coin))
  const activeRows = view === 'coins' ? rows : tokensOnly

  return (
    <main className="min-h-screen bg-gray-950 text-gray-50">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <header className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-base font-semibold text-gray-100">Market Overview</h1>
            <p className="mt-1 text-xs text-gray-500">
              Live prices, 24h performance and liquidity for the top Binance USDT markets tracked by
              ProofOfSignal.
            </p>
            <div className="mt-3 inline-flex rounded-full bg-gray-900 p-1 text-[11px]">
              <button
                type="button"
                onClick={() => setView('coins')}
                className={
                  'rounded-full px-3 py-1 text-xs ' +
                  (view === 'coins'
                    ? 'bg-emerald-500 text-gray-950'
                    : 'text-gray-300 hover:text-emerald-200')
                }
              >
                Coins
              </button>
              <button
                type="button"
                onClick={() => setView('tokens')}
                className={
                  'rounded-full px-3 py-1 text-xs ' +
                  (view === 'tokens'
                    ? 'bg-emerald-500 text-gray-950'
                    : 'text-gray-300 hover:text-emerald-200')
                }
              >
                Tokens
              </button>
            </div>
          </div>
          <Link
            href="/dashboard"
            className="rounded-full border border-gray-800 bg-gray-900 px-3 py-1 text-xs text-gray-300 hover:border-emerald-500/40 hover:text-emerald-200"
          >
            ← Back to dashboard
          </Link>
        </header>

        {loading && <div className="mb-4 text-xs text-gray-500">Loading market data…</div>}
        {error && !loading && <div className="mb-4 text-xs text-red-400">{error}</div>}

        {/* Top gainers / losers for current view */}
        {!loading && !error && activeRows.length > 0 && (
          <section className="mb-4 grid gap-4 md:grid-cols-2 text-[11px]">
            {/* Top gainers */}
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-3">
              <h2 className="mb-2 text-xs font-semibold text-gray-100">Top gainers (24h %)</h2>
              <div className="space-y-1.5">
                {activeRows
                  .slice()
                  .sort((a, b) => b.changePercent - a.changePercent)
                  .slice(0, 5)
                  .map((row) => (
                    <button
                      key={row.pair}
                      type="button"
                      onClick={() => router.push(`/dashboard?symbol=${encodeURIComponent(row.pair)}`)}
                      className="flex w-full items-center justify-between rounded-md px-1 py-0.5 text-left text-[11px] hover:bg-gray-900/80"
                    >
                      <div>
                        <div className="text-gray-200">{row.coin}</div>
                        <div className="text-[10px] text-gray-500">{row.pair}</div>
                      </div>
                      <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-300">
                        {`+${row.changePercent.toFixed(2)}%`}
                      </span>
                    </button>
                  ))}
              </div>
            </div>

            {/* Top losers */}
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-3">
              <h2 className="mb-2 text-xs font-semibold text-gray-100">Top losers (24h %)</h2>
              <div className="space-y-1.5">
                {activeRows
                  .slice()
                  .sort((a, b) => a.changePercent - b.changePercent)
                  .slice(0, 5)
                  .map((row) => (
                    <button
                      key={row.pair}
                      type="button"
                      onClick={() => router.push(`/dashboard?symbol=${encodeURIComponent(row.pair)}`)}
                      className="flex w-full items-center justify-between rounded-md px-1 py-0.5 text-left text-[11px] hover:bg-gray-900/80"
                    >
                      <div>
                        <div className="text-gray-200">{row.coin}</div>
                        <div className="text-[10px] text-gray-500">{row.pair}</div>
                      </div>
                      <span className="rounded-full bg-red-500/10 px-2 py-0.5 text-[10px] font-semibold text-red-300">
                        {`${row.changePercent.toFixed(2)}%`}
                      </span>
                    </button>
                  ))}
              </div>
            </div>
          </section>
        )}

        <div className="overflow-hidden rounded-2xl border border-gray-900 bg-gray-950/80 text-[11px]">
          <div className="max-h-[520px] overflow-y-auto">
          <table className="min-w-full border-collapse text-left">
            <thead className="bg-gray-950">
              <tr className="border-b border-gray-900 text-gray-500">
                <th className="px-4 py-2 font-medium">Market</th>
                <th className="px-4 py-2 font-medium">Pair</th>
                <th className="px-4 py-2 font-medium">Price</th>
                <th className="px-4 py-2 font-medium">24h %</th>
                <th className="px-4 py-2 font-medium">24h High</th>
                <th className="px-4 py-2 font-medium">24h Low</th>
                <th className="px-4 py-2 font-medium">Vol 24h (quote)</th>
              </tr>
            </thead>
            <tbody>
              {activeRows.map((row) => {
                const positive = row.changePercent >= 0
                const priceFormatted =
                  row.price >= 1000
                    ? `$${row.price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                    : `$${row.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`

                const changeFormatted = `${positive ? '+' : ''}${row.changePercent.toFixed(2)}%`
                const highFormatted =
                  row.highPrice >= 1000
                    ? `$${row.highPrice.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                    : `$${row.highPrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}`

                const lowFormatted =
                  row.lowPrice >= 1000
                    ? `$${row.lowPrice.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                    : `$${row.lowPrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
                const volumeBillions = row.volumeQuote / 1_000_000_000
                const volumeFormatted = `$${volumeBillions.toFixed(1)}B`

                return (
                  <tr
                    key={row.pair}
                    className="cursor-pointer border-b border-gray-900/80 last:border-0 hover:bg-gray-900/60"
                    onClick={() => router.push(`/dashboard?symbol=${encodeURIComponent(row.pair)}`)}
                  >
                    <td className="px-4 py-2">
                      <div className="flex flex-col">
                        <span className="text-gray-200">{row.coin}</span>
                        <span className="text-[10px] text-gray-500">{row.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2 text-gray-400">{row.pair}</td>
                    <td className="px-4 py-2 text-gray-200">{priceFormatted}</td>
                    <td className="px-4 py-2">
                      <span
                        className={
                          'inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ' +
                          (positive
                            ? 'bg-emerald-500/10 text-emerald-300'
                            : 'bg-red-500/10 text-red-300')
                        }
                      >
                        {changeFormatted}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-gray-300">{highFormatted}</td>
                    <td className="px-4 py-2 text-gray-300">{lowFormatted}</td>
                    <td className="px-4 py-2 text-gray-300">{volumeFormatted}</td>
                  </tr>
                )
              })}

              {!loading && activeRows.length === 0 && !error && (
                <tr>
                  <td colSpan={4} className="px-4 py-3 text-gray-500">
                    No markets available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          </div>
        </div>
      </div>
    </main>
  )
}
