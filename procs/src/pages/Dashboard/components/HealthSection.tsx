import HealthIndicator from '../../../components/shared/HealthIndicator'
import Alert from '../../../components/shared/Alert'
import Skeleton from '../../../components/shared/Skeleton'
import { theme } from '../../../styles/theme'
import type { DashboardHealth } from '../types'

interface HealthSectionProps {
  health: DashboardHealth | null
  loading: boolean
  error: string | null
  onRetry?: () => void
}

function mapHealthItems(health: DashboardHealth) {
  return [
    { label: 'Database', status: health.database.status as 'healthy' | 'degraded' | 'failing' | 'unknown', latency: health.database.latency },
    { label: 'AI Providers', status: health.ai_providers.status as 'healthy' | 'degraded' | 'failing' | 'unknown', latency: health.ai_providers.latency },
    { label: 'Storage', status: health.storage.status as 'healthy' | 'degraded' | 'failing' | 'unknown', latency: health.storage.latency },
    { label: 'Background Jobs', status: health.background_jobs.status as 'healthy' | 'degraded' | 'failing' | 'unknown', latency: health.background_jobs.latency },
  ]
}

export default function HealthSection({ health, loading, error, onRetry }: HealthSectionProps) {
  return (
    <div
      style={{
        padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
        backgroundColor: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md,
        marginBottom: theme.spacing[6],
      }}
    >
      <div
        style={{
          fontSize: theme.typography.sizes.bodySmall,
          fontWeight: theme.typography.weights.medium,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
          marginBottom: theme.spacing[2],
        }}
      >
        System Health
      </div>

      {loading && (
        <div style={{ display: 'flex', gap: theme.spacing[6] }}>
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="text" width="100px" height="16px" />
          ))}
        </div>
      )}

      {error && !health && (
        <Alert variant="error" title="Health check failed" action={onRetry ? { label: 'Retry', onClick: onRetry } : undefined}>
          {error}
        </Alert>
      )}

      {health && (
        <HealthIndicator items={mapHealthItems(health)} />
      )}
    </div>
  )
}
