import AuthForm from '@/components/auth/AuthForm'
import Link from 'next/link'

export const metadata = {
  title: 'Sign In | SportShield AI',
  description: 'Access the SportShield AI Command Center',
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-[#0B0E14] flex flex-col font-sans selection:bg-[#FF6B6B] selection:text-white">
      {/* Minimal Header */}
      <header className="w-full p-6 absolute top-0 left-0 z-10">
        <div className="max-w-screen-2xl mx-auto">
          <Link href="/" className="flex items-center gap-2 w-max group">
            <span className="material-symbols-outlined text-[#FF6B6B] text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>shield</span>
            <span className="text-xl font-bold text-white uppercase tracking-wider group-hover:text-[#FF6B6B] transition-colors">SportShield AI</span>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-6 relative overflow-hidden">
        {/* Abstract Background Elements */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#FF6B6B]/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#901822]/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="w-full z-10 animate-fade-in-up">
          <AuthForm />
        </div>
      </main>
    </div>
  )
}
