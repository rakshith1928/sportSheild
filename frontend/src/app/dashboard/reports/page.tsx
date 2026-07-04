import { getReports, getAssets, ReportsResponse } from '@/utils/api'
import { ReportsClient } from '@/components/reports/ReportsClient'

export const dynamic = 'force-dynamic'

export default async function ReportsPage() {
  let reportsData: ReportsResponse = { total: 0, reports: [] }
  let assetsData: { total: number; assets: any[] } = { total: 0, assets: [] }

  try {
    const [reports, assets] = await Promise.all([getReports(), getAssets()])
    if (reports) reportsData = reports
    if (assets) assetsData = assets
  } catch (err) {
    console.error('Failed to load reports data:', err)
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-500 tracking-tight">
          CASE REPORT CENTER
        </h1>
        <p className="text-[#FF6B6B] font-mono text-xs tracking-[0.2em] mt-1 uppercase">
          Forensic PDF Compilation Engine // {reportsData.total} Reports Generated
        </p>
      </div>

      <ReportsClient
        initialReports={reportsData.reports}
        assets={assetsData.assets}
      />
    </div>
  )
}
