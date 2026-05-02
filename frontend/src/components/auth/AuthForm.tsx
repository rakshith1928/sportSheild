"use client"

import { useState } from 'react'
import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'

export default function AuthForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  
  const router = useRouter()
  const supabase = createClient()

  const handleAuth = async (isSignUp: boolean) => {
    setLoading(true)
    setError(null)
    setMessage(null)
    
    try {
      if (isSignUp) {
        // Sign Up
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${location.origin}/auth/callback`,
          },
        })
        if (error) throw error
        setMessage('Success! Please check your email to verify your account.')
      } else {
        // Sign In
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })
        if (error) throw error
        
        router.push('/dashboard')
        router.refresh()
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during authentication')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-sm mx-auto p-8 rounded-2xl bg-[#111415] border border-slate-800 shadow-2xl">
      <div className="flex justify-center mb-6">
        <div className="w-12 h-12 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center">
          <span className="material-symbols-outlined text-[#FF6B6B]" style={{ fontVariationSettings: "'FILL' 1" }}>shield</span>
        </div>
      </div>
      
      <h2 className="text-2xl font-bold text-white mb-2 text-center">
        Welcome Back
      </h2>
      <p className="text-slate-400 text-sm text-center mb-8">
        Enter your credentials to access the command center.
      </p>
      
      <div className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">Email Address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 bg-[#1d2021] border border-slate-700 text-white rounded-xl focus:outline-none focus:border-[#FF6B6B] focus:ring-1 focus:ring-[#FF6B6B] transition-all"
            placeholder="admin@sportshield.ai"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 bg-[#1d2021] border border-slate-700 text-white rounded-xl focus:outline-none focus:border-[#FF6B6B] focus:ring-1 focus:ring-[#FF6B6B] transition-all"
            placeholder="••••••••"
          />
        </div>

        {error && <p className="text-sm text-[#FF6B6B] bg-[#FF6B6B]/10 p-3 rounded-lg border border-[#FF6B6B]/20">{error}</p>}
        {message && <p className="text-sm text-emerald-400 bg-emerald-400/10 p-3 rounded-lg border border-emerald-400/20">{message}</p>}

        <div className="flex flex-col gap-3 pt-4">
          <button
            onClick={() => handleAuth(false)}
            disabled={loading || !email || !password}
            className="w-full bg-[#FF6B6B] text-white py-3 px-4 rounded-xl font-bold hover:bg-[#e85d5d] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
          
          <div className="relative flex items-center py-2">
            <div className="flex-grow border-t border-slate-700"></div>
            <span className="flex-shrink-0 mx-4 text-slate-500 text-xs uppercase tracking-wider">or</span>
            <div className="flex-grow border-t border-slate-700"></div>
          </div>

          <button
            onClick={() => handleAuth(true)}
            disabled={loading || !email || !password}
            className="w-full bg-transparent border border-slate-700 text-slate-300 py-3 px-4 rounded-xl font-bold hover:bg-slate-800 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Create New Account
          </button>
        </div>
      </div>
    </div>
  )
}
