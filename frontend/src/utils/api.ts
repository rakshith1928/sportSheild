import { createClient } from '@/utils/supabase/server'
import { cookies } from 'next/headers'

// Fallback to localhost if env variable is missing
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ---------------------------------------------------------
// TypeScript Definitions (Phase 6 endpoints strongly typed)
// ---------------------------------------------------------
export interface ViolationDetails {
  id?: string
  asset_id: string
  image_url: string
  page_url: string
  clip_similarity: number
  match_text?: string
  is_likely_copy: boolean
  detected_at: string
}

export interface ExplainResponse {
  success: boolean
  severity: string
  explanation: string
  legal_context: string[]
  recommended_action: string
}

export interface GenerateReportResponse {
  success: boolean
  report_id: string
  download_url: string
  violations_analyzed: number
}

export interface ReportMeta {
  report_id: string
  asset_id: string
  download_url: string
  violations_analyzed: number
  created_at: string
}

export interface ReportsResponse {
  total: number
  reports: ReportMeta[]
}

/**
 * Server-side API fetcher.
 * Automatically injects the Supabase user session token into the Authorization header
 * so the FastAPI backend can verify the user.
 */
export async function fetchApi(endpoint: string, options: RequestInit = {}) {
  // 1. Get the session token from Supabase cookies
  const cookieStore = await cookies()
  const supabase = createClient(cookieStore)
  const { data: { session } } = await supabase.auth.getSession()

  // 2. Prepare headers
  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  
  // 3. Attach the Bearer token if the user is logged in
  if (session?.access_token) {
    headers.set('Authorization', `Bearer ${session.access_token}`)
  }

  // 4. Construct full URL and make the fetch call
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
  
  const response = await fetch(url, {
    ...options,
    headers,
  })

  // 5. Handle HTTP errors gracefully
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`API Error (${response.status}): ${errorText}`)
  }

  return response.json()
}

// ---------------------------------------------------------
// Specific Endpoint Fetchers (Phase 4 Mappings)
// ---------------------------------------------------------

export async function getDashboardStats() {
  // This points to a FastAPI route that we will create/update
  // For now, we wrap it in a try/catch so the UI doesn't crash if the backend is off
  try {
    return await fetchApi('/dashboard/stats')
  } catch (error) {
    console.error("Failed to fetch stats, returning fallback data", error)
    return null
  }
}

export async function getRecentAlerts() {
  try {
    return await fetchApi('/scan/alerts?limit=5')
  } catch (error) {
    console.error("Failed to fetch alerts, returning fallback data", error)
    return []
  }
}

export async function getAssets() {
  try {
    return await fetchApi('/upload/assets')
  } catch (error) {
    console.error("Failed to fetch assets", error)
    return { total: 0, assets: [] }
  }
}

export async function uploadAsset(formData: FormData) {
  try {
    return await fetchApi('/upload/asset', {
      method: 'POST',
      body: formData,
    })
  } catch (error) {
    console.error("Failed to upload asset", error)
    throw error
  }
}

// ---------------------------------------------------------
// Phase 6 Mappings (RAG & Violations)
// ---------------------------------------------------------

export async function getViolations(
  severity?: string
): Promise<{ total: number; violations: ViolationDetails[] }> {
  try {
    const query = severity ? `?severity=${encodeURIComponent(severity)}` : ''
    return await fetchApi(`/scan/violations${query}`)
  } catch (error) {
    console.error("Failed to fetch violations", error)
    return { total: 0, violations: [] }
  }
}

export async function getAssetViolations(
  assetId: string
): Promise<{ asset_id: string; total: number; violations: ViolationDetails[] }> {
  try {
    return await fetchApi(`/scan/violations/${encodeURIComponent(assetId)}`)
  } catch (error) {
    console.error("Failed to fetch asset violations", error)
    return { asset_id: assetId, total: 0, violations: [] }
  }
}

export async function explainViolation(
  violationData: ViolationDetails
): Promise<ExplainResponse> {
  try {
    return await fetchApi('/explain/violation', {
      method: 'POST',
      body: JSON.stringify(violationData)
    })
  } catch (error) {
    console.error("Failed to explain violation", error)
    throw error // Re-throw to allow component boundary handling
  }
}

export async function generateReport(
  assetId: string,
  violations: ViolationDetails[]
): Promise<GenerateReportResponse> {
  try {
    return await fetchApi('/report/generate', {
      method: 'POST',
      body: JSON.stringify({ asset_id: assetId, violations })
    })
  } catch (error) {
    console.error("Failed to generate report", error)
    throw error
  }
}

export async function getReports(): Promise<ReportsResponse> {
  try {
    return await fetchApi('/report/list')
  } catch (error) {
    console.error("Failed to fetch reports", error)
    return { total: 0, reports: [] }
  }
}
