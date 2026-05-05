import React from 'react';

interface StatCardProps {
  label: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: 'alert' | 'scan' | 'shield' | 'lock';
}

export function StatCard({ label, value, change, trend, icon }: StatCardProps) {
  const getIcon = () => {
    switch (icon) {
      case 'alert':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        );
      case 'scan':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        );
      case 'shield':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
        );
      case 'lock':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        );
    }
  };

  const getTrendConfig = () => {
    if (trend === 'up') return { color: '#FF6B6B', bg: 'rgba(255,107,107,0.1)', arrow: '↑' };
    if (trend === 'down') return { color: '#10B981', bg: 'rgba(16,185,129,0.1)', arrow: '↓' };
    return { color: '#64748B', bg: 'rgba(100,116,139,0.1)', arrow: '→' };
  };

  const trendConfig = getTrendConfig();

  return (
    <div
      className="rounded-xl p-6 relative overflow-hidden group hover:border-[#FF6B6B]/20 transition-all duration-300"
      style={{
        backgroundColor: '#111415',
        border: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      {/* Subtle top glow on hover */}
      <div
        className="absolute top-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{ background: 'linear-gradient(90deg, transparent, #FF6B6B, transparent)' }}
      />

      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-slate-400">{label}</span>
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: 'rgba(255,107,107,0.12)', color: '#FF6B6B' }}
        >
          {getIcon()}
        </div>
      </div>

      <div className="flex items-end justify-between">
        <span className="text-3xl font-bold text-white" style={{ lineHeight: 1 }}>
          {value}
        </span>
        <span
          className="text-xs font-semibold px-2 py-1 rounded-md"
          style={{ color: trendConfig.color, backgroundColor: trendConfig.bg }}
        >
          {trendConfig.arrow} {change}
        </span>
      </div>
    </div>
  );
}
