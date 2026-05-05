"use client"

import { useState } from 'react'
import Link from 'next/link'
import { createClient } from '@/utils/supabase/client'
import { useRouter } from 'next/navigation'

interface TopBarProps {
  userEmail: string | null
}

export default function TopBar({ userEmail }: TopBarProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const router = useRouter()
  const supabase = createClient()

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  // Get initials from email (e.g. "john@example.com" → "JO")
  const initials = userEmail
    ? userEmail.substring(0, 2).toUpperCase()
    : 'AI'

  return (
    <header className="bg-[#0B0E14]/90 backdrop-blur-md border-b border-white/5 sticky top-0 z-50">
      <div className="flex justify-between items-center w-full px-6 py-4 max-w-screen-2xl mx-auto">

        {/* Logo — identical to landing page */}
        <Link href="/dashboard" className="flex items-center gap-2 group">
          <span
            className="material-symbols-outlined text-[#FF6B6B] text-2xl transition-transform group-hover:scale-110"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            shield
          </span>
          <span className="text-xl font-bold text-white uppercase tracking-wider group-hover:text-[#FF6B6B] transition-colors">
            SportShield AI
          </span>
        </Link>

        {/* Nav Links */}
        <nav className="hidden md:flex items-center gap-8">
          <Link href="/dashboard" className="text-slate-400 font-medium hover:text-[#FF6B6B] transition-colors duration-300">
            Overview
          </Link>
          <Link href="/dashboard/assets" className="text-slate-400 font-medium hover:text-[#FF6B6B] transition-colors duration-300">
            Assets
          </Link>
          <Link href="/dashboard/violations" className="text-slate-400 font-medium hover:text-[#FF6B6B] transition-colors duration-300">
            Violations
          </Link>
          <Link href="/dashboard/reports" className="text-slate-400 font-medium hover:text-[#FF6B6B] transition-colors duration-300">
            Reports
          </Link>
        </nav>

        {/* Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-3 group"
          >
            {/* Avatar Circle */}
            <div className="w-9 h-9 rounded-full bg-[#FF6B6B] flex items-center justify-center text-white text-sm font-bold group-hover:ring-2 group-hover:ring-[#FF6B6B]/50 transition-all">
              {initials}
            </div>
            {/* Chevron */}
            <svg
              className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <>
              {/* Backdrop to close on outside click */}
              <div
                className="fixed inset-0 z-40"
                onClick={() => setDropdownOpen(false)}
              />
              <div className="absolute right-0 mt-3 w-56 rounded-xl bg-[#1d2021] border border-slate-700 shadow-2xl z-50 overflow-hidden animate-fade-in-up">
                {/* User info */}
                <div className="px-4 py-3 border-b border-slate-700">
                  <p className="text-xs text-slate-500 uppercase tracking-wider">Signed in as</p>
                  <p className="text-sm text-white font-medium truncate mt-1">{userEmail}</p>
                </div>

                {/* Menu Items */}
                <div className="py-1">
                  <Link
                    href="/dashboard/settings"
                    onClick={() => setDropdownOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
                  >
                    <span className="material-symbols-outlined text-base" style={{ fontVariationSettings: "'FILL' 0" }}>settings</span>
                    Profile Settings
                  </Link>
                  <Link
                    href="/dashboard/reports"
                    onClick={() => setDropdownOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
                  >
                    <span className="material-symbols-outlined text-base" style={{ fontVariationSettings: "'FILL' 0" }}>description</span>
                    My Reports
                  </Link>
                </div>

                {/* Logout */}
                <div className="border-t border-slate-700 py-1">
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-[#FF6B6B] hover:bg-[#FF6B6B]/10 transition-colors w-full text-left"
                  >
                    <span className="material-symbols-outlined text-base" style={{ fontVariationSettings: "'FILL' 0" }}>logout</span>
                    Log Out
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
