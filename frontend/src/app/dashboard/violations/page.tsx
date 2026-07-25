import { getViolations, ViolationDetails } from '@/utils/api'
import { ViolationsClient } from '@/components/violations/ViolationsClient'

export const dynamic = 'force-dynamic'

type ViolationsSearchParams = {
  severity?: 'high' | 'medium' | 'low' | string
  page?: string
}

export default async function ViolationsPage({
  searchParams,
}: {
  searchParams: ViolationsSearchParams
}) {
  const currentPage = Math.max(1, parseInt(searchParams.page || '1', 10))
  const severity =
    ['high', 'medium', 'low'].includes(searchParams.severity ?? '')
      ? searchParams.severity
      : undefined

  let violationsData: { violations: ViolationDetails[], total: number } = { violations: [], total: 0 }
  let hasError = false

  try {
    const res = await getViolations(severity, currentPage, 10)
    if (res) violationsData = res
  } catch (err) {
    console.error("Dashboard failed to load violations feed:", err)
    hasError = true
  }

  const { violations = [], total = 0 } = violationsData

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-500 tracking-tight">
          THREAT INTELLIGENCE
        </h1>
        <p className="text-[#FF6B6B] font-mono text-xs tracking-[0.2em] mt-1 uppercase">
          Live Forensic Operations Center // {total} Events Detected
        </p>
      </div>

      {hasError && (
        <div className="bg-red-500/10 border border-red-500/30 p-4 rounded text-red-400 font-mono text-sm shadow-[0_0_15px_rgba(239,68,68,0.1)] mb-6">
          <span className="font-bold">SYSTEM ERROR:</span> Failed to query the vector database for violation intelligence.
        </div>
      )}

      <ViolationsClient 
        initialViolations={violations} 
        totalCount={total}
        currentPage={currentPage}
        currentSeverity={severity} 
      />
    </div>
  )
}
