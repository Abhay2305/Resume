import { type ReactNode } from 'react'
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react'
import { theme } from '../../styles/theme'

type AlertVariant = 'success' | 'warning' | 'error' | 'info'

interface AlertProps {
  variant: AlertVariant
  title?: string
  children: ReactNode
  closable?: boolean
  onClose?: () => void
  action?: {
    label: string
    onClick: () => void
  }
  testId?: string
}

const variantConfig: Record<AlertVariant, { icon: typeof CheckCircle; color: string; bg: string }> = {
  success: { icon: CheckCircle, color: theme.colors.success, bg: theme.colors.successBg },
  warning: { icon: AlertTriangle, color: theme.colors.warning, bg: theme.colors.warningBg },
  error: { icon: XCircle, color: theme.colors.danger, bg: theme.colors.dangerBg },
  info: { icon: Info, color: theme.colors.info, bg: theme.colors.infoBg },
}

export default function Alert({
  variant,
  title,
  children,
  closable = false,
  onClose,
  action,
  testId,
}: AlertProps) {
  const config = variantConfig[variant]
  const Icon = config.icon

  return (
    <div
      data-testid={testId}
      role="alert"
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: theme.spacing[3],
        padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
        borderLeft: `3px solid ${config.color}`,
        backgroundColor: config.bg,
        borderRadius: theme.borderRadius.md,
      }}
    >
      <Icon size={18} color={config.color} style={{ flexShrink: 0, marginTop: '1px' }} />
      <div style={{ flex: 1, minWidth: 0 }}>
        {title && (
          <div
            style={{
              fontWeight: theme.typography.weights.semibold,
              fontSize: theme.typography.sizes.body,
              color: theme.colors.text,
              marginBottom: '2px',
            }}
          >
            {title}
          </div>
        )}
        <div
          style={{
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            lineHeight: theme.typography.lineHeights.body,
          }}
        >
          {children}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2], flexShrink: 0 }}>
        {action && (
          <button
            onClick={action.onClick}
            style={{
              padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
              color: config.color,
              backgroundColor: 'transparent',
              border: 'none',
              borderRadius: theme.borderRadius.sm,
              cursor: 'pointer',
              fontFamily: theme.typography.fontFamily,
            }}
          >
            {action.label}
          </button>
        )}
        {closable && (
          <button
            onClick={onClose}
            aria-label="Close"
            style={{
              padding: theme.spacing[1],
              color: theme.colors.textTertiary,
              backgroundColor: 'transparent',
              border: 'none',
              cursor: 'pointer',
              display: 'inline-flex',
            }}
          >
            <X size={16} />
          </button>
        )}
      </div>
    </div>
  )
}
