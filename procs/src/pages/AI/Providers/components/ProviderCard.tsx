import { theme } from '../../../../styles/theme'
import { HealthIndicator } from '../../../../components/shared'
import type { AiProviderDetail } from '../../../../types/ai-monitoring'

interface ProviderCardProps {
  provider: AiProviderDetail
  loading: boolean
}

const providerColors: Record<string, string> = {
  gemini: '#4285F4',
  openai: '#10A37F',
  anthropic: '#D97706',
}

export default function ProviderCard({ provider, loading }: ProviderCardProps) {
  const color = providerColors[provider.name] || theme.colors.primary

  return (
    <div
      style={{
        backgroundColor: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md,
        overflow: 'hidden',
      }}
    >
      <div style={{
        padding: `${theme.spacing[4]} ${theme.spacing[5]}`,
        borderBottom: `1px solid ${theme.colors.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[3] }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: theme.borderRadius.md,
            backgroundColor: color + '20',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: theme.typography.sizes.bodySmall,
            fontWeight: theme.typography.weights.bold,
            color: color,
            fontFamily: theme.typography.fontFamily,
          }}>
            {provider.name.charAt(0).toUpperCase()}
          </div>
          <span style={{
            fontSize: theme.typography.sizes.h3,
            fontWeight: theme.typography.weights.semibold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            textTransform: 'capitalize',
          }}>
            {provider.name}
          </span>
        </div>
        <HealthIndicator
          items={[{
            label: provider.name,
            status: provider.healthy ? 'healthy' : 'failing',
          }]}
          loading={loading}
        />
      </div>

      <div style={{ padding: `${theme.spacing[4]} ${theme.spacing[5]}` }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: theme.spacing[4],
        }}>
          <StatItem label="Executions" value={provider.total_executions.toLocaleString()} loading={loading} />
          <StatItem label="Success Rate" value={`${provider.success_rate}%`} loading={loading} />
          <StatItem label="Avg Latency" value={`${Math.round(provider.avg_latency_ms)}ms`} loading={loading} />
          <StatItem label="Total Cost" value={`$${provider.total_cost.toFixed(4)}`} loading={loading} />
          <StatItem label="Total Tokens" value={provider.total_tokens.toLocaleString()} loading={loading} />
          <StatItem label="Models" value={provider.models.length.toString()} loading={loading} />
        </div>

        {provider.models.length > 0 && (
          <div style={{ marginTop: theme.spacing[4] }}>
            <span style={{
              fontSize: theme.typography.sizes.caption,
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.textSecondary,
              fontFamily: theme.typography.fontFamily,
            }}>
              Models
            </span>
            <div style={{
              marginTop: theme.spacing[2],
              display: 'flex',
              flexWrap: 'wrap',
              gap: theme.spacing[2],
            }}>
              {provider.models.map((m) => (
                <span
                  key={m.model}
                  style={{
                    padding: `${theme.spacing[1]} ${theme.spacing[2]}`,
                    fontSize: theme.typography.sizes.tiny,
                    color: theme.colors.textSecondary,
                    backgroundColor: theme.colors.neutralBg,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.sm,
                    fontFamily: theme.typography.fontFamily,
                  }}
                >
                  {m.model} ({m.executions})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function StatItem({ label, value, loading }: { label: string; value: string; loading: boolean }) {
  if (loading) {
    return (
      <div>
        <div style={{
          height: '12px',
          width: '60%',
          backgroundColor: theme.colors.border,
          borderRadius: theme.borderRadius.sm,
        }} />
        <div style={{
          marginTop: theme.spacing[1],
          height: '18px',
          width: '40%',
          backgroundColor: theme.colors.border,
          borderRadius: theme.borderRadius.sm,
        }} />
      </div>
    )
  }

  return (
    <div>
      <span style={{
        fontSize: theme.typography.sizes.caption,
        color: theme.colors.textTertiary,
        fontFamily: theme.typography.fontFamily,
      }}>
        {label}
      </span>
      <div style={{
        marginTop: theme.spacing[1],
        fontSize: theme.typography.sizes.body,
        fontWeight: theme.typography.weights.semibold,
        color: theme.colors.text,
        fontFamily: theme.typography.fontFamily,
        fontVariantNumeric: 'tabular-nums',
      }}>
        {value}
      </div>
    </div>
  )
}
