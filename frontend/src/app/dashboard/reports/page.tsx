import { getReports, getAssets, ReportsResponse } from '@/utils/api'
import { ReportsClient } from '@/components/reports/ReportsClient'
import { Asset } from '@/components/reports/types'

export const dynamic = 'force-dynamic'

interface AssetsResponse {
  total: number
  assets: Asset[]
}

export default async function ReportsPage() {
  const [reportsData, assetsData] = await Promise.all([
    getReports().catch((): ReportsResponse => ({ total: 0, reports: [] })),
    getAssets().catch((): AssetsResponse => ({ total: 0, assets: [] })),
  ])

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
