"use client"

import Link from "next/link"

export default function ContactPage() {
  return (
    <main className="min-h-screen bg-gray-950 text-gray-50">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="text-2xl font-semibold text-gray-100">Contact</h1>
        <p className="mt-2 text-sm text-gray-400">
          This is a simple contact placeholder page so the navigation links work while the product is in
          development.
        </p>

        <section className="mt-6 space-y-2 text-xs text-gray-400">
          <p>
            • Use the trading dashboard to explore live market data, sentiment analysis, and algo signals.
          </p>
          <p>
            • When you are ready, this page can be extended with a real contact form or links to Twitter, Discord,
            or email.
          </p>
        </section>

        <section className="mt-8 border-t border-gray-900 pt-6 text-xs text-gray-500">
          <Link href="/" className="text-emerald-300 hover:text-emerald-200">
            ← Back to home
          </Link>
        </section>
      </div>
    </main>
  )
}
