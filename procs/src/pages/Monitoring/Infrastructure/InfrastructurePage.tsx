import { RefreshCw } from 'lucide-react'
import { theme } from '../../../styles/theme'
import { HealthIndicator } from '../../../components/shared'
import { useHealth } from './hooks/useHealth'

function mapStatus(s: string): 'healthy' | 'degraded' | 'failing' | 'unknown' {
  if (!s) return 'unknown'
  const lower = s.toLowerCase()
  if (lower === 'healthy' || lower === 'ok' || lower === 'up' || lower === 'connected') return 'healthy'
  if (lower === 'degraded' || lower === 'slow' || lower === 'warning') return 'degraded'
  if (lower === 'failing' || lower === 'down' || lower === 'error' || lower === 'disconnected') return 'failing'
  return 'unknown'
}

interface HealthCardProps {
  title: string
  items: Array<{ label: string; status: string; latency?: string; details?: string }>
}

function HealthCard({ title, items }: HealthCardProps) {
  return (
    <div style={{
      backgroundColor: theme.colors.surface,
      border: `1px solid ${theme.colors.border}`,
      borderRadius: theme.borderRadius.md,
      padding: theme.spacing[4],
    }}>
      <h3 style={{
        margin: 0,
        marginBottom: theme.spacing[3],
        fontSize: theme.typography.sizes.body,
        fontWeight: theme.typography.weights.semibold,
        color: theme.colors.text,
        fontFamily: theme.typography.fontFamily,
      }}>
        {title}
      </h3>
      <HealthIndicator
        items={items.map((item) => ({
          label: item.label,
          status: mapStatus(item.status),
          latency: item.latency,
          details: item.details,
        }))}
      />
    </div>
  )
}

export default function InfrastructurePage() {
  const { health, procsHealth, loading, error, refresh } = useHealth()

  const dbItems = [
    {
      label: 'Database',
      status: health?.checks?.database?.status || procsHealth?.database?.status || 'unknown',
      latency: procsHealth?.database?.latency,
      details: health?.checks?.database?.pool
        ? `Pool: ${health.checks.database.pool.checked_out}/${health.checks.database.pool.size} active`
        : undefined,
    },
  ]

  const aiItems = [
    {
      label: 'AI Providers',
      status: procsHealth?.ai_providers?.status || 'unknown',
      latency: procsHealth?.ai_providers?.latency,
    },
  ]

  const storageItems = [
    {
      label: 'Storage',
      status: procsHealth?.storage?.status || 'unknown',
      latency: procsHealth?.storage?.latency,
    },
  ]

  const jobItems = [
    {
      label: 'Background Jobs',
      status: procsHealth?.background_jobs?.status || 'unknown',
      latency: procsHealth?.background_jobs?.latency,
    },
  ]

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: theme.spacing[5] }}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: theme.typography.sizes.h1,
            fontWeight: theme.typography.weights.bold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
          }}>
            Infrastructure
          </h1>
          <p style={{
            margin: 0,
            marginTop: theme.spacing[1],
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}>
            Real-time health status of system components
          </p>
        </div>
        <button
          onClick={() => refresh()}
          disabled={loading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[2],
            padding: `${theme.spacing[2]} ${theme.spacing[4]}`,
            fontSize: theme.typography.sizes.bodySmall,
            fontWeight: theme.typography.weights.medium,
            color: theme.colors.surface,
            backgroundColor: theme.colors.primary,
            border: 'none',
            borderRadius: theme.borderRadius.md,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div style={{
          padding: theme.spacing[3],
          marginBottom: theme.spacing[4],
          backgroundColor: theme.colors.dangerBg,
          border: `1px solid ${theme.colors.danger}30`,
          borderRadius: theme.borderRadius.md,
          color: theme.colors.danger,
          fontSize: theme.typography.sizes.body,
          fontFamily: theme.typography.fontFamily,
        }}>
          {error}
        </div>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: theme.spacing[4],
      }}>
        <HealthCard title="Database" items={dbItems} />
        <HealthCard title="AI Providers" items={aiItems} />
        <HealthCard title="Storage" items={storageItems} />
        <HealthCard title="Background Jobs" items={jobItems} />
      </div>

      {health && (
        <div style={{
          marginTop: theme.spacing[5],
          padding: theme.spacing[3],
          backgroundColor: theme.colors.surface,
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.md,
          display: 'flex',
          gap: theme.spacing[6],
          fontSize: theme.typography.sizes.bodySmall,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}>
          <span>Version: {health.version}</span>
          <span>Status: {health.status}</span>
          <span>Platform: {health.checks?.system?.platform || '-'}</span>
          <span>Python: {health.checks?.system?.python_version || '-'}</span>
        </div>
      )}
    </div>
  )
}
