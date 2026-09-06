import type { ReactNode } from 'react'
import { theme } from '../../styles/theme'

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger'

interface BadgeProps {
  variant?: BadgeVariant
  children: ReactNode
  size?: 'sm' | 'md'
  dot?: boolean
  testId?: string
}

const variantStyles: Record<BadgeVariant, { bg: string; text: string; dot: string }> = {
  default: { bg: '#E2E8F0', text: '#475569', dot: '#475569' },
  primary: { bg: '#0F766E10', text: '#0F766E', dot: '#0F766E' },
  success: { bg: '#10B98110', text: '#10B981', dot: '#10B981' },
  warning: { bg: '#F59E0B10', text: '#F59E0B', dot: '#F59E0B' },
  danger: { bg: '#EF444410', text: '#EF4444', dot: '#EF4444' },
}

export default function Badge({
  variant = 'default',
  children,
  size = 'sm',
  dot = false,
  testId,
}: BadgeProps) {
  const v = variantStyles[variant]
  const isSmall = size === 'sm'

  return (
    <span
      data-testid={testId}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: isSmall ? '4px' : '6px',
        padding: isSmall ? '2px 8px' : '4px 10px',
        fontSize: isSmall ? theme.typography.sizes.tiny : theme.typography.sizes.caption,
        fontWeight: theme.typography.weights.medium,
        lineHeight: 1,
        color: v.text,
        backgroundColor: v.bg,
        borderRadius: theme.borderRadius.full,
        whiteSpace: 'nowrap',
      }}
    >
      {dot && (
        <span
          style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: v.dot,
            flexShrink: 0,
          }}
        />
      )}
      {children}
    </span>
  )
}
