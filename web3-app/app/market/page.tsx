'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { supabase } from '../../lib/supabaseClient'

const TOP_COIN_ICONS: Record<string, string> = {
  BTC: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png?1547033579',
  ETH: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png?1595348880',
  SOL: 'https://assets.coingecko.com/coins/images/4128/small/solana.png?1640133422',
  BNB: 'https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png?1644979850',
  XRP: 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png?1605778731',
  ADA: 'https://assets.coingecko.com/coins/images/975/small/cardano.png?1547034860',
  DOGE: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png?1547792256',
  TON: 'https://assets.coingecko.com/coins/images/17980/small/ton_symbol.png?1670498136',
  LINK: 'https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png?1708601651',
  AVAX: 'https://assets.coingecko.com/coins/images/12559/small/coin-round-red.png?1683591517',
  USDT: 'https://assets.coingecko.com/coins/images/325/small/Tether-logo.png?1598003707',
  USDC: 'https://assets.coingecko.com/coins/images/6319/small/USD_Coin_icon.png?1547042389',
  TRX: 'https://assets.coingecko.com/coins/images/1094/small/tron-logo.png?1547035066',
  DOT: 'https://assets.coingecko.com/coins/images/12171/small/polkadot.png?1639712644',
  LTC: 'https://assets.coingecko.com/coins/images/2/small/litecoin.png?1547033580',
  UNI: 'https://assets.coingecko.com/coins/images/12504/small/uniswap-uni.png?1600306604',
}

interface GlobalAsset {
  symbol: string
  name: string
  price: number
  changePercent: number
}

interface MarketRow {
  coin: string
  pair: string
  name: string
  price: number
  changePercent: number
  volumeQuote: number
  highPrice: number
  lowPrice: number
  sparkline?: number[]
}

function Sparkline({ points, positive }: { points: number[]; positive: boolean }) {
  if (!points || points.length === 0) return null

  const min = Math.min(...points)
  const max = Math.max(...points)
  const span = max - min || 1

  const width = 80
  const height = 24

  const stepX = points.length > 1 ? width / (points.length - 1) : 0

  const d = points
    .map((p, i) => {
      const x = i * stepX
      const y = height - ((p - min) / span) * height
      return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')

  const strokeColor = positive ? '#4ade80' : '#f97373'

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-6 w-20 text-emerald-400"
      aria-hidden="true"
    >
      <path d={d} fill="none" stroke={strokeColor} strokeWidth="1.5" />
    </svg>
  )
}

export default function MarketPage() {
  const [rows, setRows] = useState<MarketRow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const [topGainers, setTopGainers] = useState<MarketRow[]>([])
  const [topLosers, setTopLosers] = useState<MarketRow[]>([])
  const [macroAssets, setMacroAssets] = useState<GlobalAsset[]>([])
  const [macroError, setMacroError] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    let isMounted = true

    async function checkAuth() {
      try {
        const { data } = await supabase.auth.getUser()
        if (!isMounted) return
        setIsAuthenticated(!!data?.user)
      } catch {
        if (isMounted) setIsAuthenticated(false)
      }
    }

    checkAuth()
    return () => {
      isMounted = false
    }
  }, [])

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
          sparkline: Array.isArray(m.sparkline)
            ? m.sparkline.map((v: any) => Number(v)).filter((v: number) => Number.isFinite(v))
            : [],
        }))

        setRows(mapped)

        const mapTopRow = (m: any): MarketRow => ({
          coin: m.coin as string,
          pair: m.pair as string,
          name: m.name as string,
          price: Number(m.price),
          changePercent: Number(m.changePercent),
          volumeQuote: Number(m.volumeQuote),
          highPrice: Number(m.highPrice),
          lowPrice: Number(m.lowPrice),
          sparkline: Array.isArray(m.sparkline)
            ? m.sparkline.map((v: any) => Number(v)).filter((v: number) => Number.isFinite(v))
            : [],
        })

        setTopGainers((data.topGainers || []).map(mapTopRow))
        setTopLosers((data.topLosers || []).map(mapTopRow))
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

  // Load global macro snapshot (gold + indices)
  useEffect(() => {
    let cancelled = false

    async function loadMacro() {
      try {
        setMacroError(null)
        const res = await fetch('/api/global/overview', { cache: 'no-store' })
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}))
          throw new Error(errData.error || 'Failed to load macro overview')
        }
        const data = await res.json()
        if (cancelled) return
        const assets: GlobalAsset[] = (data.assets || []).map((a: any) => ({
          symbol: String(a.symbol),
          name: String(a.name),
          price: Number(a.price),
          changePercent: Number(a.changePercent),
        }))
        if (!assets.length) {
          throw new Error('Macro snapshot is empty from provider.')
        }
        setMacroAssets(assets)
      } catch (e) {
        if (!cancelled) setMacroError('Failed to load macro snapshot.')
      }
    }

    loadMacro()
    return () => {
      cancelled = true
    }
  }, [])

  const activeRows = rows

  return (
    <main className="min-h-screen bg-gray-950 text-gray-50">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <header className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-base font-semibold text-gray-100">Market Overview</h1>
            <p className="mt-1 text-xs text-gray-500">
              Live prices, 24h performance and liquidity for the top markets tracked by
              ProofOfSignal.
            </p>
          </div>
          <Link
            href={isAuthenticated ? '/dashboard' : '/auth/signup'}
            className="rounded-full border border-gray-800 bg-gray-900 px-3 py-1 text-xs text-gray-300 hover:border-emerald-500/40 hover:text-emerald-200"
          >
            {isAuthenticated ? '← Back to platform' : '→ Go to platform'}
          </Link>
        </header>

        {loading && <div className="mb-4 text-xs text-gray-500">Loading market data…</div>}
        {error && !loading && <div className="mb-4 text-xs text-red-400">{error}</div>}

        {/* Top gainers / losers across all Binance USDT markets (top 3 each) */}
        {!loading && !error && (topGainers.length > 0 || topLosers.length > 0) && (
          <section className="mb-4 grid gap-4 md:grid-cols-3 text-[12px]">
            {/* Top gainers */}
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-3">
              <div className="mb-2 rounded-xl bg-gradient-to-r from-emerald-950/70 via-gray-950/80 to-gray-950/90 px-3 py-2">
                <h2 className="text-base font-semibold text-emerald-200">🚀 Top gainers</h2>
                <p className="mt-0.5 text-[11px] text-emerald-300/70">Most bullish movers by 24h percentage change.</p>
                <div className="mt-1 flex items-center justify-between text-[10px] text-emerald-300/60">
                  <span className="pl-0.5">Coin</span>
                  <span>Price</span>
                  <span className="pr-0.5">24h</span>
                </div>
              </div>
              <div className="space-y-2">
                {topGainers.map((row) => {
                    let priceFormatted: string
                    if (row.price >= 1000) {
                      priceFormatted = `$${row.price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                    } else if (row.price >= 1) {
                      priceFormatted = `$${row.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
                    } else {
                      priceFormatted = `$${row.price.toLocaleString(undefined, {
                        minimumFractionDigits: 4,
                        maximumFractionDigits: 8,
                      })}`
                    }

                    return (
                      <button
                        key={row.pair}
                        type="button"
                        onClick={() =>
                          isAuthenticated
                            ? router.push(`/dashboard?symbol=${encodeURIComponent(row.pair)}`)
                            : router.push('/auth/login')
                        }
                        className="flex w-full items-center justify-between rounded-lg bg-gray-950/40 px-2 py-1.5 text-left text-[12px] ring-1 ring-transparent hover:bg-gray-900/80 hover:ring-emerald-500/40"
                      >
                        <div className="flex flex-col">
                          <span className="text-[13px] font-semibold text-gray-100">{row.coin}</span>
                          <span className="text-[11px] text-gray-400">{row.pair}</span>
                        </div>
                        <span className="text-[12px] font-semibold text-gray-100">{priceFormatted}</span>
                        <span className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-[12px] font-semibold text-emerald-200">
                          {`+${row.changePercent.toFixed(2)}%`}
                        </span>
                      </button>
                    )
                  })}
              </div>
            </div>

            {/* Top losers */}
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-3">
              <div className="mb-2 rounded-xl bg-gradient-to-r from-red-950/70 via-gray-950/80 to-gray-950/90 px-3 py-2">
                <h2 className="text-base font-semibold text-red-200">🚨 Top losers</h2>
                <p className="mt-0.5 text-[11px] text-red-300/70">Sharpest 24h pullbacks by percentage change.</p>
                <div className="mt-1 flex items-center justify-between text-[10px] text-red-300/60">
                  <span className="pl-0.5">Coin</span>
                  <span>Price</span>
                  <span className="pr-0.5">24h</span>
                </div>
              </div>
              <div className="space-y-2">
                {topLosers.map((row) => {
                    let priceFormatted: string
                    if (row.price >= 1000) {
                      priceFormatted = `$${row.price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                    } else if (row.price >= 1) {
                      priceFormatted = `$${row.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
                    } else {
                      priceFormatted = `$${row.price.toLocaleString(undefined, {
                        minimumFractionDigits: 4,
                        maximumFractionDigits: 8,
                      })}`
                    }

                    return (
                      <button
                        key={row.pair}
                        type="button"
                        onClick={() =>
                          isAuthenticated
                            ? router.push(`/dashboard?symbol=${encodeURIComponent(row.pair)}`)
                            : router.push('/auth/login')
                        }
                        className="flex w-full items-center justify-between rounded-lg bg-gray-950/40 px-2 py-1.5 text-left text-[12px] ring-1 ring-transparent hover:bg-gray-900/80 hover:ring-red-500/40"
                      >
                        <div className="flex flex-col">
                          <span className="text-[13px] font-semibold text-gray-100">{row.coin}</span>
                          <span className="text-[11px] text-gray-400">{row.pair}</span>
                        </div>
                        <span className="text-[12px] font-semibold text-gray-100">{priceFormatted}</span>
                        <span className="rounded-full bg-red-500/15 px-2.5 py-0.5 text-[12px] font-semibold text-red-200">
                          {`${row.changePercent.toFixed(2)}%`}
                        </span>
                      </button>
                    )
                  })}
              </div>
            </div>

            {/* Macro snapshot: Gold and indices */}
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-3">
              <div className="mb-2 rounded-xl bg-gradient-to-r from-sky-950/70 via-gray-950/80 to-gray-950/90 px-3 py-2">
                <h2 className="text-base font-semibold text-sky-200">📊 Gold and Indices overview</h2>
                <p className="mt-0.5 text-[11px] text-sky-300/70">
                  Gold and indices prices for additional market context.
                </p>
                <div className="mt-1 flex items-center justify-between text-[10px] text-sky-300/60">
                  <span className="pl-0.5">Asset</span>
                  <span>Price</span>
                  <span className="pr-0.5">24h</span>
                </div>
              </div>
              {macroError && (
                <div className="text-[11px] text-red-400">{macroError}</div>
              )}
              {!macroError && macroAssets.length === 0 && (
                <div className="text-[11px] text-gray-500">Loading macro data…</div>
              )}
              <div className="space-y-2">
                {macroAssets.map((asset) => {
                  const pct = asset.changePercent
                  const positive = pct >= 0
                  const pctFormatted = `${positive ? '+' : ''}${pct.toFixed(2)}%`

                  let displaySymbol = asset.symbol
                  if (asset.symbol === 'GLD') displaySymbol = 'XAUUSD'
                  else if (asset.symbol === '^GSPC') displaySymbol = 'US500'
                  else if (asset.symbol === '^IXIC') displaySymbol = 'NAS100'
                  else if (asset.symbol === '^DJI') displaySymbol = 'US30'

                  let displayName = asset.symbol === 'GLD' ? 'Gold (XAUUSD)' : asset.name

                  if (asset.symbol === 'XAUUSD') displayName = '🥇 Gold'
                  else if (asset.symbol === 'US500') displayName = '🇺🇸 S&P 500'
                  else if (asset.symbol === 'NAS100') displayName = '💻 Nasdaq 100'
                  else if (asset.symbol === 'US30') displayName = '🏛️ Dow Jones 30'

                  return (
                    <button
                      key={asset.symbol}
                      type="button"
                      className="flex w-full items-center justify-between rounded-xl bg-gray-950/60 px-3 py-1.5 text-[11px] transition hover:bg-gray-900"
                    >
                      <div className="flex flex-col text-left">
                        <span className="text-[13px] font-semibold text-gray-100">{displayName}</span>
                        <span className="text-[11px] text-gray-400">{displaySymbol}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-[12px] font-semibold text-gray-100">
                          {asset.price.toLocaleString(undefined, {
                            maximumFractionDigits: 2,
                          })}
                        </span>
                        <span
                          className={
                            'rounded-full px-2.5 py-0.5 text-[12px] font-semibold ' +
                            (positive
                              ? 'bg-emerald-500/15 text-emerald-200'
                              : 'bg-red-500/15 text-red-200')
                          }
                        >
                          {pctFormatted}
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </section>
        )}

        {/* Market table */}

        <div className="overflow-hidden rounded-2xl border border-gray-900 bg-gray-950/80 text-[11px]">
          <div className="max-h-[520px] overflow-y-auto">
          <table className="min-w-full border-collapse text-left">
            <thead className="bg-gray-950">
              <tr className="border-b border-gray-900 text-[12px] font-semibold text-gray-300">
                <th className="px-4 py-2 text-left">Coin</th>
                <th className="px-4 py-2 text-left">Price</th>
                <th className="px-4 py-2 text-left">24h %</th>
                <th className="px-4 py-2 text-left">24h High</th>
                <th className="px-4 py-2 text-left">24h Low</th>
                <th className="px-4 py-2 text-left">Vol 24h (quote)</th>
                <th className="px-4 py-2 text-left">7d Chart</th>
              </tr>
            </thead>
            <tbody>
              {activeRows.map((row) => {
                const positive = row.changePercent >= 0

                let priceFormatted: string
                if (row.price >= 1000) {
                  priceFormatted = `$${row.price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                } else if (row.price >= 1) {
                  priceFormatted = `$${row.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
                } else {
                  // For very small prices, show more precision so it doesn't look like $0.00
                  priceFormatted = `$${row.price.toLocaleString(undefined, {
                    minimumFractionDigits: 4,
                    maximumFractionDigits: 8,
                  })}`
                }

                const changeFormatted = `${positive ? '+' : ''}${row.changePercent.toFixed(2)}%`
                const highFormatted =
                  row.highPrice >= 1000
                    ? `$${row.highPrice.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                    : `$${row.highPrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}`

                const lowFormatted =
                  row.lowPrice >= 1000
                    ? `$${row.lowPrice.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                    : `$${row.lowPrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
                let volumeFormatted: string
                if (row.volumeQuote >= 1_000_000_000) {
                  const v = row.volumeQuote / 1_000_000_000
                  volumeFormatted = `$${v.toFixed(v >= 10 ? 1 : 2)}B`
                } else if (row.volumeQuote >= 1_000_000) {
                  const v = row.volumeQuote / 1_000_000
                  volumeFormatted = `$${v.toFixed(v >= 10 ? 1 : 2)}M`
                } else if (row.volumeQuote >= 1_000) {
                  const v = row.volumeQuote / 1_000
                  volumeFormatted = `$${v.toFixed(v >= 10 ? 1 : 2)}K`
                } else {
                  volumeFormatted = `$${row.volumeQuote.toLocaleString(undefined, {
                    maximumFractionDigits: 2,
                  })}`
                }

                return (
                  <tr
                    key={row.pair}
                    className="cursor-pointer border-b border-gray-900/80 last:border-0 hover:bg-gray-900/60"
                    onClick={() =>
                      isAuthenticated
                        ? router.push(`/dashboard?symbol=${encodeURIComponent(row.pair)}`)
                        : router.push('/auth/login')
                    }
                  >
                    <td className="px-4 py-2">
                      <div className="flex items-center gap-2">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-900 text-[11px] font-semibold text-gray-200 overflow-hidden">
                          {TOP_COIN_ICONS[row.coin] ? (
                            <img
                              src={TOP_COIN_ICONS[row.coin]}
                              alt={row.coin}
                              className="h-6 w-6 object-contain"
                              onError={(e) => {
                                const target = e.currentTarget as HTMLImageElement
                                target.style.display = 'none'
                                target.parentElement && (target.parentElement.textContent = row.coin.charAt(0))
                              }}
                            />
                          ) : (
                            row.coin.charAt(0)
                          )}
                        </div>
                        <div className="flex flex-col">
                          <span className="text-gray-200">{row.coin}</span>
                          <span className="text-[10px] text-gray-500">{row.pair}</span>
                        </div>
                      </div>
                    </td>
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
                    <td className="px-4 py-2 text-gray-300">
                      <Sparkline points={row.sparkline || []} positive={positive} />
                    </td>
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
