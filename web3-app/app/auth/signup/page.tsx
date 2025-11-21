"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation"

export default function SignupPage(): React.JSX.Element {
  const [email, setEmail] = useState("")
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    try {
      const raw = typeof window !== "undefined" ? window.localStorage.getItem("pos_users") : null
      const users = raw ? JSON.parse(raw) : []

      const exists = users.some(
        (u: { email: string; username: string }) =>
          u.email.toLowerCase() === email.toLowerCase() ||
          u.username.toLowerCase() === username.toLowerCase(),
      )

      if (exists) {
        setError("User with this email or username already exists.")
        return
      }

      const updatedUsers = [
        ...users,
        {
          email,
          username,
          password,
        },
      ]

      if (typeof window !== "undefined") {
        window.localStorage.setItem("pos_users", JSON.stringify(updatedUsers))
        window.localStorage.setItem("pos_current_user", username)
        window.localStorage.setItem("pos_is_authenticated", "true")
      }

      router.push("/dashboard")
    } catch (e) {
      console.error("signup error", e)
      setError("Something went wrong. Please try again.")
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-10">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-gray-50">
          Create your account
        </h1>
        <p className="mt-2 text-sm text-gray-500">
          Sign up to access the ProofOfSignal trading dashboard.
        </p>
      </div>

      {error && (
        <div className="mb-3 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-300">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-2xl border border-gray-900 bg-gray-950/80 p-6"
      >
        <div className="space-y-1">
          <label
            htmlFor="email"
            className="block text-xs font-medium text-gray-300"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-800 bg-gray-950 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:border-emerald-400 focus:outline-none"
            placeholder="you@example.com"
          />
        </div>

        <div className="space-y-1">
          <label
            htmlFor="username"
            className="block text-xs font-medium text-gray-300"
          >
            Username
          </label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-800 bg-gray-950 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:border-emerald-400 focus:outline-none"
            placeholder="trader42"
          />
        </div>

        <div className="space-y-1">
          <label
            htmlFor="password"
            className="block text-xs font-medium text-gray-300"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-800 bg-gray-950 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:border-emerald-400 focus:outline-none"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          className="mt-2 w-full rounded-lg bg-gradient-to-r from-emerald-500 to-emerald-400 px-4 py-2 text-sm font-semibold text-gray-950 hover:from-emerald-400 hover:to-emerald-300"
        >
          Sign up
        </button>
      </form>
    </div>
  )
}