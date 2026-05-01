"use client"

import React, { useEffect } from 'react'
import Link from 'next/link'

export default function LandingPage() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('active')
          }
        })
      },
      { threshold: 0.1 }
    )

    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el))

    return () => observer.disconnect()
  }, [])

  return (
    <>
      <style dangerouslySetInnerHTML={{__html: `
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .coral-accent { color: #FF6B6B; }
        .bg-coral-accent { background-color: #FF6B6B; }
        .border-coral-accent { border-color: #FF6B6B; }
        
        @keyframes slide-infinite {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        .animate-carousel {
            display: flex;
            width: max-content;
            animation: slide-infinite 40s linear infinite;
        }
        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .reveal.active {
            opacity: 1;
            transform: translateY(0);
        }
      `}} />
      
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />

      <div className="bg-[#0B0E14] text-slate-200 selection:bg-[#FF6B6B] selection:text-white min-h-screen flex flex-col font-sans">
        {/* TopNavBar */}
        <header className="bg-[#0B0E14]/80 backdrop-blur-md w-full top-0 z-50 border-b border-white/5 sticky">
          <div className="flex justify-between items-center w-full px-6 py-4 max-w-screen-2xl mx-auto tracking-tight">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#FF6B6B] text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>shield</span>
              <span className="text-xl font-bold text-white uppercase tracking-wider">SportShield AI</span>
            </div>
            <nav className="hidden md:flex items-center gap-8">
              <Link href="#" className="text-slate-400 font-medium hover:text-[#FF6B6B] transition-all duration-300">Solutions</Link>
              <Link href="#" className="text-slate-400 font-medium hover:text-[#FF6B6B] transition-all duration-300">Technology</Link>
              <Link href="#" className="text-slate-400 font-medium hover:text-[#FF6B6B] transition-all duration-300">Compliance</Link>
              <Link href="#" className="text-slate-400 font-medium hover:text-[#FF6B6B] transition-all duration-300">Pricing</Link>
            </nav>
            <Link href="/dashboard" className="bg-[#FF6B6B] text-white px-6 py-2 rounded-lg font-bold hover:scale-105 active:scale-95 transform transition-all duration-300">
              Request Demo
            </Link>
          </div>
        </header>

        <main className="flex-1">
          {/* Hero Section */}
          <section className="relative pt-24 pb-48 overflow-hidden bg-[#0B0E14]">
            <div className="max-w-7xl mx-auto px-6 text-center">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#901822]/20 border border-[#901822]/30 mb-8">
                <span className="w-2 h-2 rounded-full bg-coral-accent animate-pulse"></span>
                <span className="text-[12px] font-semibold tracking-wider text-[#ffb3b0] uppercase">Enterprise Grade Intelligence</span>
              </div>
              <h1 className="text-4xl md:text-7xl font-bold text-white mb-8 max-w-5xl mx-auto leading-tight tracking-tight">
                Securing the Future of <span className="coral-accent">Global Sports Rights</span>
              </h1>
              <p className="text-lg text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
                Combat piracy and protect your digital assets with autonomous AI fingerprinting and real-time automated takedown protocols.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-24">
                <button className="bg-coral-accent text-white px-10 py-5 rounded-xl font-bold text-lg hover:shadow-[0_0_30px_rgba(255,107,107,0.3)] transition-all">Start Free Audit</button>
                <button className="bg-transparent border border-slate-700 text-white px-10 py-5 rounded-xl font-bold text-lg hover:bg-slate-800 transition-all">View Case Studies</button>
              </div>

              {/* Modern Feature Showcase around Hero Image */}
              <div className="relative max-w-7xl mx-auto px-4 md:px-0 mt-28 overflow-hidden">
                <div className="animate-carousel">
                  {/* Original set */}
                  <div className="flex gap-6 pr-6">
                    <div className="relative w-[400px] shrink-0">
                      <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-lg bg-[#191c1d] p-1 group hover:border-[#FF6B6B]/30 transition-all duration-500">
                        <img alt="High-performance sports action" className="w-full rounded-xl object-cover aspect-[16/9]" src="/images/footbal.jpg" />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0B0E14]/60 via-transparent to-transparent"></div>
                      </div>
                    </div>
                    <div className="relative w-[400px] shrink-0">
                      <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-lg bg-[#191c1d] p-1 group hover:border-[#FF6B6B]/30 transition-all duration-500">
                        <img alt="Stadium Action" className="w-full rounded-xl object-cover aspect-[16/9]" src="/images/GettyImages-2219813002.jpg.webp" />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0B0E14]/60 via-transparent to-transparent"></div>
                      </div>
                    </div>
                    <div className="relative w-[400px] shrink-0">
                      <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-lg bg-[#191c1d] p-1 group hover:border-[#FF6B6B]/30 transition-all duration-500">
                        <img alt="Championship Celebration" className="w-full rounded-xl object-cover aspect-[16/9]" src="/images/cn6ocva_perth-scorchers-bbl-2023-afp_625x300_04_February_23%20(1).webp" />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0B0E14]/60 via-transparent to-transparent"></div>
                      </div>
                    </div>
                  </div>
                  {/* Duplicated set for seamless loop */}
                  <div className="flex gap-6 pr-6">
                    <div className="relative w-[400px] shrink-0">
                      <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-lg bg-[#191c1d] p-1 group hover:border-[#FF6B6B]/30 transition-all duration-500">
                        <img alt="High-performance sports action" className="w-full rounded-xl object-cover aspect-[16/9]" src="/images/footbal.jpg" />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0B0E14]/60 via-transparent to-transparent"></div>
                      </div>
                    </div>
                    <div className="relative w-[400px] shrink-0">
                      <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-lg bg-[#191c1d] p-1 group hover:border-[#FF6B6B]/30 transition-all duration-500">
                        <img alt="Stadium Action" className="w-full rounded-xl object-cover aspect-[16/9]" src="/images/GettyImages-2219813002.jpg.webp" />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0B0E14]/60 via-transparent to-transparent"></div>
                      </div>
                    </div>
                    <div className="relative w-[400px] shrink-0">
                      <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-lg bg-[#191c1d] p-1 group hover:border-[#FF6B6B]/30 transition-all duration-500">
                        <img alt="Championship Celebration" className="w-full rounded-xl object-cover aspect-[16/9]" src="/images/cn6ocva_perth-scorchers-bbl-2023-afp_625x300_04_February_23%20(1).webp" />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0B0E14]/60 via-transparent to-transparent"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Features Bento Grid */}
          <section className="py-24 bg-[#0c0f10]">
            <div className="max-w-7xl mx-auto px-6">
              <div className="text-center mb-16 reveal">
                <h2 className="text-3xl font-bold text-white mb-4">Command Center Capabilities</h2>
                <p className="text-slate-400 text-lg">Integrated security tools for the modern digital rights landscape.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-[#1d2021] p-6 rounded-xl border border-slate-800/50 hover:border-[#FF6B6B]/50 transition-colors group reveal">
                  <div className="w-12 h-12 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center mb-6 group-hover:bg-[#FF6B6B]/20 transition-colors">
                    <span className="material-symbols-outlined coral-accent" style={{ fontVariationSettings: "'FILL' 1" }}>fingerprint</span>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">AI Fingerprinting</h3>
                  <p className="text-sm text-slate-400 mb-6">Inject invisible, forensic watermarks into every stream to trace leaks back to the precise subscriber source within seconds.</p>
                  <div className="flex items-center text-[#FF6B6B] font-bold gap-1 cursor-pointer hover:gap-2 transition-all">
                    Learn more <span className="material-symbols-outlined text-sm">arrow_forward</span>
                  </div>
                </div>
                <div className="bg-[#1d2021] p-6 rounded-xl border border-slate-800/50 hover:border-[#FF6B6B]/50 transition-colors group reveal">
                  <div className="w-12 h-12 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center mb-6 group-hover:bg-[#FF6B6B]/20 transition-colors">
                    <span className="material-symbols-outlined coral-accent" style={{ fontVariationSettings: "'FILL' 1" }}>travel_explore</span>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">Global Web Scanning</h3>
                  <p className="text-sm text-slate-400 mb-6">Autonomous spiders scan indexed sites, social media, and pirate IPTV networks 24/7 to identify illegal re-broadcasts.</p>
                  <div className="flex items-center text-[#FF6B6B] font-bold gap-1 cursor-pointer hover:gap-2 transition-all">
                    Learn more <span className="material-symbols-outlined text-sm">arrow_forward</span>
                  </div>
                </div>
                <div className="bg-[#1d2021] p-6 rounded-xl border border-slate-800/50 hover:border-[#FF6B6B]/50 transition-colors group reveal">
                  <div className="w-12 h-12 rounded-lg bg-[#FF6B6B]/10 flex items-center justify-center mb-6 group-hover:bg-[#FF6B6B]/20 transition-colors">
                    <span className="material-symbols-outlined coral-accent" style={{ fontVariationSettings: "'FILL' 1" }}>gavel</span>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">Automated Takedowns</h3>
                  <p className="text-sm text-slate-400 mb-6">Instantly trigger DMCA notices and ISP block requests. AI-driven legal protocols resolve threats without human intervention.</p>
                  <div className="flex items-center text-[#FF6B6B] font-bold gap-1 cursor-pointer hover:gap-2 transition-all">
                    Learn more <span className="material-symbols-outlined text-sm">arrow_forward</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Stats Section */}
          <section className="py-20 bg-[#0B0E14]">
            <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <p className="text-4xl font-bold text-white">99.8%</p>
                <p className="text-xs font-semibold tracking-wider text-slate-500 uppercase mt-2">Detection Rate</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-bold text-white">12s</p>
                <p className="text-xs font-semibold tracking-wider text-slate-500 uppercase mt-2">Avg Response Time</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-bold text-white">4M+</p>
                <p className="text-xs font-semibold tracking-wider text-slate-500 uppercase mt-2">Daily Scans</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-bold text-white">$2B+</p>
                <p className="text-xs font-semibold tracking-wider text-slate-500 uppercase mt-2">Revenue Protected</p>
              </div>
            </div>
          </section>

          {/* Dashboard Preview Banner */}
          <section className="py-24 bg-[#0c0f10] border-y border-slate-800">
            <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center gap-12">
              <div className="flex-1 reveal">
                <h2 className="text-4xl font-bold text-white mb-6">Total Visual Control</h2>
                <p className="text-lg text-slate-400 mb-8">Manage your entire IP portfolio from a single, unified command center designed for rapid decision-making.</p>
                <ul className="space-y-4">
                  <li className="flex items-center gap-3 text-white">
                    <span className="material-symbols-outlined coral-accent">check_circle</span>
                    Real-time heatmaps of pirate activity
                  </li>
                  <li className="flex items-center gap-3 text-white">
                    <span className="material-symbols-outlined coral-accent">check_circle</span>
                    One-click legal escalation
                  </li>
                  <li className="flex items-center gap-3 text-white">
                    <span className="material-symbols-outlined coral-accent">check_circle</span>
                    Comprehensive audit trails for litigation
                  </li>
                </ul>
              </div>
              <div className="flex-1 w-full reveal">
                <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-[#111415]">
                  <img alt="Command Center Dashboard" className="w-full h-full object-cover" src="/images/Screenshot%202026-05-01%20125331.png" />
                </div>
              </div>
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="bg-[#0B0E14] w-full border-t border-slate-800/50">
          <div className="flex flex-col md:flex-row justify-between items-center w-full px-8 py-12 gap-6 max-w-screen-2xl mx-auto text-sm">
            <div className="flex flex-col gap-4">
              <span className="text-lg font-black text-white">SportShield AI</span>
              <p className="text-slate-400 max-w-xs">© 2026 SportShield AI. Secure Intelligence for Global Sports.</p>
            </div>
            <div className="flex flex-wrap justify-center gap-8">
              <Link href="#" className="text-slate-500 hover:text-white transition-colors">Privacy Policy</Link>
              <Link href="#" className="text-slate-500 hover:text-white transition-colors">Terms of Service</Link>
              <Link href="#" className="text-slate-500 hover:text-white transition-colors">Security</Link>
              <Link href="#" className="text-slate-500 hover:text-white transition-colors">Contact</Link>
            </div>
            <div className="flex gap-4">
              <span className="material-symbols-outlined text-slate-500 hover:text-white cursor-pointer transition-colors">public</span>
              <span className="material-symbols-outlined text-slate-500 hover:text-white cursor-pointer transition-colors">security</span>
              <span className="material-symbols-outlined text-slate-500 hover:text-white cursor-pointer transition-colors">analytics</span>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}
