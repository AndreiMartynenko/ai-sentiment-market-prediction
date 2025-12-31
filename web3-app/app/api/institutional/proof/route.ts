import { NextResponse } from 'next/server'

const GO_BACKEND_URL = process.env.GO_BACKEND_URL || 'http://localhost:8080'

export const dynamic = 'force-dynamic'

export async function POST(req: Request) {
  try {
    const body = await req.json()

    const res = await fetch(`${GO_BACKEND_URL}/api/v1/proof/mock`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      cache: 'no-store',
    })

    const text = await res.text()
    if (!res.ok) {
      return NextResponse.json({ error: 'Gateway request failed', status: res.status, body: text }, { status: 502 })
    }

    return new NextResponse(text, { status: 200, headers: { 'Content-Type': 'application/json' } })
  } catch (e: any) {
    console.error('Institutional proof proxy error:', e)
    return NextResponse.json(
      {
        error: 'Failed to publish proof',
        details: typeof e?.message === 'string' ? e.message : String(e),
      },
      { status: 500 },
    )
  }
}
