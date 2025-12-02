import Link from "next/link"
import { Github, Twitter } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-gray-800 bg-gray-950/95">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8 text-sm text-gray-400 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-2">
          <div className="text-xs uppercase tracking-[0.2em] text-emerald-400">
            ProofOfSignal
          </div>
          <div className="text-xs text-gray-500">
            AI Sentiment Market Prediction • Web3‑ready analytics for traders & protocols.
          </div>
          <div className="text-xs text-gray-600">
            © {new Date().getFullYear()} ProofOfSignal. All rights reserved.
          </div>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-8">
          <nav className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-gray-400">
            <Link href="/api" className="hover:text-emerald-300">
              API
            </Link>
            <Link href="/contact" className="hover:text-emerald-300">
              Contact
            </Link>
          </nav>

          <div className="flex items-center gap-4 text-gray-500">
            <a
              href="https://github.com/AndreiMartynenko"
              target="_blank"
              rel="noreferrer"
              className="hover:text-emerald-300"
            >
              <Github className="h-4 w-4" />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noreferrer"
              className="hover:text-emerald-300"
            >
              <Twitter className="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
