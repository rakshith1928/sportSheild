'use client'

import { useState, useTransition } from 'react'
import Image from 'next/image'
import { ReportMeta, ViolationDetails, generateReport, getAssetViolations, getReports } from '@/utils/api'
import { Asset } from './types'
import { SeverityPill, CompileStep } from './ReportHelpers'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Props {
  initialReports: ReportMeta[]
  assets: Asset[]
}

export function ReportsClient({ initialReports, assets }: Props) {
  const [reports, setReports] = useState<ReportMeta[]>(initialReports)
  const [selectedAssetId, setSelectedAssetId] = useState<string>('')
  const [compileStep, setCompileStep] = useState<number>(0)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  const selectedAsset = assets.find((a) => a.asset_id === selectedAssetId)

  const handleCompile = () => {
    if (!selectedAssetId) {
      setError('Please select an asset to compile a report for.')
      return
    }
    setError(null)

    startTransition(async () => {
      try {
        // Step 1: Fetch violations for this asset
        setCompileStep(1)
        const violationsRes = await getAssetViolations(selectedAssetId)
        const violations: ViolationDetails[] = violationsRes.violations

        if (!violations.length) {
          setError('No violations found for this asset. Run a scan first.')
          setCompileStep(0)
          return
        }

        // Step 2: RAG enrichment + PDF compile (synchronous on backend)
        setCompileStep(2)
        await generateReport(selectedAssetId, violations)

        // Step 3: Refetch from server — ensures timestamps/metadata are accurate
        setCompileStep(3)
        const refreshed = await getReports().catch(() => null)
        if (refreshed) setReports(refreshed.reports)

        setCompileStep(0)
        setSelectedAssetId('')
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Report compilation failed.'
        setError(message)
        setCompileStep(0)
      }
    })
  }

  return (
    <div className="flex-1 flex flex-col gap-8">

      {/* === COMPILE PANEL === */}
      <div className="relative border border-white/8 bg-[#0D0F10] rounded-xl overflow-hidden">
        {/* Scanline texture */}
        <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.3)_50%)] bg-[length:100%_4px] opacity-10 pointer-events-none" />
        
        {/* Header */}
        <div className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-[#FF6B6B] animate-pulse" />
            <span className="font-mono text-xs tracking-[0.2em] text-slate-300 uppercase">
              Compile New Forensic Report
            </span>
          </div>
          <span className="font-mono text-[10px] text-slate-600 tracking-widest">
            RAG + LLM POWERED // FPDF ENGINE
          </span>
        </div>

        <div className="relative z-10 p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Asset Selector */}
          <div className="space-y-4">
            <label className="block text-[10px] font-mono text-slate-500 tracking-[0.2em] uppercase mb-2">
              Select Protected Asset
            </label>

            {assets.length === 0 ? (
              <p className="text-slate-500 font-mono text-xs border border-dashed border-slate-800 p-4 rounded">
                No assets found. Upload and protect an asset first.
              </p>
            ) : (
              <div className="grid grid-cols-1 gap-2 max-h-64 overflow-y-auto pr-1 custom-scrollbar">
                {assets.map((asset) => {
                  const isSelected = asset.asset_id === selectedAssetId
                  return (
                    <button
                      key={asset.asset_id}
                      onClick={() => setSelectedAssetId(isSelected ? '' : asset.asset_id)}
                      className={`
                        group w-full flex items-center gap-3 p-3 rounded-lg border text-left transition-all duration-200
                        ${isSelected
                          ? 'border-[#FF6B6B]/50 bg-[#FF6B6B]/5 shadow-[0_0_15px_rgba(255,107,107,0.1)]'
                          : 'border-slate-800/60 hover:border-slate-600 bg-[#111415]'}
                      `}
                    >
                      <div className="relative w-10 h-10 rounded-md overflow-hidden flex-shrink-0 bg-black border border-slate-800">
                        {asset.content_type?.startsWith('image/') ? (
                          <Image src={asset.file_url} alt={asset.filename} fill unoptimized className="object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <span className="material-symbols-outlined text-slate-600 text-sm">movie</span>
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`font-mono text-xs truncate ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                          {asset.original_filename || asset.filename}
                        </p>
                        <p className="text-[10px] text-slate-600 truncate">{asset.sport} · {asset.team}</p>
                      </div>
                      {isSelected && (
                        <span className="text-[#FF6B6B] flex-shrink-0">
                          <span className="material-symbols-outlined text-sm">check_circle</span>
                        </span>
                      )}
                    </button>
                  )
                })}
              </div>
            )}

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 p-3 rounded text-[11px] font-mono text-red-400">
                <span className="font-bold">ERROR:</span> {error}
              </div>
            )}
          </div>

          {/* Right: Compile Actions + Steps */}
          <div className="flex flex-col justify-between">
            <div className="mb-6">
              <p className="text-[10px] font-mono text-slate-500 tracking-[0.2em] uppercase mb-3">
                Compilation Target
              </p>
              {selectedAsset ? (
                <div className="bg-[#111415] border border-white/5 rounded-lg p-4 font-mono space-y-2">
                  <p className="text-white text-sm font-bold truncate">
                    {selectedAsset.original_filename || selectedAsset.filename}
                  </p>
                  <p className="text-slate-500 text-[10px] tracking-widest">
                    ID: {selectedAsset.asset_id?.substring(0, 16)}...
                  </p>
                  <div className="flex gap-2 flex-wrap mt-2">
                    {selectedAsset.sport && (
                      <span className="px-2 py-0.5 bg-slate-800 text-slate-300 text-[10px] uppercase font-semibold rounded">
                        {selectedAsset.sport}
                      </span>
                    )}
                    {selectedAsset.team && (
                      <span className="px-2 py-0.5 bg-slate-800 text-[#FF6B6B] text-[10px] uppercase font-semibold rounded">
                        {selectedAsset.team}
                      </span>
                    )}
                  </div>
                </div>
              ) : (
                <div className="bg-[#111415] border border-dashed border-slate-800 rounded-lg p-4 text-center">
                  <p className="text-slate-600 font-mono text-xs">No asset selected</p>
                </div>
              )}
            </div>

            {isPending && (
              <div className="space-y-3 mb-6 p-4 bg-[#080A0B] border border-slate-800 rounded-lg">
                <CompileStep step={1} label="FETCHING VIOLATION EVENTS..." active={compileStep === 1} />
                <CompileStep step={2} label="RAG ENRICHMENT + LLM ANALYSIS..." active={compileStep === 2} />
                <CompileStep step={3} label="SYNCING REPORT FROM SERVER..." active={compileStep === 3} />
              </div>
            )}

            <button
              onClick={handleCompile}
              disabled={isPending || !selectedAssetId}
              className={`
                relative w-full py-4 px-6 rounded-lg font-mono text-sm tracking-[0.15em] uppercase font-bold transition-all
                overflow-hidden border group
                ${isPending || !selectedAssetId
                  ? 'border-slate-800 text-slate-600 bg-slate-900/50 cursor-not-allowed'
                  : 'border-[#FF6B6B]/40 text-white bg-[#FF6B6B]/10 hover:bg-[#FF6B6B]/20 hover:border-[#FF6B6B]/70 hover:shadow-[0_0_30px_rgba(255,107,107,0.2)] cursor-pointer'}
              `}
            >
              <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700" />
              <span className="relative flex items-center justify-center gap-3">
                {isPending ? (
                  <>
                    <span className="w-4 h-4 border-2 border-slate-600 border-t-[#FF6B6B] rounded-full animate-spin" />
                    Compiling Report...
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
                    Compile PDF Forensic Report
                  </>
                )}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* === REPORTS ARCHIVE TABLE === */}
      <div className="border border-white/8 bg-[#0D0F10] rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
          <div>
            <span className="font-mono text-xs tracking-[0.2em] text-slate-300 uppercase">
              Generated Reports Archive
            </span>
            <span className="ml-3 font-mono text-[10px] text-slate-600">
              {reports.length} record{reports.length !== 1 ? 's' : ''}
            </span>
          </div>
          <span className="font-mono text-[10px] text-slate-600 tracking-widest">
            SORTED BY // DATE DESC
          </span>
        </div>

        {reports.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 relative overflow-hidden">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:32px_32px]" />
            <span className="material-symbols-outlined text-5xl text-slate-800 mb-4 relative z-10">folder_off</span>
            <p className="font-mono text-slate-600 text-xs tracking-widest relative z-10">NO REPORTS COMPILED YET</p>
            <p className="font-mono text-slate-700 text-[10px] mt-1 relative z-10">Select an asset above and compile your first forensic case file</p>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            <div className="grid grid-cols-[1fr_2fr_1fr_1fr_auto] gap-4 px-6 py-3">
              {['Report ID', 'Asset', 'Violations', 'Compiled At', 'Download'].map((col) => (
                <span key={col} className="font-mono text-[9px] tracking-[0.25em] text-slate-600 uppercase">{col}</span>
              ))}
            </div>

            {reports.map((report, idx) => {
              const assetMeta = assets.find((a) => a.asset_id === report.asset_id)
              const displayName = assetMeta?.original_filename || assetMeta?.filename || 'Unknown Asset'

              return (
                <div
                  key={report.report_id}
                  className="grid grid-cols-[1fr_2fr_1fr_1fr_auto] gap-4 px-6 py-4 items-center hover:bg-white/[0.02] transition-colors"
                  style={{ animationDelay: `${idx * 40}ms` }}
                >
                  <div className="font-mono">
                    <span className="text-xs text-[#00FF9D] tracking-wider font-bold">#{report.report_id}</span>
                  </div>

                  <div className="flex items-center gap-2 min-w-0">
                    <div className="relative w-7 h-7 flex-shrink-0 rounded overflow-hidden border border-slate-800 bg-black">
                      {assetMeta?.content_type?.startsWith('image/') ? (
                        <Image src={assetMeta.file_url} alt={displayName} fill unoptimized className="object-cover opacity-70" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <span className="material-symbols-outlined text-slate-700 text-[12px]">movie</span>
                        </div>
                      )}
                    </div>
                    <span className="font-mono text-xs text-slate-300 truncate">{displayName}</span>
                  </div>

                  <div>
                    <SeverityPill count={report.violations_analyzed} />
                  </div>

                  <div className="font-mono text-[10px] text-slate-500">
                    {new Date(report.created_at).toLocaleString('en-US', {
                      month: 'short', day: '2-digit',
                      hour: '2-digit', minute: '2-digit',
                      hour12: false,
                    })}
                  </div>

                  <a
                    href={`${API_BASE_URL}${report.download_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={`Download report ${report.report_id}`}
                    className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-700 hover:border-[#FF6B6B]/50 hover:bg-[#FF6B6B]/5 rounded font-mono text-[10px] text-slate-400 hover:text-[#FF6B6B] transition-all tracking-wider group"
                  >
                    <span className="material-symbols-outlined text-[14px] group-hover:animate-bounce">download</span>
                    PDF
                  </a>
                </div>
              )
            })}
          </div>
        )}
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
      `}</style>
    </div>
  )
}
