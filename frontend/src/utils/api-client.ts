// Browser-side API client.
//
// utils/api.ts is SERVER-ONLY: its fetcher reads the Supabase session via
// next/headers cookies(), which throws when invoked in the browser. The
// interactive client components (ReportsClient, ViolationDrawer) call the
// backend from event handlers, so they must go through this module, which
// gets the session from the browser Supabase SDK instead.
//
// Types are imported type-only so the server module is never bundled.

import { createClient } from '@/utils/supabase/client'
import type {
  ViolationDetails,
  ExplainResponse,
  GenerateReportResponse,
  JobStatusResponse,
  ReportsResponse,
} from '@/utils/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchApiClient(endpoint: string, options: RequestInit = {}) {
  const supabase = createClient()
  const { data: { session } } = await supabase.auth.getSession()

  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (session?.access_token) {
    headers.set('Authorization', `Bearer ${session.access_token}`)
  }

  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
  const response = await fetch(url, { ...options, headers })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`API Error (${response.status}): ${errorText}`)
  }
  return response.json()
}

export async function explainViolation(
  violationData: ViolationDetails
): Promise<ExplainResponse> {
  try {
    return await fetchApiClient('/explain/violation', {
      method: 'POST',
      body: JSON.stringify(violationData)
    })
  } catch (error) {
    console.error("Failed to explain violation", error)
    throw error
  }
}

export async function getAssetViolations(
  assetId: string,
  page = 1,
  limit = 50
): Promise<{ asset_id: string; total: number; violations: ViolationDetails[] }> {
  try {
    const offset = (page - 1) * limit
    return await fetchApiClient(`/scan/violations/${encodeURIComponent(assetId)}?limit=${limit}&offset=${offset}`)
  } catch (error) {
    console.error("Failed to fetch asset violations", error)
    return { asset_id: assetId, total: 0, violations: [] }
  }
}

export async function generateReport(
  assetId: string,
  violations: ViolationDetails[]
): Promise<GenerateReportResponse> {
  try {
    return await fetchApiClient('/report/generate', {
      method: 'POST',
      body: JSON.stringify({ asset_id: assetId, violations })
    })
  } catch (error) {
    console.error("Failed to generate report", error)
    throw error
  }
}

export async function getReportJobStatus(jobId: string): Promise<JobStatusResponse> {
  try {
    return await fetchApiClient(`/report/status/${encodeURIComponent(jobId)}`)
  } catch (error) {
    console.error(`Failed to fetch job status for ${jobId}`, error)
    throw error
  }
}

export async function getReports(page = 1, limit = 50): Promise<ReportsResponse> {
  try {
    const offset = (page - 1) * limit
    return await fetchApiClient(`/report/list?limit=${limit}&offset=${offset}`)
  } catch (error) {
    console.error("Failed to fetch reports", error)
    return { total: 0, reports: [] }
  }
}
