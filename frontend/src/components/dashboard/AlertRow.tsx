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
      className="py-4 px-4 -mx-4 hover:bg-opacity-50 transition-colors cursor-pointer"
      style={{
        borderBottom: isLast ? 'none' : '1px solid var(--border-color)',
        backgroundColor: 'transparent'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--surface-gray)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent';
      }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <h4
              style={{
                fontSize: 'var(--text-base)',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--text-primary)'
              }}
            >
              {alert.title}
            </h4>
            <SeverityBadge level={alert.severity} />
          </div>
          <div className="flex items-center gap-4">
            <span
              style={{
                fontSize: 'var(--text-sm)',
                color: 'var(--text-secondary)'
              }}
            >
              {alert.source}
            </span>
            <span
              style={{
                fontSize: 'var(--text-xs)',
                color: 'var(--text-secondary)'
              }}
            >
              {alert.time}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span
            className="px-3 py-1 rounded-md"
            style={{
              fontSize: 'var(--text-xs)',
              fontWeight: 'var(--font-weight-medium)',
              color: 'var(--text-secondary)',
              backgroundColor: 'var(--surface-gray)',
              borderRadius: 'var(--radius-button)'
            }}
          >
            {alert.status}
          </span>
          <button
            className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
            style={{
              backgroundColor: 'transparent',
              color: 'var(--text-secondary)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--surface-gray)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
