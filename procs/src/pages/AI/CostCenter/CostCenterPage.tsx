import { theme } from '../../../styles/theme'
import { MetricCard, Alert } from '../../../components/shared'
import { useAiCosts } from './hooks/useAiCosts'
import CostByProvider from './components/CostByProvider'
import CostTrendChart from './components/CostTrendChart'

const PERIODS = ['24h', '7d', '30d']

export default function CostCenterPage() {
  const { data, period, setPeriod, loading, error } = useAiCosts()

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
          AI Cost Center
        </h1>
        <p style={{
          margin: 0,
          marginTop: theme.spacing[1],
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}>
          Track AI spending across providers
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
          title="Total Cost"
          value={`$${(data?.total_cost ?? 0).toFixed(2)}`}
          loading={loading}
          testId="metric-total-cost"
        />
        <MetricCard
          title="Providers Active"
          value={data?.by_provider?.length ?? 0}
          loading={loading}
          testId="metric-providers"
        />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <CostByProvider data={data} loading={loading} />
        <CostTrendChart data={data} loading={loading} />
      </div>
    </div>
  )
}
