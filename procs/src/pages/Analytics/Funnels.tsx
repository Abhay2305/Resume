import { Filter, CheckCircle } from 'lucide-react'
import { theme } from '../../styles/theme'
import { MetricCard, Alert, EmptyState } from '../../components/shared'
import { useFunnels } from './hooks/useFunnels'
import type { FunnelData } from './types'

function FunnelChart({ funnel }: { funnel: FunnelData }) {
  const maxCount = funnel.steps[0]?.count ?? 1
  const colors = [theme.colors.primary, theme.colors.info, theme.colors.warning, theme.colors.success]

  return (
    <div style={{
      backgroundColor: theme.colors.surface,
      border: `1px solid ${theme.colors.border}`,
      borderRadius: theme.borderRadius.md,
      overflow: 'hidden',
    }}>
      <div style={{
        padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
        borderBottom: `1px solid ${theme.colors.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <span style={{
          fontSize: theme.typography.sizes.bodySmall,
          fontWeight: theme.typography.weights.semibold,
          color: theme.colors.text,
          fontFamily: theme.typography.fontFamily,
        }}>
          {funnel.name}
        </span>
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          padding: '2px 8px',
          fontSize: theme.typography.sizes.tiny,
          fontWeight: theme.typography.weights.medium,
          color: theme.colors.success,
          backgroundColor: theme.colors.successBg,
          borderRadius: theme.borderRadius.full,
        }}>
          <CheckCircle size={10} />
          {funnel.completion_rate}% completion
        </span>
      </div>
      <div style={{ padding: theme.spacing[4] }}>
        {funnel.steps.map((step, i) => {
          const widthPct = maxCount > 0 ? (step.count / maxCount) * 100 : 0
          const color = colors[i % colors.length]
          return (
            <div key={step.name} style={{ marginBottom: i < funnel.steps.length - 1 ? theme.spacing[3] : 0 }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: theme.spacing[1],
              }}>
                <span style={{
                  fontSize: theme.typography.sizes.bodySmall,
                  color: theme.colors.text,
                  fontFamily: theme.typography.fontFamily,
                }}>
                  {step.name}
                </span>
                <span style={{
                  fontSize: theme.typography.sizes.bodySmall,
                  color: theme.colors.textSecondary,
                  fontFamily: theme.typography.fontFamily,
                  fontVariantNumeric: 'tabular-nums',
                }}>
                  {step.count.toLocaleString()} ({step.percentage}%)
                </span>
              </div>
              <div style={{
                height: '8px',
                backgroundColor: theme.colors.surfaceHover,
                borderRadius: theme.borderRadius.sm,
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  width: `${widthPct}%`,
                  backgroundColor: color,
                  borderRadius: theme.borderRadius.sm,
                  transition: 'width 300ms ease',
                }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function Funnels() {
  const { data, loading, error } = useFunnels()

  const totalUsers = data?.funnels[0]?.steps[0]?.count ?? 0
  const completionRate = data?.funnels[0]?.completion_rate ?? 0

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{ marginBottom: theme.spacing[5] }}>
        <h1 style={{
          margin: 0,
          fontSize: theme.typography.sizes.h1,
          fontWeight: theme.typography.weights.bold,
          color: theme.colors.text,
          fontFamily: theme.typography.fontFamily,
        }}>
          Funnels
        </h1>
        <p style={{
          margin: 0,
          marginTop: theme.spacing[1],
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}>
          Track conversion rates across user onboarding and content creation pipelines
        </p>
      </div>

      {error && (
        <div style={{ marginBottom: theme.spacing[4] }}>
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <MetricCard
          title="Total Users"
          value={totalUsers}
          loading={loading}
        />
        <MetricCard
          title="Onboarding Completion"
          value={`${completionRate}%`}
          loading={loading}
        />
        <MetricCard
          title="Active Funnels"
          value={data?.funnels.length ?? 0}
          icon={<Filter size={20} color={theme.colors.primary} />}
          loading={loading}
        />
      </div>

      {!loading && (!data?.funnels || data.funnels.length === 0) && (
        <EmptyState
          title="No funnel data available"
          description="Funnel analytics will appear here once there is sufficient user activity data."
        />
      )}

      {!loading && data?.funnels && data.funnels.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: theme.spacing[4],
        }}>
          {data.funnels.map((funnel) => (
            <FunnelChart key={funnel.name} funnel={funnel} />
          ))}
        </div>
      )}
    </div>
  )
}
