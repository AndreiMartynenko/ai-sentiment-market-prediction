"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { TrendingUp, Menu, X, User } from "lucide-react"
import { supabase } from "../../lib/supabaseClient"

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState<any | null>(null)
  const [userLoading, setUserLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    let isMounted = true

    async function loadUser() {
      try {
        const { data, error } = await supabase.auth.getUser()
        if (!isMounted) return
        if (!error && data?.user) {
          setCurrentUser(data.user)
        } else {
          setCurrentUser(null)
        }
      } catch {
        if (isMounted) setCurrentUser(null)
      } finally {
        if (isMounted) setUserLoading(false)
      }
    }

    loadUser()

     const { data: authListener } = supabase.auth.onAuthStateChange((_event, session) => {
       if (!isMounted) return
       setCurrentUser(session?.user ?? null)
       setUserLoading(false)
     })

    return () => {
      isMounted = false
      authListener.subscription.unsubscribe()
    }
  }, [])

  const handleSignOut = async () => {
    try {
      await supabase.auth.signOut()
    } catch {
      // ignore error, best-effort logout
    } finally {
      setCurrentUser(null)
      setIsMenuOpen(false)
      router.push("/")
    }
  }

  const navigation = [
    { name: "Overview", href: "/" },
    { name: "Market", href: "/market" },
    { name: "API", href: "/api" },
    { name: "Contact Us", href: "/contact" },
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

        {/* Auth / user area (desktop) */}
        <div className="hidden items-center gap-3 md:flex">
          {currentUser && !userLoading ? (
            <>
              <div className="flex items-center gap-2 rounded-full border border-gray-800 bg-gray-950 px-3 py-1 text-xs text-gray-300">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-900 text-gray-300">
                  <User className="h-3.5 w-3.5" />
                </div>
                <div>
                  <span className="text-gray-500">Hi, </span>
                  <span className="font-semibold text-emerald-300">
                    {(() => {
                      const username = (currentUser.user_metadata && currentUser.user_metadata.username) || ""
                      if (username && typeof username === "string") return username
                      const email: string | undefined = currentUser.email
                      if (email) return email.split("@")[0]
                      return "User"
                    })()}
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={handleSignOut}
                className="rounded-lg border border-gray-800 bg-gray-950 px-3 py-2 text-xs font-semibold tracking-wide text-gray-300 hover:border-red-500/60 hover:text-red-300 hover:bg-gray-900 transition-colors"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link
                href="/auth/login"
                className="rounded-lg border border-gray-800 bg-gray-950 px-3 py-2 text-xs font-semibold tracking-wide text-gray-300 hover:border-gray-700 hover:bg-gray-900 transition-colors"
              >
                Log in
              </Link>
              <Link
                href="/auth/signup"
                className="rounded-lg bg-gradient-to-r from-emerald-500 to-emerald-400 px-4 py-2 text-xs font-semibold tracking-wide text-gray-950 shadow-lg shadow-emerald-500/30 hover:from-emerald-400 hover:to-emerald-300 transition-colors"
              >
                Sign up
              </Link>
            </>
          )}
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
            <div className="mt-2 flex gap-2">
              <Link
                href="/auth/login"
                className="flex-1 rounded-lg border border-gray-800 px-3 py-2 text-center text-xs font-semibold tracking-wide text-gray-300 hover:border-gray-700 hover:bg-gray-900"
                onClick={() => setIsMenuOpen(false)}
              >
                Log in
              </Link>
              <Link
                href="/auth/signup"
                className="flex-1 rounded-lg bg-gradient-to-r from-emerald-500 to-emerald-400 px-3 py-2 text-center text-xs font-semibold tracking-wide text-gray-950"
                onClick={() => setIsMenuOpen(false)}
              >
                Sign up
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
