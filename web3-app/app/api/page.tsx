"use client"

import Link from "next/link"

export default function ApiPage() {
  return (
    <main className="min-h-screen bg-gray-950 text-gray-50">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="text-2xl font-semibold text-gray-100">API</h1>
        <p className="mt-2 text-sm text-gray-400">The public API documentation is currently under construction.</p>

        <div className="mt-6 rounded-2xl border border-gray-900 bg-gray-950/80 p-5 text-xs text-gray-400">
          <p>
            This section will soon include details on how to access ProofOfSignal programmatically via HTTP and
            WebSocket endpoints.
          </p>
          <p className="mt-3 text-gray-500">For now, please use the dashboard and market pages in the navigation.</p>
        </div>

        <section className="mt-8 border-t border-gray-900 pt-6 text-xs text-gray-500">
          <Link href="/" className="text-emerald-300 hover:text-emerald-200">
            ← Back to home
          </Link>
        </section>
      </div>
    </main>
  )
}
