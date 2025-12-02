'use client'

import type React from 'react'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { supabase } from '../lib/supabaseClient'
import {
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Signal,
  BarChart3,
  Users,
} from 'lucide-react'

export default function HomePage() {
  const [selectedCoin, setSelectedCoin] = useState('BTC')
  const [marketData, setMarketData] = useState<
    | {
        coin: string
        name: string
        price: number
        changePercent: number
        volumeQuote: number
      }[]
    | null
  >(null)
  const [marketLoading, setMarketLoading] = useState(false)
  const [marketError, setMarketError] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const router = useRouter()

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

    async function loadMarkets() {
      try {
        setMarketLoading(true)
        setMarketError(null)

        const res = await fetch('/api/markets', { cache: 'no-store' })
        if (!res.ok) {
          throw new Error('Failed to load markets')
        }

        const data = await res.json()
        if (cancelled) return

        const mapped = (data.markets || []).map((m: any) => ({
          coin: m.coin as string,
          name: m.name as string,
          price: Number(m.price),
          changePercent: Number(m.changePercent),
          volumeQuote: Number(m.volumeQuote),
        }))

        setMarketData(mapped)
      } catch (err) {
        if (!cancelled) {
          setMarketError('Failed to load market snapshot.')
        }
      } finally {
        if (!cancelled) setMarketLoading(false)
      }
    }

    loadMarkets()

    return () => {
      cancelled = true
    }
  }, [])

  const latestSignals = [
    { coin: 'BTC', signal: 'BUY', confidence: 0.92, time: '2 min ago' },
    { coin: 'ETH', signal: 'NEUTRAL', confidence: 0.65, time: '5 min ago' },
    { coin: 'SOL', signal: 'SELL', confidence: 0.88, time: '8 min ago' },
  ]

  const getSignalClass = (signal: string) => {
    switch (signal.toLowerCase()) {
      case 'buy':
        return 'signal-buy'
      case 'sell':
        return 'signal-sell'
      default:
        return 'signal-neutral'
    }
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Hero */}
      <section className="border-b border-gray-900/60 bg-gradient-to-b from-gray-950 via-gray-950 to-gray-950/95">
        <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 pb-16 pt-10 md:flex-row md:items-center md:pb-20 md:pt-16">
          {/* Left: copy */}
          <div className="flex-1 space-y-7">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/5 px-3 py-1 text-xs font-medium text-emerald-300">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              Live AI Sentiment Signals
            </div>

            <h1 className="text-balance text-4xl font-semibold tracking-tight text-gray-50 sm:text-5xl md:text-6xl">
              Web3‑native
              <span className="block bg-gradient-to-r from-emerald-400 to-emerald-200 bg-clip-text text-transparent">
                Market Sentiment Engine
              </span>
            </h1>

            <p className="max-w-xl text-sm leading-relaxed text-gray-400 sm:text-base">
              ProofOfSignal analyzes order books, on‑chain data, and social signals in real time to
              deliver transparent, reproducible trading signals for both traders and protocols.
            </p>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <button
                type="button"
                onClick={() =>
                  isAuthenticated ? router.push('/dashboard') : router.push('/auth/login')
                }
                className="btn-primary inline-flex items-center justify-center px-7 py-3 text-sm font-semibold"
              >
                Launch Trading Dashboard
                <ArrowUpRight className="ml-2 h-4 w-4" />
              </button>
              <Link
                href="/api"
                className="btn-secondary inline-flex items-center justify-center px-7 py-3 text-sm font-semibold"
              >
                View API
              </Link>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 text-xs text-gray-400 sm:grid-cols-4">
              <div>
                <div className="text-sm font-semibold text-gray-100">+24k</div>
                <div className="text-[11px] uppercase tracking-wide text-gray-500">Signals Generated</div>
              </div>
              <div>
                <div className="text-sm font-semibold text-emerald-300">87%</div>
                <div className="text-[11px] uppercase tracking-wide text-gray-500">Win Rate (backtested)</div>
              </div>
              <div>
                <div className="text-sm font-semibold text-gray-100">18</div>
                <div className="text-[11px] uppercase tracking-wide text-gray-500">Supported Markets</div>
              </div>
              <div>
                <div className="text-sm font-semibold text-gray-100">&lt; 300ms</div>
                <div className="text-[11px] uppercase tracking-wide text-gray-500">Signal Latency</div>
              </div>
            </div>
          </div>

          {/* Right: glass widget */}
          <div className="flex-1">
            <div className="relative">
              <div className="pointer-events-none absolute -inset-8 rounded-3xl bg-emerald-500/10 blur-3xl" />
              <div className="relative rounded-3xl border border-gray-800 bg-gray-950/80 p-5 shadow-[0_0_60px_rgba(16,185,129,0.25)]">
                <div className="flex items-center justify-between pb-3 text-xs text-gray-500">
                  <span className="font-mono text-[11px] text-gray-400">AI Signal Stream</span>
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] text-emerald-300">
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                    Live
                  </span>
                </div>

                <div className="space-y-3 text-xs font-mono">
                  {latestSignals.map((s) => (
                    <div
                      key={s.coin}
                      className="flex items-center justify-between rounded-xl border border-gray-800 bg-gray-900/60 px-3 py-2"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gray-900">
                          <span className="text-[11px] font-semibold text-gray-100">{s.coin}</span>
                        </div>
                        <div>
                          <div className="text-[11px] text-gray-400">{s.time}</div>
                          <div className="text-[11px] text-gray-500">sentiment &amp; orderflow scan</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-[11px] font-semibold ${s.signal === 'BUY' ? 'text-emerald-300' : s.signal === 'SELL' ? 'text-red-400' : 'text-gray-300'}`}>
                          {s.signal}
                        </div>
                        <div className="text-[10px] text-gray-500">conf {(s.confidence * 100).toFixed(0)}%</div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 grid grid-cols-3 gap-3 text-[10px] text-gray-500">
                  <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-3">
                    <div className="flex items-center justify-between">
                      <span>Global Sentiment</span>
                      <ArrowUpRight className="h-3 w-3 text-emerald-300" />
                    </div>
                    <div className="mt-2 flex items-baseline gap-1">
                      <span className="text-sm font-semibold text-emerald-300">0.72</span>
                      <span className="text-[10px] text-gray-500">bullish</span>
                    </div>
                  </div>
                  <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-3">
                    <div className="flex items-center justify-between">
                      <span>BTC/ETH Spread</span>
                      <ArrowDownRight className="h-3 w-3 text-gray-400" />
                    </div>
                    <div className="mt-2 flex items-baseline gap-1">
                      <span className="text-sm font-semibold text-gray-200">1.8%</span>
                      <span className="text-[10px] text-gray-500">24h</span>
                    </div>
                  </div>
                  <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-3">
                    <div className="flex items-center justify-between">
                      <span>Nodes</span>
                      <TrendingUp className="h-3 w-3 text-emerald-300" />
                    </div>
                    <div className="mt-2 flex items-baseline gap-1">
                      <span className="text-sm font-semibold text-gray-200">12</span>
                      <span className="text-[10px] text-gray-500">regions</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Market snapshot */}
      <section className="border-b border-gray-900/60 bg-gray-950 py-10">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Market Snapshot</h2>
              <p className="text-xs text-gray-500">High‑level view of top markets tracked by ProofOfSignal.</p>
            </div>
          </div>

          {marketLoading && (
            <div className="mb-3 text-xs text-gray-500">Loading market snapshot…</div>
          )}

          {marketError && !marketLoading && (
            <div className="mb-3 text-xs text-red-400">{marketError}</div>
          )}

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {(marketData || []).map((item) => {
              const positive = item.changePercent >= 0
              const priceFormatted =
                item.price >= 1000
                  ? `$${item.price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                  : `$${item.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`

              const changeFormatted = `${positive ? '+' : ''}${item.changePercent.toFixed(2)}%`
              const volumeBillions = item.volumeQuote / 1_000_000_000
              const volumeFormatted = `$${volumeBillions.toFixed(1)}B`

              return (
              <div
                key={item.coin}
                className="rounded-2xl border border-gray-900 bg-gray-950/80 p-4 transition hover:border-emerald-500/40 hover:bg-gray-900/80"
              >
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <div className="text-xs font-semibold text-gray-200">{item.coin}</div>
                    <div className="text-[11px] text-gray-500">{item.name}</div>
                  </div>
                  {positive ? (
                    <ArrowUpRight className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 text-red-400" />
                  )}
                </div>
                <div className="flex items-end justify-between">
                  <div>
                    <div className="text-sm font-semibold text-gray-100">{priceFormatted}</div>
                    <div
                      className={`text-[11px] font-medium ${positive ? 'text-emerald-300' : 'text-red-400'}`}
                    >
                      {changeFormatted}
                    </div>
                  </div>
                  <div className="text-right text-[11px] text-gray-500">
                    <div>Vol 24h</div>
                    <div className="text-gray-300">{volumeFormatted}</div>
                  </div>
                </div>
              </div>
            )})}
          </div>
        </div>
      </section>

      {/* How it works / features */}
      <section className="border-b border-gray-900/60 bg-gray-950 py-14">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-8 max-w-2xl">
            <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">How It Works</h2>
            <p className="mt-2 text-lg font-medium text-gray-100">From raw data streams to actionable signals.</p>
            <p className="mt-2 text-sm text-gray-500">
              ProofOfSignal combines market data, on‑chain activity, and social‑media NLP models in a
              latency‑optimized pipeline to turn noisy streams into clean, tradable signals.
            </p>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-5">
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10">
                <TrendingUp className="h-4 w-4 text-emerald-400" />
              </div>
              <h3 className="mb-2 text-sm font-semibold text-gray-100">Signal Engine</h3>
              <p className="text-xs text-gray-500">
                Ensemble models analyze order flow, funding, volatility, and news flow, producing
                BUY/SELL/NEUTRAL signals for each market in real time.
              </p>
            </div>
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-5">
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10">
                <Signal className="h-4 w-4 text-emerald-400" />
              </div>
              <h3 className="mb-2 text-sm font-semibold text-gray-100">Risk Layer</h3>
              <p className="text-xs text-gray-500">
                Per‑signal risk controls: position sizing, max drawdown limits, and dynamic stop‑loss logic
                tailored to each strategy.
              </p>
            </div>
            <div className="rounded-2xl border border-gray-900 bg-gray-950/80 p-5">
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10">
                <BarChart3 className="h-4 w-4 text-emerald-400" />
              </div>
              <h3 className="mb-2 text-sm font-semibold text-gray-100">API for Builders</h3>
              <p className="text-xs text-gray-500">
                A simple API to plug into your bot, dApp, or quant stack with JSON/REST endpoints and
                WebSocket feeds ready for production use.
              </p>
            </div>
          </div>
        </div>
      </section>

    </div>
  )
}
