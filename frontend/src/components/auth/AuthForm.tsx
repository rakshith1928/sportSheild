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
    <>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes auth-fade-up {
          from { opacity: 0; transform: translateY(24px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes auth-glow-pulse {
          0%, 100% { box-shadow: 0 0 20px rgba(255,107,107,0.0); }
          50% { box-shadow: 0 0 40px rgba(255,107,107,0.15); }
        }
        @keyframes auth-shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        .auth-card {
          animation: auth-fade-up 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards,
                     auth-glow-pulse 4s ease-in-out infinite 0.7s;
        }
        .auth-field {
          opacity: 0;
          animation: auth-fade-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .auth-field:nth-child(1) { animation-delay: 0.15s; }
        .auth-field:nth-child(2) { animation-delay: 0.25s; }
        .auth-field:nth-child(3) { animation-delay: 0.35s; }
        .auth-field:nth-child(4) { animation-delay: 0.45s; }
        .auth-btn-primary {
          background-size: 200% 100%;
          background-image: linear-gradient(90deg, #FF6B6B 0%, #e85d5d 50%, #FF6B6B 100%);
          transition: all 0.3s ease;
        }
        .auth-btn-primary:hover:not(:disabled) {
          background-position: 100% 0;
          transform: translateY(-1px);
          box-shadow: 0 8px 24px rgba(255,107,107,0.3);
        }
        .auth-btn-primary:active:not(:disabled) {
          transform: translateY(0);
        }
        .auth-input:focus {
          border-color: #FF6B6B !important;
          box-shadow: 0 0 0 3px rgba(255,107,107,0.1);
        }
      `}} />

      <div className="w-full max-w-sm mx-auto p-8 rounded-2xl bg-[#111415] border border-slate-800 auth-card" style={{ opacity: 0 }}>
        {/* Logo — same as Landing Page */}
        <div className="flex items-center gap-2 justify-center mb-8 auth-field">
          <span className="material-symbols-outlined text-[#FF6B6B] text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>shield</span>
          <span className="text-xl font-bold text-white uppercase tracking-wider">SportShield AI</span>
        </div>
        
        <h2 className="text-2xl font-bold text-white mb-2 text-center auth-field">
          Welcome Back
        </h2>
        <p className="text-slate-400 text-sm text-center mb-8 auth-field">
          Enter your credentials to access the command center.
        </p>
        
        <div className="space-y-5">
          <div className="auth-field">
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="auth-input w-full px-4 py-3 bg-[#1d2021] border border-slate-700 text-white rounded-xl focus:outline-none transition-all duration-300"
              placeholder="admin@sportshield.ai"
            />
          </div>
          
          <div className="auth-field">
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input w-full px-4 py-3 bg-[#1d2021] border border-slate-700 text-white rounded-xl focus:outline-none transition-all duration-300"
              placeholder="••••••••"
              onKeyDown={(e) => e.key === 'Enter' && handleAuth(false)}
            />
          </div>

          {error && (
            <div className="auth-field" style={{ animationDelay: '0s', opacity: 1 }}>
              <p className="text-sm text-[#FF6B6B] bg-[#FF6B6B]/10 p-3 rounded-lg border border-[#FF6B6B]/20">{error}</p>
            </div>
          )}
          {message && (
            <div className="auth-field" style={{ animationDelay: '0s', opacity: 1 }}>
              <p className="text-sm text-emerald-400 bg-emerald-400/10 p-3 rounded-lg border border-emerald-400/20">{message}</p>
            </div>
          )}

          <div className="flex flex-col gap-3 pt-4 auth-field">
            <button
              onClick={() => handleAuth(false)}
              disabled={loading || !email || !password}
              className="auth-btn-primary w-full text-white py-3 px-4 rounded-xl font-bold disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                  Authenticating...
                </span>
              ) : 'Sign In'}
            </button>
            
            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t border-slate-700"></div>
              <span className="flex-shrink-0 mx-4 text-slate-500 text-xs uppercase tracking-wider">or</span>
              <div className="flex-grow border-t border-slate-700"></div>
            </div>

            <button
              onClick={() => handleAuth(true)}
              disabled={loading || !email || !password}
              className="w-full bg-transparent border border-slate-700 text-slate-300 py-3 px-4 rounded-xl font-bold hover:bg-slate-800 hover:text-white hover:border-slate-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create New Account
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
