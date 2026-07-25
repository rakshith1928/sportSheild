'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { ViolationDetails } from '@/utils/api'
import { ViolationDrawer } from './ViolationDrawer'
import { PaginationControls } from '@/components/common/PaginationControls'

interface Props {
  initialViolations: ViolationDetails[]
  totalCount?: number
  currentPage?: number
  currentSeverity?: string
}

// Extracted helper for severity styling
function getSeverityStyles(confidence: number) {
  if (confidence > 90) {
    return {
      textColor: 'text-red-500',
      indicatorColor: 'bg-red-500',
      glowClass: 'group-hover:shadow-[0_0_20px_rgba(239,68,68,0.15)] bg-red-950/20',
      statusBorder: 'border-red-500/50 text-red-500'
    }
  }
  if (confidence > 75) {
    return {
      textColor: 'text-orange-500',
      indicatorColor: 'bg-orange-500',
      glowClass: 'group-hover:shadow-[0_0_20px_rgba(255,255,255,0.05)] bg-[#111415]',
      statusBorder: 'border-slate-700 text-slate-400'
    }
  }
  return {
    textColor: 'text-emerald-500',
    indicatorColor: 'bg-emerald-500',
    glowClass: 'group-hover:shadow-[0_0_20px_rgba(255,255,255,0.05)] bg-[#111415]',
    statusBorder: 'border-slate-700 text-slate-400'
  }
}

export function ViolationsClient({ initialViolations, totalCount, currentPage, currentSeverity }: Props) {
  const router = useRouter()
  const [selectedViolation, setSelectedViolation] = useState<ViolationDetails | null>(null)

  const handleFilter = (severity: string) => {
    if (severity === currentSeverity) {
      router.push('/dashboard/violations')
    } else {
      router.push(`/dashboard/violations?severity=${severity}`)
    }
  }

  // Keyboard accessibility for selecting a card
  const handleKeyDown = (e: React.KeyboardEvent, violation: ViolationDetails) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setSelectedViolation(violation)
    }
  }

  const severities = ['high', 'medium', 'low']

  return (
    <div className="flex-1 flex flex-col relative w-full h-full pb-12">
      {/* HUD Filter Controls */}
      <div className="flex items-center gap-4 mb-6 border-b border-white/10 pb-4">
        <span className="text-slate-500 font-mono text-[10px] tracking-widest uppercase">Filter Matrix</span>
        <div className="flex gap-2">
          {severities.map(sev => {
            const isActive = currentSeverity === sev
            let baseColor, activeClasses
            if (sev === 'high') {
              baseColor = 'border-red-500/20 text-red-500'
              activeClasses = 'bg-red-500/10 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.2)]'
            } else if (sev === 'medium') {
              baseColor = 'border-orange-500/20 text-orange-500'
              activeClasses = 'bg-orange-500/10 border-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.2)]'
            } else {
              baseColor = 'border-emerald-500/20 text-emerald-500'
              activeClasses = 'bg-emerald-500/10 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.2)]'
            }

            return (
              <button
                key={sev}
                onClick={() => handleFilter(sev)}
                className={`
                  px-4 py-1.5 rounded-sm font-mono text-[10px] tracking-widest uppercase transition-all
                  border backdrop-blur-sm
                  ${isActive ? activeClasses : `${baseColor} hover:bg-white/5`}
                `}
              >
                {sev} RISK
              </button>
            )
          })}
        </div>
        {currentSeverity && (
          <button 
            onClick={() => router.push('/dashboard/violations')}
            className="text-slate-400 hover:text-white font-mono text-[10px] tracking-widest ml-auto underline underline-offset-4"
          >
            RESET
          </button>
        )}
      </div>

      {/* Forensic Feed Grid */}
      <div className="flex-1 space-y-4">
        {initialViolations.length === 0 ? (
          <div className="w-full flex-1 min-h-[300px] border border-slate-800/50 bg-[#080A0B] flex flex-col items-center justify-center relative overflow-hidden">
             <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px]"></div>
             <span className="material-symbols-outlined text-4xl text-slate-700 animate-pulse mb-3">radar</span>
             <p className="font-mono text-slate-500 tracking-widest text-xs">NO ANOMALIES DETECTED IN THIS VECTOR</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 perspective-[1000px]">
            {initialViolations.map((violation, idx) => {
              const confidence = Math.round(violation.clip_similarity * 100)
              const styles = getSeverityStyles(confidence)
              
              return (
                <div 
                  key={violation.id} // Enforcing unique DB identifier
                  tabIndex={0}
                  role="button"
                  onClick={() => setSelectedViolation(violation)}
                  onKeyDown={(e) => handleKeyDown(e, violation)}
                  className={`
                    group w-full relative flex items-stretch border border-slate-800/60 rounded-md overflow-hidden cursor-pointer
                    transition-all duration-300 hover:border-slate-600 hover:-translate-y-0.5 focus:outline-none focus:ring-1 focus:ring-white/20
                    ${styles.glowClass}
                  `}
                  style={{ animationDelay: `${idx * 50}ms` }}
                >
                  {/* Left Edge Indicator */}
                  <div className={`w-1 h-auto flex-shrink-0 ${styles.indicatorColor}`}></div>
                  
                  {/* Image Patch */}
                  <div className="w-32 h-24 bg-black relative flex-shrink-0 border-r border-slate-800/60 overflow-hidden group-hover:opacity-80 transition-opacity">
                    <Image 
                      src={violation.image_url} 
                      alt="Violation Evidence" 
                      fill
                      unoptimized
                      className="object-cover mix-blend-luminosity opacity-70 group-hover:mix-blend-normal group-hover:opacity-100 transition-all duration-500" 
                    />
                    {/* Targeting HUD overlay */}
                    <div className="absolute inset-0 border border-[#00FF9D]/30 m-2 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-[#00FF9D]"></div>
                      <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-[#00FF9D]"></div>
                      <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-[#00FF9D]"></div>
                      <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-[#00FF9D]"></div>
                    </div>
                  </div>

                  {/* Core Data */}
                  <div className="flex-1 p-4 flex flex-col justify-center">
                    <div className="flex justify-between items-start mb-2">
                       <h3 className="font-mono text-slate-200 text-sm tracking-wide truncate max-w-lg group-hover:text-white transition-colors">
                          <span className="text-slate-500 mr-2">SOURCE_URL://</span>
                          {violation.page_url.replace(/^https?:\/\//, '')}
                       </h3>
                       <span className="font-mono text-[10px] tracking-wider text-slate-500">
                          {new Date(violation.detected_at).toLocaleString('en-US', { hour12: false })}
                       </span>
                    </div>

                    <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-8 mt-1">
                      <div className="space-y-2 flex-1 max-w-[200px]">
                        <div className="flex justify-between items-baseline mb-1">
                          <span className="block text-[8px] tracking-[0.2em] text-slate-500 uppercase">Confidence</span>
                          <span className={`font-mono text-sm font-bold ${styles.textColor}`}>
                            {confidence}%
                          </span>
                        </div>
                        {/* Visual Progress Bar Add-on */}
                        <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                           <div 
                             className={`h-full ${styles.indicatorColor} transition-all duration-1000 ease-out`}
                             style={{ width: `${confidence}%` }}
                           />
                        </div>
                      </div>
                      
                      <div className="space-y-1 self-start mt-2 sm:mt-0">
                        <span className="block text-[8px] tracking-[0.2em] text-slate-500 uppercase">Assessed Status</span>
                        <span className={`inline-block px-2 py-0.5 border text-[10px] uppercase tracking-wider bg-black/40 ${styles.statusBorder}`}>
                          {violation.is_likely_copy ? 'LIKELY COPY' : 'NEEDS REVIEW'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Action Affordance */}
                  <div className="w-48 bg-slate-900/40 border-l border-slate-800/60 p-4 flex flex-col justify-center items-center group-hover:bg-slate-800/40 transition-colors">
                    <span className="text-[10px] font-mono tracking-widest text-[#FF6B6B] opacity-0 group-hover:opacity-100 transition-opacity mb-2">
                       AWAIT INITIALIZE
                    </span>
                    <span className="material-symbols-outlined text-slate-600 group-hover:text-[#00FF9D] transition-colors">
                      pageview
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Slide-over Legal Drawer */}
      <ViolationDrawer 
        violation={selectedViolation} 
        onClose={() => setSelectedViolation(null)} 
      />

      {/* Pagination Controls */}
      {totalCount !== undefined && currentPage !== undefined && (
        <PaginationControls
          currentPage={currentPage}
          totalItems={totalCount}
          pageSize={10}
          onPageChange={(newPage) => {
            const query = new URLSearchParams()
            if (currentSeverity) query.set('severity', currentSeverity)
            query.set('page', newPage.toString())
            router.push(`/dashboard/violations?${query.toString()}`)
          }}
        />
      )}
    </div>
  )
}
