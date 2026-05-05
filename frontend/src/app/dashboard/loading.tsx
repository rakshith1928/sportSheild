export default function DashboardLoading() {
  return (
    <div className="space-y-8 animate-pulse">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-8 w-48 bg-white/10 rounded-lg mb-2"></div>
          <div className="h-4 w-64 bg-white/5 rounded-lg"></div>
        </div>
        <div className="h-8 w-32 bg-white/10 rounded-full"></div>
      </div>

      {/* Stats Grid Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 rounded-xl bg-[#111415] border border-white/5 p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="h-4 w-24 bg-white/10 rounded"></div>
              <div className="h-10 w-10 bg-white/10 rounded-lg"></div>
            </div>
            <div className="h-8 w-16 bg-white/10 rounded mt-4"></div>
          </div>
        ))}
      </div>

      {/* Alerts Skeleton */}
      <div className="rounded-xl p-6 bg-[#111415] border border-white/5">
        <div className="flex justify-between mb-6">
          <div className="h-6 w-32 bg-white/10 rounded"></div>
          <div className="h-4 w-16 bg-white/10 rounded"></div>
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex justify-between items-center py-4 border-b border-white/5 last:border-0">
              <div className="space-y-2">
                <div className="h-4 w-64 bg-white/10 rounded"></div>
                <div className="h-3 w-32 bg-white/5 rounded"></div>
              </div>
              <div className="h-6 w-20 bg-white/10 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
