import { cookies } from 'next/headers'
import { createClient } from '@/utils/supabase/server'
import { StatCard } from '@/components/dashboard/StatCard'
import { AlertRow } from '@/components/dashboard/AlertRow'
import { SeverityBadge } from '@/components/dashboard/SeverityBadge'

// Static data — will be replaced with live API calls in Phase 4
const stats = [
  { label: 'Active Threats', value: '24', change: '+3 today', trend: 'up' as const, icon: 'alert' as const },
  { label: 'Assets Scanned', value: '1,284', change: '+128 this week', trend: 'up' as const, icon: 'scan' as const },
  { label: 'Assets Protected', value: '347', change: '+12 this week', trend: 'down' as const, icon: 'shield' as const },
  { label: 'Takedowns Issued', value: '89', change: '+5 today', trend: 'down' as const, icon: 'lock' as const },
]

const alerts = [
  { id: 1, title: 'Unauthorized broadcast of Champions League highlight reel', source: 'streamhub.net', time: '2 min ago', severity: 'high' as const, status: 'New' },
  { id: 2, title: 'Premier League match clip reposted without license', source: 'vidshare.co', time: '18 min ago', severity: 'high' as const, status: 'New' },
  { id: 3, title: 'Team logo used in unauthorized merchandise listing', source: 'shopify-store-2891.com', time: '1 hr ago', severity: 'medium' as const, status: 'Under Review' },
  { id: 4, title: 'Stadium photo used in news article without attribution', source: 'localnews.in', time: '3 hrs ago', severity: 'low' as const, status: 'Acknowledged' },
  { id: 5, title: 'Match replay segment found on social media', source: 'twitter.com', time: '5 hrs ago', severity: 'medium' as const, status: 'Under Review' },
]

export default async function DashboardPage() {
  const cookieStore = await cookies()
  const supabase = createClient(cookieStore)
  const { data: { user } } = await supabase.auth.getUser()

  return (
    <div className="space-y-8">
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes stat-fade-up {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .stat-card-anim {
          opacity: 0;
          animation: stat-fade-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
      `}} />

      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Protection Overview</h1>
          <p className="text-slate-400 text-sm mt-1">
            Welcome back, <span className="text-[#FF6B6B]">{user?.email}</span>
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Systems Online</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={stat.label} className="stat-card-anim" style={{ animationDelay: `${i * 0.08}s` }}>
            <StatCard {...stat} />
          </div>
        ))}
      </div>

      {/* Recent Alerts */}
      <div
        className="rounded-xl p-6"
        style={{
          backgroundColor: '#111415',
          border: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-white">Recent Alerts</h2>
            <p className="text-slate-500 text-sm mt-0.5">Latest detected violations across monitored assets</p>
          </div>
          <a
            href="/dashboard/violations"
            className="text-sm text-[#FF6B6B] font-medium hover:text-[#e85d5d] transition-colors flex items-center gap-1"
          >
            View all
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </a>
        </div>

        <div>
          {alerts.map((alert, index) => (
            <AlertRow
              key={alert.id}
              alert={alert}
              isLast={index === alerts.length - 1}
            />
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <a
          href="/dashboard/assets"
          className="group flex items-center gap-4 p-5 rounded-xl border border-slate-800 hover:border-[#FF6B6B]/40 bg-[#111415] transition-all duration-300"
        >
          <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center group-hover:bg-[#FF6B6B]/20 transition-colors">
            <span className="material-symbols-outlined text-[#FF6B6B] text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>upload_file</span>
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Upload Asset</p>
            <p className="text-xs text-slate-500">Fingerprint & protect new media</p>
          </div>
        </a>

        <a
          href="/dashboard/violations"
          className="group flex items-center gap-4 p-5 rounded-xl border border-slate-800 hover:border-[#FF6B6B]/40 bg-[#111415] transition-all duration-300"
        >
          <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center group-hover:bg-[#FF6B6B]/20 transition-colors">
            <span className="material-symbols-outlined text-[#FF6B6B] text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>travel_explore</span>
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Scan for Violations</p>
            <p className="text-xs text-slate-500">Run web scan on all assets</p>
          </div>
        </a>

        <a
          href="/dashboard/reports"
          className="group flex items-center gap-4 p-5 rounded-xl border border-slate-800 hover:border-[#FF6B6B]/40 bg-[#111415] transition-all duration-300"
        >
          <div className="w-10 h-10 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center group-hover:bg-[#FF6B6B]/20 transition-colors">
            <span className="material-symbols-outlined text-[#FF6B6B] text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>description</span>
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Generate Report</p>
            <p className="text-xs text-slate-500">Create PDF takedown notice</p>
          </div>
        </a>
      </div>

      {/* Design System Showcase — from Figma */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Actions & Controls */}
        <div className="rounded-xl p-6 bg-[#111415] border border-white/5">
          <h4 className="text-lg font-semibold text-white mb-4">Actions & Controls</h4>
          <div className="space-y-3">
            <button className="w-full px-4 py-3 rounded-lg font-medium text-white text-sm transition-colors hover:opacity-90" style={{ backgroundColor: 'var(--accent-coral)', borderRadius: 'var(--radius-button)' }}>
              Issue Takedown Notice
            </button>
            <button className="w-full px-4 py-3 rounded-lg font-medium text-white text-sm transition-colors hover:opacity-90" style={{ backgroundColor: 'var(--primary-base)', borderRadius: 'var(--radius-button)' }}>
              Start Investigation
            </button>
            <button className="w-full px-4 py-3 rounded-lg font-medium text-sm transition-colors" style={{ backgroundColor: 'transparent', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--surface-white)', borderRadius: 'var(--radius-button)' }}>
              Export Report
            </button>
          </div>
        </div>

        {/* Threat Classification */}
        <div className="rounded-xl p-6 bg-[#111415] border border-white/5">
          <h4 className="text-lg font-semibold text-white mb-4">Threat Classification</h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Critical violations</span>
              <SeverityBadge level="high" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Moderate risk</span>
              <SeverityBadge level="medium" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Minor incidents</span>
              <SeverityBadge level="low" />
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}
