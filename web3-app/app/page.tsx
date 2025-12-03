'use client'

import type React from 'react'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
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
                Launch Trading Platform
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

      {/* Make better investment decisions / inline SVG visual */}
      <section className="border-b border-gray-900/60 bg-gray-950 py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-8 flex flex-col gap-3 text-center md:text-left">
            <h2 className="text-xs font-semibold uppercase tracking-[0.25em] text-emerald-400">ProofOfSignal in action</h2>
            <p className="text-2xl font-semibold tracking-tight text-gray-50 sm:text-3xl">
              Make better investment decisions.
            </p>
            <p className="max-w-3xl text-sm text-gray-500 md:text-base">
              With ProofOfSignal, live price action, sentiment, and news sit on one canvas, so you can move from
              raw information to clear conviction instead of guessing off noise.
            </p>
          </div>

          <div className="overflow-hidden rounded-3xl border border-gray-900 bg-gradient-to-b from-gray-900 via-gray-950 to-black shadow-[0_0_80px_rgba(16,185,129,0.5)]">
            <div className="relative">
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_0%_0%,rgba(16,185,129,0.3),transparent_55%),radial-gradient(circle_at_100%_100%,rgba(56,189,248,0.25),transparent_55%)] mix-blend-screen" />
              <div className="relative">
                <Image
                  src="/trading-dashboard.png"
                  alt="ProofOfSignal trading dashboard screenshot"
                  width={1600}
                  height={900}
                  className="h-full w-full object-cover"
                  priority
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-gray-900/60 bg-black/90 py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-10 max-w-3xl text-center md:text-left">
            <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Inside the dashboard</h2>
            <p className="mt-2 text-xl font-semibold tracking-tight text-gray-100 sm:text-2xl">
              Every panel tells you something different about the market.
            </p>
          </div>

          <div className="grid items-center gap-10 md:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
            <div className="overflow-hidden rounded-3xl border border-gray-900 bg-gradient-to-br from-gray-900 via-gray-950 to-black">
              <div className="relative">
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-tr from-emerald-500/15 via-transparent to-sky-500/15 mix-blend-screen" />
                <Image
                  src="/news.png"
                  alt="Dashboard news and sentiment section"
                  width={1600}
                  height={900}
                  className="h-full w-full object-cover object-center"
                />
              </div>
            </div>

            <div className="space-y-4">
              <p className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/5 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-emerald-300">
                News & context
              </p>
              <h3 className="text-lg font-semibold tracking-tight text-gray-100 sm:text-xl">
                News panel keeps you ahead of the narrative.
              </h3>
              <p className="text-sm text-gray-400">
                The right-hand column surfaces headlines scored by our NLP models, so you instantly see whether
                the news flow around BTC, ETH, or any asset is bullish, bearish, or just noise.
              </p>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="mt-[6px] h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <span>Color-coded tags show sentiment for each story at a glance.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-[6px] h-1.5 w-1.5 rounded-full bg-sky-400" />
                  <span>Confidence scores help you weigh one headline against the rest of the feed.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-gray-900/60 bg-black py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="grid items-center gap-10 md:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)]">
            <div className="order-2 space-y-4 md:order-1">
              <p className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/5 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-emerald-300">
                Trade signal
              </p>
              <h3 className="text-lg font-semibold tracking-tight text-gray-100 sm:text-xl">
                One clear signal to BUY, SELL, or HOLD.
              </h3>
              <p className="text-sm text-gray-400">
                Under the chart, the trade‑signal card distills sentiment, order flow, volatility and
                trend into a simple BUY / SELL / HOLD decision with a confidence bar you can actually act on.
              </p>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="mt-[6px] h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <span>Use the confidence meter to size positions instead of trading on gut feel.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-[6px] h-1.5 w-1.5 rounded-full bg-amber-400" />
                  <span>Timeframe labels keep scalps, swings, and longer‑term views clearly separated.</span>
                </li>
              </ul>
            </div>

            <div className="order-1 overflow-hidden rounded-3xl border border-gray-900 bg-gradient-to-br from-gray-900 via-gray-950 to-black md:order-2">
              <div className="relative">
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-bl from-emerald-500/20 via-transparent to-fuchsia-500/20 mix-blend-screen" />
                <Image
                  src="/trade signal.png"
                  alt="Dashboard trade signal card"
                  width={1600}
                  height={900}
                  className="h-full w-full object-cover object-bottom"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-gray-900/60 bg-black py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="grid items-center gap-10 md:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
            <div className="overflow-hidden rounded-3xl border border-gray-900 bg-gradient-to-br from-gray-900 via-gray-950 to-black">
              <div className="relative">
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-tr from-fuchsia-500/20 via-transparent to-sky-500/20 mix-blend-screen" />
                <Image
                  src="/algo-signals.png"
                  alt="Algo signals engine overview"
                  width={1600}
                  height={900}
                  className="h-full w-full object-cover object-center"
                />
              </div>
            </div>

            <div className="space-y-4">
              <p className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/5 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-emerald-300">
                Algo signals engine
              </p>
              <h3 className="text-lg font-semibold tracking-tight text-gray-100 sm:text-xl">
                Under the hood, multiple models agree before a signal goes live.
              </h3>
              <p className="text-sm text-gray-400">
                The Algo‑Signals view shows how our different models combine order flow, volatility, funding,
                sentiment and on‑chain activity into one unified conviction score for each market.
              </p>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="mt-[6px] h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <span>See which factors are driving a signal instead of trusting a black box.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-[6px] h-1.5 w-1.5 rounded-full bg-sky-400" />
                  <span>Helps you align discretionary views with what the algo stack is actually seeing.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-gray-900/60 bg-gray-950 py-16">
        <div className="mx-auto max-w-6xl px-4">
          <div className="grid items-center gap-10 md:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
            <div className="overflow-hidden rounded-3xl border border-gray-900 bg-gradient-to-br from-gray-900 via-gray-950 to-black">
              <div className="relative">
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-tr from-amber-400/20 via-transparent to-emerald-400/20 mix-blend-screen" />
                <Image
                  src="/rsi.png"
                  alt="Dashboard RSI and market regime section"
                  width={1600}
                  height={900}
                  className="h-full w-full object-cover object-bottom"
                />
              </div>
            </div>

            <div className="space-y-4">
              <p className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/5 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-emerald-300">
                Average Crypto RSI
              </p>
              <h3 className="text-lg font-semibold tracking-tight text-gray-100 sm:text-xl">
                RSI panel shows when the whole market is stretched.
              </h3>
              <p className="text-sm text-gray-400">
                The Average Crypto RSI card aggregates momentum across top markets, so you instantly see
                whether risk assets are extended, oversold, or sitting in a neutral regime.
              </p>
              <ul className="space-y-2 text-sm text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="mt-[6px] h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <span>Helps you avoid buying tops or panic‑selling bottoms when emotions run hot.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-[6px] h-1.5 w-1.5 rounded-full bg-sky-400" />
                  <span>Pairs perfectly with the AI Trade Signal to separate signal from background noise.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Call-to-action */}
      <section className="border-b border-gray-900/60 bg-black py-16">
        <div className="mx-auto flex max-w-3xl flex-col items-center px-4 text-center">
          <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400">Try it</h2>
          <p className="mt-3 text-2xl font-semibold tracking-tight text-gray-50 sm:text-3xl">
            Launch the ProofOfSignal trading platform.
          </p>
          <p className="mt-3 text-sm text-gray-400 md:text-base">
            Create your account and explore live signals.
          </p>

          <Link
            href="/auth/signup"
            className="btn-primary mt-6 inline-flex items-center justify-center px-7 py-3 text-sm font-semibold"
          >
            Launch Trading Platform
            <ArrowUpRight className="ml-2 h-4 w-4" />
          </Link>
        </div>
      </section>

    </div>
  )
}
