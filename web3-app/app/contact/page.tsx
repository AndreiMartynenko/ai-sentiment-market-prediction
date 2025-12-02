"use client"

import Link from "next/link"

export default function ContactPage() {
  return (
    <main className="min-h-screen bg-gray-950 text-gray-50">
      <div className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="text-2xl font-semibold text-gray-100">Contact</h1>
        <p className="mt-2 text-sm text-gray-400">
          Get in touch about the ProofOfSignal project, collaboration, or opportunities.
        </p>

        {/* Email section */}
        <section className="mt-8 rounded-2xl border border-gray-900 bg-gray-950/80 p-5">
          <h2 className="text-sm font-semibold text-gray-100">Email us</h2>
          <p className="mt-2 text-xs text-gray-400">
            For questions about the project, research collaboration, or roles, feel free to reach out by email.
          </p>
          <div className="mt-4 space-y-2 text-sm">
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-gray-500">Primary email</div>
              <a
                href="mailto:computersoftwaresolutions@outlook.com"
                className="text-sm font-semibold text-emerald-300 hover:text-emerald-200"
              >
                computersoftwaresolutions@outlook.com
              </a>
            </div>
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-gray-500">Phone</div>
              <a
                href="tel:07869381974"
                className="text-sm font-semibold text-gray-200 hover:text-emerald-200"
              >
                07869 381 974
              </a>
            </div>
          </div>
        </section>

        {/* Visit our office section */}
        <section className="mt-6 rounded-2xl border border-gray-900 bg-gray-950/80 p-5">
          <h2 className="text-sm font-semibold text-gray-100">Visit our office</h2>
          <p className="mt-2 text-xs text-gray-400">
            You can also visit us during business hours at the address below.
          </p>

          <div className="mt-4 grid gap-4 text-xs text-gray-300 sm:grid-cols-2">
            <div>
              <div className="font-medium text-gray-100">Address</div>
              <p className="mt-1 text-gray-400">
                Unit 12 Juno Wy.
                <br />
                London SE14 5RW
                <br />
                United Kingdom
              </p>
            </div>
            <div>
              <div className="font-medium text-gray-100">Business hours</div>
              <p className="mt-1 text-gray-400">
                Monday – Friday: 09:00 – 17:00
                <br />
                Saturday – Sunday: Closed
              </p>
            </div>
          </div>
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
