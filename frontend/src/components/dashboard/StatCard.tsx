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

  const getTrendColor = () => {
    if (trend === 'up') return 'var(--severity-high)';
    if (trend === 'down') return 'var(--success)';
    return 'var(--text-secondary)';
  };

  return (
    <div
      className="rounded-xl p-6"
      style={{
        backgroundColor: 'var(--surface-white)',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-sm)'
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <span
          style={{
            fontSize: 'var(--text-sm)',
            fontWeight: 'var(--font-weight-medium)',
            color: 'var(--text-secondary)'
          }}
        >
          {label}
        </span>
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center"
          style={{
            backgroundColor: 'var(--surface-gray)',
            color: 'var(--text-secondary)'
          }}
        >
          {getIcon()}
        </div>
      </div>
      <div className="flex items-end justify-between">
        <span
          style={{
            fontSize: 'var(--text-3xl)',
            fontWeight: 'var(--font-weight-bold)',
            color: 'var(--text-primary)',
            lineHeight: 1
          }}
        >
          {value}
        </span>
        <span
          style={{
            fontSize: 'var(--text-sm)',
            fontWeight: 'var(--font-weight-medium)',
            color: getTrendColor()
          }}
        >
          {change}
        </span>
      </div>
    </div>
  );
}
