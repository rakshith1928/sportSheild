export default function ViolationsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Violations</h1>
        <p className="text-slate-400 text-sm mt-1">All detected copyright violations across your assets</p>
      </div>
      <div className="flex items-center justify-center h-64 rounded-xl border border-dashed border-slate-700 bg-[#111415]">
        <div className="text-center space-y-3">
          <span className="material-symbols-outlined text-slate-600 text-5xl block" style={{ fontVariationSettings: "'FILL' 1" }}>travel_explore</span>
          <p className="text-slate-400 font-medium">Violations Drilldown & RAG Legal Context</p>
          <p className="text-slate-600 text-sm">Coming in Phase 6</p>
        </div>
      </div>
    </div>
  )
}
