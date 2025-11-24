'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface TimeframeSummary {
  timeframe: string
  trend: 'bullish' | 'bearish' | 'neutral'
  rsi: number
  note: string
}

interface IndicatorsResponse {
  symbol: string
  scalping: TimeframeSummary[]
  swing: TimeframeSummary[]
}

function trendChipClasses(trend: TimeframeSummary['trend']) {
  if (trend === 'bullish') return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/40'
  if (trend === 'bearish') return 'bg-red-500/10 text-red-300 border-red-500/40'
  return 'bg-gray-700/40 text-gray-300 border-gray-700'
}

export default function SignalsPage() {
  const [data, setData] = useState<IndicatorsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        setError(null)

        const res = await fetch('/api/indicators?symbol=BTCUSDT', { cache: 'no-store' })
        if (!res.ok) throw new Error('Failed to load signals')
        const json = (await res.json()) as IndicatorsResponse
        if (cancelled) return
        setData(json)
      } catch (e) {
        if (!cancelled) setError('Failed to load signals.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main className="min-h-screen bg-gray-950 text-gray-50">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <header className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-base font-semibold text-gray-100">AI Trading Signals</h1>
            <p className="mt-1 text-xs text-gray-500">
              Combined view of EMA20/50, RSI14 and news sentiment across multiple timeframes. These
              signals are for research and educational use only, not financial advice.
            </p>
          </div>
          <Link
            href="/dashboard"
            className="rounded-full border border-gray-800 bg-gray-900 px-3 py-1 text-xs text-gray-300 hover:border-emerald-500/40 hover:text-emerald-200"
          >
            ← Back to dashboard
          </Link>
        </header>

        {loading && <div className="mb-4 text-xs text-gray-500">Loading signals…</div>}
        {error && !loading && <div className="mb-4 text-xs text-red-400">{error}</div>}

        {data && (
          <div className="space-y-6 text-xs">
            {/* Scalping signals table */}
            <section>
              <div className="mb-2 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-sm font-semibold text-gray-100">Scalping Signals</h2>
                  <p className="text-[11px] text-gray-500">
                    Short-term intraday direction for 5m, 15m and 1h timeframes, using EMA20/50 and RSI14.
                  </p>
                </div>
              </div>

              <div className="overflow-hidden rounded-2xl border border-gray-900 bg-gray-950/80">
                <table className="min-w-full border-collapse text-left text-[11px]">
                  <thead className="bg-gray-950">
                    <tr className="border-b border-gray-900 text-gray-500">
                      <th className="px-4 py-2 font-medium">Timeframe</th>
                      <th className="px-4 py-2 font-medium">Trend</th>
                      <th className="px-4 py-2 font-medium">RSI</th>
                      <th className="px-4 py-2 font-medium">Comment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.scalping.map((row) => (
                      <tr key={row.timeframe} className="border-b border-gray-900/80 last:border-0">
                        <td className="px-4 py-2 text-gray-300">{row.timeframe}</td>
                        <td className="px-4 py-2">
                          <span
                            className={
                              'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold ' +
                              trendChipClasses(row.trend)
                            }
                          >
                            <span className="capitalize">{row.trend}</span>
                          </span>
                        </td>
                        <td className="px-4 py-2 text-gray-300">{row.rsi.toFixed(1)}</td>
                        <td className="px-4 py-2 text-gray-400">{row.note}</td>
                      </tr>
                    ))}

                    {!loading && data.scalping.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-4 py-3 text-gray-500">
                          No scalping signals available.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Swing signals table */}
            <section>
              <div className="mb-2 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-sm font-semibold text-gray-100">Swing / Daytrading Signals</h2>
                  <p className="text-[11px] text-gray-500">
                    Medium-term trend view on 4h and 1D timeframes based on EMA20/50, RSI14 and our AI
                    signal engine.
                  </p>
                </div>
              </div>

              <div className="overflow-hidden rounded-2xl border border-gray-900 bg-gray-950/80">
                <table className="min-w-full border-collapse text-left text-[11px]">
                  <thead className="bg-gray-950">
                    <tr className="border-b border-gray-900 text-gray-500">
                      <th className="px-4 py-2 font-medium">Timeframe</th>
                      <th className="px-4 py-2 font-medium">Trend</th>
                      <th className="px-4 py-2 font-medium">RSI</th>
                      <th className="px-4 py-2 font-medium">Comment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.swing.map((row) => (
                      <tr key={row.timeframe} className="border-b border-gray-900/80 last:border-0">
                        <td className="px-4 py-2 text-gray-300">{row.timeframe}</td>
                        <td className="px-4 py-2">
                          <span
                            className={
                              'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold ' +
                              trendChipClasses(row.trend)
                            }
                          >
                            <span className="capitalize">{row.trend}</span>
                          </span>
                        </td>
                        <td className="px-4 py-2 text-gray-300">{row.rsi.toFixed(1)}</td>
                        <td className="px-4 py-2 text-gray-400">{row.note}</td>
                      </tr>
                    ))}

                    {!loading && data.swing.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-4 py-3 text-gray-500">
                          No swing/daytrading signals available.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}
      </div>
    </main>
  )
}
