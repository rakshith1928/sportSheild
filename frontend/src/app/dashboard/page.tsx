import { cookies } from 'next/headers'
import { createClient } from '@/utils/supabase/server'

export default async function DashboardPage() {
  const cookieStore = await cookies()
  const supabase = createClient(cookieStore)
  const { data: { user } } = await supabase.auth.getUser()

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2 mb-6">
          <span
            className="material-symbols-outlined text-[#FF6B6B] text-4xl"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            shield
          </span>
          <span className="text-2xl font-bold text-white uppercase tracking-wider">
            SportShield AI
          </span>
        </div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400">
          Welcome, <span className="text-[#FF6B6B] font-semibold">{user?.email}</span>
        </p>
        <p className="text-slate-500 text-sm">
          Phase 3 — Static Dashboard layout coming next.
        </p>
      </div>
    </div>
  )
}
