'use client'

import { useEffect } from 'react'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Dashboard Error:', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
      <div className="w-16 h-16 rounded-full bg-[#FF6B6B]/10 flex items-center justify-center">
        <span className="material-symbols-outlined text-[#FF6B6B] text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
          error
        </span>
      </div>
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Something went wrong</h2>
        <p className="text-slate-400 max-w-md mx-auto text-sm">
          We encountered an issue loading your dashboard data. Our systems have logged the error.
        </p>
      </div>
      <button
        onClick={() => reset()}
        className="px-6 py-2.5 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-colors text-sm font-medium border border-white/10"
      >
        Try again
      </button>
    </div>
  )
}
