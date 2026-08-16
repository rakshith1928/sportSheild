import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { createClient } from '@/utils/supabase/server'

// Same-origin proxy for the backend's auth-gated report download.
// The backend requires a Bearer token, which a plain <a href> navigation
// cannot carry — this handler attaches the session token server-side and
// streams the PDF back to the browser as an attachment.

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params

  const cookieStore = await cookies()
  const supabase = createClient(cookieStore)
  const { data: { session } } = await supabase.auth.getSession()

  if (!session?.access_token) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  let upstream: Response
  try {
    upstream = await fetch(
      `${API_BASE_URL}/report/download/${encodeURIComponent(id)}`,
      { headers: { Authorization: `Bearer ${session.access_token}` } }
    )
  } catch (error) {
    console.error('Report download proxy failed to reach backend', error)
    return NextResponse.json(
      { detail: 'Backend unavailable' },
      { status: 502 }
    )
  }

  if (!upstream.ok) {
    // 401/403/404 pass through so the UI can react; others degrade to 502
    const status = upstream.status === 401 || upstream.status === 404 ? upstream.status : 502
    return NextResponse.json({ detail: 'Report not available' }, { status })
  }

  const bytes = Buffer.from(await upstream.arrayBuffer())
  return new NextResponse(bytes, {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="sportshield_report_${id}.pdf"`,
    },
  })
}
