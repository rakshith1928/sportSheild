// Severity badge for violation count
export function SeverityPill({ count }: { count: number }) {
  const color = count > 5
    ? 'text-red-400 border-red-500/30 bg-red-500/10'
    : count > 2
    ? 'text-orange-400 border-orange-500/30 bg-orange-500/10'
    : 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm border font-mono text-[10px] tracking-widest ${color}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      {count} VIOLATIONS
    </span>
  )
}

// Animated compilation step indicator
export function CompileStep({ step, label, active }: { step: number; label: string; active: boolean }) {
  return (
    <div className={`flex items-center gap-3 transition-all duration-500 ${active ? 'opacity-100' : 'opacity-30'}`}>
      <div className={`w-6 h-6 rounded-full border flex items-center justify-center text-[10px] font-mono
        ${active ? 'border-[#FF6B6B] text-[#FF6B6B] bg-[#FF6B6B]/10 animate-pulse' : 'border-slate-700 text-slate-500'}`}>
        {step}
      </div>
      <span className={`font-mono text-xs tracking-wider ${active ? 'text-white' : 'text-slate-500'}`}>{label}</span>
    </div>
  )
}
