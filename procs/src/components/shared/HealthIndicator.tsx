import { CheckCircle, AlertTriangle, XCircle, HelpCircle } from 'lucide-react'
import { theme } from '../../styles/theme'

type HealthStatus = 'healthy' | 'degraded' | 'failing' | 'unknown'

interface HealthItem {
  label: string
  status: HealthStatus
  latency?: string
  details?: string
}

interface HealthIndicatorProps {
  items: HealthItem[]
  loading?: boolean
  testId?: string
}

const statusConfig: Record<HealthStatus, { icon: typeof CheckCircle; color: string; label: string }> = {
  healthy: { icon: CheckCircle, color: theme.colors.success, label: 'Healthy' },
  degraded: { icon: AlertTriangle, color: theme.colors.warning, label: 'Degraded' },
  failing: { icon: XCircle, color: theme.colors.danger, label: 'Failing' },
  unknown: { icon: HelpCircle, color: theme.colors.textTertiary, label: 'Unknown' },
}

export default function HealthIndicator({ items, loading = false, testId }: HealthIndicatorProps) {
  if (loading) {
    return (
      <div data-testid={testId} style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[3] }}>
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            style={{
              height: '20px',
              backgroundColor: theme.colors.border,
              borderRadius: theme.borderRadius.sm,
              backgroundImage: 'linear-gradient(90deg, transparent 25%, rgba(255,255,255,0.4) 50%, transparent 75%)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 1.5s ease-in-out infinite',
            }}
          />
        ))}
      </div>
    )
  }

  return (
    <div data-testid={testId} style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[3] }}>
      {items.map((item, i) => {
        const config = statusConfig[item.status]
        const Icon = config.icon
        return (
          <div
            key={i}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: theme.spacing[3],
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2], minWidth: 0 }}>
              <Icon size={14} color={config.color} style={{ flexShrink: 0 }} />
              <span
                style={{
                  fontSize: theme.typography.sizes.body,
                  color: theme.colors.text,
                  fontFamily: theme.typography.fontFamily,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {item.label}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2], flexShrink: 0 }}>
              {item.latency && (
                <span
                  style={{
                    fontSize: theme.typography.sizes.caption,
                    color: theme.colors.textTertiary,
                    fontFamily: theme.typography.fontFamily,
                  }}
                >
                  {item.latency}
                </span>
              )}
              <span
                style={{
                  fontSize: theme.typography.sizes.caption,
                  fontWeight: theme.typography.weights.medium,
                  color: config.color,
                  fontFamily: theme.typography.fontFamily,
                }}
              >
                {config.label}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
