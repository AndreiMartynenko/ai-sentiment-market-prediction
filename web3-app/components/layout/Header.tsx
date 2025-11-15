"use client"

import { useState } from "react"
import Link from "next/link"
import { TrendingUp, Menu, X } from "lucide-react"

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const navigation = [
    { name: "Overview", href: "/" },
    { name: "Signals", href: "/signals" },
    { name: "Market", href: "/market" },
    { name: "Docs", href: "/docs" },
  ]

  return (
    <header className="sticky top-0 z-40 border-b border-gray-800/80 bg-gray-950/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 shadow-lg shadow-emerald-500/30">
            <TrendingUp className="h-5 w-5 text-gray-950" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-semibold tracking-wide text-gray-300">
              ProofOfSignal
            </span>
            <span className="text-xs text-gray-500">AI Sentiment Engine</span>
          </div>
        </Link>

        {/* Desktop navigation */}
        <nav className="hidden items-center gap-8 text-sm text-gray-400 md:flex">
          {navigation.map((item) => (
            <Link key={item.name} href={item.href} className="nav-link">
              {item.name}
            </Link>
          ))}
        </nav>

        {/* CTAs */}
        <div className="hidden items-center gap-3 md:flex">
          <Link
            href="/dashboard"
            className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-xs font-semibold tracking-wide text-emerald-300 hover:border-emerald-400/60 hover:bg-emerald-500/20 transition-colors"
          >
            Launch App
          </Link>
        </div>

        {/* Mobile menu button */}
        <button
          className="inline-flex items-center justify-center rounded-lg border border-gray-800 p-2 text-gray-400 hover:border-gray-700 hover:text-gray-100 md:hidden"
          onClick={() => setIsMenuOpen((open) => !open)}
        >
          {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile nav */}
      {isMenuOpen && (
        <div className="border-t border-gray-800/80 bg-gray-950/95 md:hidden">
          <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-3 text-sm">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="rounded-lg px-2 py-2 text-gray-300 hover:bg-gray-900/80"
                onClick={() => setIsMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
            <Link
              href="/dashboard"
              className="mt-2 rounded-lg bg-gradient-to-r from-emerald-500 to-emerald-400 px-3 py-2 text-center text-xs font-semibold tracking-wide text-gray-950"
              onClick={() => setIsMenuOpen(false)}
            >
              Launch App
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}
