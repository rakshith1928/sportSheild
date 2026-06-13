import { createClient } from '@/utils/supabase/server'
import { cookies } from 'next/headers'

// Fallback to localhost if env variable is missing
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
