import React from 'react';
import { SeverityBadge } from './SeverityBadge';

interface AlertRowProps {
  alert: {
    id: number;
    title: string;
    source: string;
    time: string;
    severity: 'high' | 'medium' | 'low';
    status: string;
  };
  isLast: boolean;
}

export function AlertRow({ alert, isLast }: AlertRowProps) {
  return (
    <div
      className="py-4 px-4 -mx-4 cursor-pointer rounded-lg transition-colors duration-150"
      style={{ borderBottom: isLast ? 'none' : '1px solid rgba(255,255,255,0.05)' }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.03)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent';
      }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1.5">
            <h4 className="text-sm font-semibold text-white truncate">{alert.title}</h4>
            <SeverityBadge level={alert.severity} />
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-500">{alert.source}</span>
            <span className="text-xs text-slate-600">{alert.time}</span>
          </div>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span
            className="px-2.5 py-1 rounded-md text-xs font-medium"
            style={{
              backgroundColor: 'rgba(255,255,255,0.05)',
              color: '#94a3b8',
            }}
          >
            {alert.status}
          </span>
          <button
            className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-600 hover:text-slate-300 hover:bg-white/5 transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
