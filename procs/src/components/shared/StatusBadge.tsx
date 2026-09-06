import { CheckCircle, AlertTriangle, XCircle, HelpCircle } from 'lucide-react'
import { theme } from '../../styles/theme'

type StatusType = 'success' | 'warning' | 'danger' | 'info' | 'neutral'
type BadgeVariant = 'dot' | 'badge' | 'pill'

interface StatusBadgeProps {
  status: StatusType
  label: string
  variant?: BadgeVariant
  size?: 'sm' | 'md'
  testId?: string
}

const statusConfig: Record<StatusType, { color: string; bg: string }> = {
  success: { color: theme.colors.success, bg: theme.colors.successBg },
  warning: { color: theme.colors.warning, bg: theme.colors.warningBg },
  danger: { color: theme.colors.danger, bg: theme.colors.dangerBg },
  info: { color: theme.colors.info, bg: theme.colors.infoBg },
  neutral: { color: theme.colors.textSecondary, bg: theme.colors.neutralBg },
}

const statusIcon: Record<StatusType, typeof CheckCircle> = {
  success: CheckCircle,
  warning: AlertTriangle,
  danger: XCircle,
  info: HelpCircle,
  neutral: HelpCircle,
}

export default function StatusBadge({
  status,
  label,
  variant = 'badge',
  size = 'sm',
  testId,
}: StatusBadgeProps) {
  const config = statusConfig[status]
  const Icon = statusIcon[status]
  const isSmall = size === 'sm'

  if (variant === 'dot') {
    return (
      <span
        data-testid={testId}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: isSmall ? '4px' : '6px',
          fontSize: isSmall ? theme.typography.sizes.tiny : theme.typography.sizes.caption,
          color: theme.colors.text,
          fontFamily: theme.typography.fontFamily,
        }}
      >
        <span
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: config.color,
            flexShrink: 0,
          }}
        />
        {label}
      </span>
    )
  }

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
        color: config.color,
        backgroundColor: config.bg,
        borderRadius: variant === 'pill' ? theme.borderRadius.full : theme.borderRadius.sm,
        lineHeight: 1,
        whiteSpace: 'nowrap',
      }}
    >
      <Icon size={isSmall ? 10 : 12} style={{ flexShrink: 0 }} />
      {label}
    </span>
  )
}
