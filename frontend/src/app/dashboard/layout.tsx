import { redirect } from 'next/navigation'
import { cookies } from 'next/headers'
import { createClient } from '@/utils/supabase/server'
import TopBar from '@/components/dashboard/TopBar'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Server-side session check — second layer of protection beyond middleware
  const cookieStore = await cookies()
  const supabase = createClient(cookieStore)
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <div className="min-h-screen bg-[#0B0E14] text-slate-200 font-sans">
      <TopBar userEmail={user.email ?? null} />
      <main className="max-w-screen-2xl mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  )
}
