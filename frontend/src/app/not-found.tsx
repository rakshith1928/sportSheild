import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#0B0E14] flex flex-col items-center justify-center text-center p-6 font-sans">
      <div className="mb-8">
        <span className="material-symbols-outlined text-[#FF6B6B] text-6xl mb-4 opacity-80" style={{ fontVariationSettings: "'FILL' 1" }}>
          sports_score
        </span>
        <h1 className="text-6xl font-black text-white tracking-tighter mb-2">404</h1>
        <h2 className="text-2xl font-bold text-slate-200 mb-4">Page out of bounds</h2>
        <p className="text-slate-400 max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved. Let's get you back in the game.
        </p>
      </div>
      
      <Link 
        href="/"
        className="px-6 py-3 bg-[#FF6B6B] hover:bg-[#ff5252] text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
      >
        <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>home</span>
        Return to Base
      </Link>
    </div>
  )
}
