import { theme } from '../../../styles/theme'
import { MetricCard, Alert } from '../../../components/shared'
import { useAiTokens } from './hooks/useAiTokens'
import TokenByModel from './components/TokenByModel'
import TokenTrendChart from './components/TokenTrendChart'

const PERIODS = ['24h', '7d', '30d']

export default function TokenAnalyticsPage() {
  const { data, period, setPeriod, loading, error } = useAiTokens()

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
          Token Analytics
        </h1>
        <p style={{
          margin: 0,
          marginTop: theme.spacing[1],
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}>
          Monitor AI token consumption and efficiency
        </p>
      </div>

      {error && (
        <div style={{ marginBottom: theme.spacing[4] }}>
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      <div style={{
        display: 'flex',
        gap: theme.spacing[2],
        marginBottom: theme.spacing[4],
      }}>
        {PERIODS.map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            style={{
              padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: period === p ? theme.typography.weights.medium : theme.typography.weights.regular,
              fontFamily: theme.typography.fontFamily,
              color: period === p ? theme.colors.textInverse : theme.colors.text,
              backgroundColor: period === p ? theme.colors.primary : theme.colors.surface,
              border: `1px solid ${period === p ? theme.colors.primary : theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              cursor: 'pointer',
            }}
          >
            {p === '24h' ? '24 Hours' : p === '7d' ? '7 Days' : '30 Days'}
          </button>
        ))}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <MetricCard
          title="Total Tokens"
          value={data?.total_tokens ?? 0}
          loading={loading}
          testId="metric-total-tokens"
        />
        <MetricCard
          title="Avg Tokens/Request"
          value={data?.avg_tokens_per_request ?? 0}
          loading={loading}
          testId="metric-avg-tokens"
        />
        <MetricCard
          title="Models Used"
          value={data?.by_model?.length ?? 0}
          loading={loading}
          testId="metric-models"
        />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <TokenByModel data={data} loading={loading} />
        <TokenTrendChart data={data} loading={loading} />
      </div>
    </div>
  )
}
