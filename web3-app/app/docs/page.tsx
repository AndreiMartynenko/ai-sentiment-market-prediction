"use client"

import Link from "next/link"

export default function DocsPage() {
  return (
    <main className="min-h-screen bg-gray-950 text-gray-50">
      <div className="mx-auto max-w-4xl px-4 py-10">
        <h1 className="text-2xl font-semibold text-gray-100">ProofOfSignal Docs (Preview)</h1>
        <p className="mt-2 text-sm text-gray-400">
          This is a lightweight docs placeholder so you can explore the app without 404 pages.
        </p>

        <section className="mt-8 space-y-3 text-sm text-gray-300">
          <h2 className="text-sm font-semibold text-gray-100">Market Snapshot</h2>
          <p className="text-xs text-gray-400">
            The Market Snapshot section on the homepage shows live data for core markets (BTC, ETH, SOL, BNB).
            Prices, 24h performance, and 24h quote volume are fetched in real time from Binance.
          </p>
        </section>

        <section className="mt-6 space-y-3 text-sm text-gray-300">
          <h2 className="text-sm font-semibold text-gray-100">AI Trading Signals</h2>
          <p className="text-xs text-gray-400">
            On the dashboard, AI Trade Signal and Algo Signals combine EMA20/50, RSI14, and FinBERT news sentiment
            across multiple timeframes (5m, 15m, 1h, 4h, 1d) to produce BUY / SHORT / HOLD suggestions with a
            confidence score and short text reasons. These are for research and education only, not financial advice.
          </p>
        </section>

        <section className="mt-8 border-t border-gray-900 pt-6 text-xs text-gray-500">
          <p>
            More detailed API documentation can be added here later (REST endpoints, auth, examples, etc.).
          </p>
          <p className="mt-3">
            <Link href="/" className="text-emerald-300 hover:text-emerald-200">
              ← Back to home
            </Link>
          </p>
        </section>
      </div>
    </main>
  )
}
