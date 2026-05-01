import React from 'react';

interface SeverityBadgeProps {
  level: 'high' | 'medium' | 'low';
}

export function SeverityBadge({ level }: SeverityBadgeProps) {
  const getStyles = () => {
    switch (level) {
      case 'high':
        return {
          backgroundColor: 'rgba(255, 107, 107, 0.1)',
          color: 'var(--severity-high)',
          label: 'HIGH'
        };
      case 'medium':
        return {
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          color: 'var(--severity-medium)',
          label: 'MEDIUM'
        };
      case 'low':
        return {
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          color: 'var(--severity-low)',
          label: 'LOW'
        };
    }
  };

  const styles = getStyles();

  return (
    <span
      className="px-3 py-1 rounded-md inline-flex items-center gap-2"
      style={{
        backgroundColor: styles.backgroundColor,
        color: styles.color,
        fontSize: 'var(--text-xs)',
        fontWeight: 'var(--font-weight-semibold)',
        letterSpacing: '0.05em',
        borderRadius: 'var(--radius-button)'
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{ backgroundColor: styles.color }}
      />
      {styles.label}
    </span>
  );
}
