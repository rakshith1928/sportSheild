'use client'

import { useState, useEffect, useRef } from 'react'
import Image from 'next/image'
import { ViolationDetails, ExplainResponse, explainViolation } from '@/utils/api'

interface Props {
  violation: ViolationDetails | null
  onClose: () => void
}

export function ViolationDrawer({ violation, onClose }: Props) {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<ExplainResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const drawerRef = useRef<HTMLDivElement>(null)

  // Focus management for accessibility
  useEffect(() => {
    if (violation && drawerRef.current) {
      drawerRef.current.focus()
    }
  }, [violation])

  // Trigger RAG API call when open
  useEffect(() => {
    if (!violation) return

    let isMounted = true
    const analyze = async () => {
      setLoading(true)
      setData(null)
      setError(null)
      try {
        const response = await explainViolation(violation)
        if (isMounted) setData(response)
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'RAG Analysis disconnected.'
        if (isMounted) setError(message)
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    analyze()

    return () => {
      isMounted = false
    }
  }, [violation])

  const copyTakedown = async () => {
    if (data?.recommended_action) {
       try {
         await navigator.clipboard.writeText(data.recommended_action)
         setCopied(true)
         setTimeout(() => setCopied(false), 2000)
       } catch (err) {
         console.error('Failed to copy to clipboard', err)
         alert('Failed to copy to clipboard. Please copy manually.')
       }
    }
  }

  // Handle ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onClose])

  if (!violation) return null

  const confidenceScore = Math.round(violation.clip_similarity * 100)

  return (
    <>
       {/* Backdrop for click-away */}
       <div 
         className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
         onClick={onClose}
         aria-hidden="true"
       ></div>

       {/* Drawer Panel */}
       <div 
         role="dialog"
         aria-modal="true"
         aria-labelledby="drawer-title"
         ref={drawerRef}
         tabIndex={-1}
         className="fixed top-0 right-0 w-full max-w-2xl h-full bg-[#0B0D0E] border-l border-white/10 shadow-2xl z-50 flex flex-col pt-16 lg:pt-0 transform transition-transform duration-500 animate-slide-in outline-none"
       >
          
          {/* Header */}
          <div className="flex-shrink-0 border-b border-white/10 p-6 flex justify-between items-start bg-[#080A0B] relative overflow-hidden">
             <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.5)_50%)] bg-[length:100%_4px] opacity-20 pointer-events-none"></div>
             <div className="relative z-10 w-full">
                <div className="flex justify-between items-center mb-4">
                   <h2 id="drawer-title" className="font-mono text-xl font-bold text-white tracking-widest uppercase">
                       <span className="text-[#FF6B6B] mr-2">█</span>
                       Forensic Details
                   </h2>
                   <button 
                     onClick={onClose} 
                     aria-label="Close Forensic Details drawer" 
                     className="p-2 hover:bg-white/5 rounded-full text-slate-500 hover:text-white transition-colors"
                   >
                     <span className="material-symbols-outlined">close</span>
                   </button>
                </div>
                <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
                   <span className="bg-slate-800/50 px-2 py-1 rounded">ID: {violation.id?.substring(0,8) || 'UKNWN'}</span>
                   <span>TIMESTAMP: {violation.detected_at}</span>
                </div>
             </div>
          </div>

          {/* Body Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar relative">
             
             {/* Match Evidence Header Section */}
             <div className="bg-[#111415] border border-white/5 p-4 rounded flex flex-col md:flex-row gap-6">
                <div className="w-full md:w-48 h-32 bg-black flex-shrink-0 border border-slate-800 relative group overflow-hidden">
                   <Image 
                     src={violation.image_url} 
                     alt="Violation Evidence matched from scan" 
                     fill 
                     unoptimized
                     className="object-cover opacity-80 group-hover:scale-105 transition-transform duration-500" 
                   />
                   <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-sm border border-slate-700 text-white text-[10px] font-mono px-1.5 py-0.5 rounded-sm tracking-widest font-bold">
                       {confidenceScore}% MATCH
                   </div>
                   {/* Visual Confidence Bar */}
                   <div className="absolute bottom-0 left-0 w-full bg-slate-900/80 h-1.5 backdrop-blur-md">
                     <div 
                       className={`h-full transition-all duration-1000 ease-out ${confidenceScore > 90 ? 'bg-red-500' : confidenceScore > 75 ? 'bg-orange-500' : 'bg-emerald-500'}`}
                       style={{ width: `${confidenceScore}%` }}
                     />
                   </div>
                </div>
                <div className="flex-1 flex flex-col justify-center font-mono">
                   <p className="text-[10px] text-slate-500 tracking-widest uppercase mb-1">Offending URI Origin</p>
                   <p className="text-sm text-[#00FF9D] break-all mb-4">{violation.page_url}</p>
                   
                   <p className="text-[10px] text-slate-500 tracking-widest uppercase mb-1">Algorithm Confidence Context</p>
                   <p className="text-slate-300 text-sm">Visual similarity signature strongly indicates unauthorized replication of asset {violation.asset_id.substring(0,8)}.</p>
                </div>
             </div>

             {/* RAG Engine State */}
             {!data && loading && (
                <div className="space-y-4">
                   <div className="h-6 w-48 bg-[#FF6B6B]/20 animate-pulse rounded border border-[#FF6B6B]/50"></div>
                   <div className="bg-slate-900/50 border border-slate-800 p-6 rounded relative overflow-hidden font-mono text-xs text-[#00FF9D]">
                       <p className="animate-pulse opacity-70">Initializing LangChain RAG pipeline...</p>
                       <p className="mt-1 opacity-50">Querying vector index for relevant copyright law...</p>
                       <p className="mt-1 opacity-30">Generating Llama-3 risk assessment...</p>
                       <div className="absolute bottom-0 left-0 h-1 bg-[#FF6B6B] w-full animate-scan"></div>
                   </div>
                </div>
             )}

             {error && !loading && (
               <div className="bg-red-500/10 border border-red-500/30 p-4 rounded text-red-400 font-mono text-sm shadow-[0_0_15px_rgba(239,68,68,0.1)]">
                 <span className="font-bold">SYSTEM ERROR:</span> {error}
               </div>
             )}

             {data && !loading && (
                <div className="space-y-6 animate-fade-in-up">
                   
                   {/* AI Assessment */}
                   <div>
                       {/* "//" prefix is the intended code-aesthetic header style, not a stray comment */}
                       <h3 className="text-xs font-mono text-slate-500 tracking-[0.2em] uppercase border-b border-white/5 pb-2 mb-4">
                          {'// Automated Legal Assessment'}
                       </h3>
                       <div className={`p-4 rounded border-l-2 bg-[#111415]
                          ${data.severity.toLowerCase() === 'high' ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.05)]' : 
                            data.severity.toLowerCase() === 'medium' ? 'border-orange-500' : 'border-slate-500'}
                       `}>
                          <p className="text-white text-sm leading-relaxed">{data.explanation}</p>
                       </div>
                   </div>

                   {/* Legal Precedents (RAG Context) */}
                   {data.legal_context && data.legal_context.length > 0 && (
                     <div>
                         {/* "//" prefix is the intended code-aesthetic header style, not a stray comment */}
                         <h3 className="text-xs font-mono text-slate-500 tracking-[0.2em] uppercase border-b border-white/5 pb-2 mb-4">
                            {'// Retrieved Legal Context (VDB)'}
                         </h3>
                         <div className="space-y-2">
                            {data.legal_context.map((ctx, idx) => (
                               <div key={idx} className="group bg-slate-900/80 border border-slate-800 p-3 rounded text-xs font-mono text-slate-400 break-words">
                                  <div className="flex items-center justify-between gap-2 mb-2">
                                     <span className="text-[10px] uppercase tracking-[0.2em] text-[#FF6B6B]">{ctx.law}</span>
                                     <span className="text-[10px] text-slate-500 shrink-0">{ctx.source} · {Math.round(ctx.relevance_score * 100)}%</span>
                                  </div>
                                  <p className="whitespace-pre-wrap line-clamp-3 group-hover:line-clamp-none transition-all">{ctx.content}</p>
                               </div>
                            ))}
                         </div>
                     </div>
                   )}

                   {/* DMCA Letter Output */}
                   <div>
                       <div className="flex justify-between items-end border-b border-white/5 pb-2 mb-4">
                         {/* "//" prefix is the intended code-aesthetic header style, not a stray comment */}
                         <h3 className="text-xs font-mono text-slate-500 tracking-[0.2em] uppercase">
                            {'// Drafted Takedown Notice'}
                         </h3>
                         <button 
                           onClick={copyTakedown}
                           aria-label="Copy generated takedown notice text to clipboard"
                           className="flex items-center gap-1.5 px-3 py-1 bg-white/5 hover:bg-white/10 text-white rounded text-[10px] font-mono tracking-widest uppercase transition-colors border border-white/10"
                         >
                            <span className="material-symbols-outlined text-[14px]">
                              {copied ? 'check' : 'content_copy'}
                            </span>
                            {copied ? 'Copied' : 'Copy Text'}
                         </button>
                       </div>
                       <div className="bg-[#0A0A0A] border border-slate-800 rounded p-4 font-mono text-sm text-slate-300 whitespace-pre-wrap leading-relaxed shadow-inner overflow-x-auto selection:bg-[#FF6B6B]/30">
                          {data.recommended_action}
                       </div>
                   </div>

                </div>
             )}
          </div>
       </div>
       
       <style jsx global>{`
          .animate-slide-in {
             animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          }
          .animate-fade-in-up {
             animation: fadeInUp 0.5s ease-out forwards;
          }
          .animate-scan {
             animation: scanLine 2s linear infinite;
          }
          .custom-scrollbar::-webkit-scrollbar {
             width: 6px;
          }
          .custom-scrollbar::-webkit-scrollbar-track {
             background: transparent;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb {
             background: #334155;
             border-radius: 10px;
          }
          @keyframes slideIn {
             from { transform: translateX(100%); }
             to { transform: translateX(0); }
          }
          @keyframes fadeInUp {
             from { opacity: 0; transform: translateY(10px); }
             to { opacity: 1; transform: translateY(0); }
          }
          @keyframes scanLine {
             0% { width: 0%; left: 0; }
             50% { width: 100%; left: 0; opacity: 1; }
             50.1% { width: 100%; left: auto; right: 0; }
             100% { width: 0%; left: auto; right: 0; opacity: 0; }
          }
       `}</style>
    </>
  )
}
