import { NextResponse } from 'next/server'

const GO_BACKEND_URL = process.env.GO_BACKEND_URL || 'http://localhost:8080'

export const dynamic = 'force-dynamic'

export async function POST(req: Request) {
  try {
    const body = await req.json()

    const res = await fetch(`${GO_BACKEND_URL}/api/v1/signals/institutional/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      cache: 'no-store',
    })

    const text = await res.text()

    if (!res.ok) {
      return NextResponse.json(
        {
          error: 'Backend request failed',
          status: res.status,
          body: text,
        },
        { status: 502 },
      )
    }

    // Forward backend JSON payload as-is.
    return new NextResponse(text, {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (e: any) {
    console.error('Institutional generate proxy error:', e)
    return NextResponse.json(
      {
        error: 'Failed to generate signal',
        go_backend_url: GO_BACKEND_URL,
        details: typeof e?.message === 'string' ? e.message : String(e),
      },
      { status: 500 },
    )
  }
}
