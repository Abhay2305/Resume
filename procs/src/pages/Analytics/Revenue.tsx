import { DollarSign, TrendingUp, Receipt, BarChart3 } from 'lucide-react'
import { theme } from '../../styles/theme'
import { MetricCard, ChartContainer, LineChart, Alert } from '../../components/shared'
import { useRevenue } from './hooks/useRevenue'

const PERIODS = [
  { label: '7d', value: '7d' },
  { label: '30d', value: '30d' },
  { label: '90d', value: '90d' },
]

function formatCurrency(value: number): string {
  return `$${value.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
}

export default function Revenue() {
  const { data, period, setPeriod, loading, error } = useRevenue()

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
            Revenue
          </h1>
          <p style={{
            margin: 0,
            marginTop: theme.spacing[1],
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}>
            Track revenue, growth, and transaction metrics
          </p>
        </div>
        <div style={{ display: 'flex', gap: theme.spacing[2] }}>
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              style={{
                padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
                fontSize: theme.typography.sizes.bodySmall,
                fontWeight: period === p.value ? theme.typography.weights.semibold : theme.typography.weights.medium,
                color: period === p.value ? theme.colors.surface : theme.colors.textSecondary,
                backgroundColor: period === p.value ? theme.colors.primary : theme.colors.surface,
                border: `1px solid ${period === p.value ? theme.colors.primary : theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                cursor: 'pointer',
                fontFamily: theme.typography.fontFamily,
              }}
            >
              {p.label === '7d' ? '7 Days' : p.label === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
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
          title="Total Revenue"
          value={formatCurrency(data?.summary.total_revenue ?? 0)}
          icon={<DollarSign size={20} color={theme.colors.success} />}
          loading={loading}
        />
        <MetricCard
          title="Growth"
          value={`${data?.summary.growth ?? 0}%`}
          trend={data?.summary.growth}
          icon={<TrendingUp size={20} color={theme.colors.info} />}
          loading={loading}
        />
        <MetricCard
          title="Avg Revenue/Tx"
          value={formatCurrency(data?.summary.avg_revenue ?? 0)}
          icon={<BarChart3 size={20} color={theme.colors.primary} />}
          loading={loading}
        />
        <MetricCard
          title="Transactions"
          value={data?.summary.total_transactions ?? 0}
          icon={<Receipt size={20} color={theme.colors.warning} />}
          loading={loading}
        />
      </div>

      <ChartContainer
        title="Revenue Trend"
        subtitle={`Daily revenue over ${period === '7d' ? '7 days' : period === '30d' ? '30 days' : '90 days'}`}
        loading={loading}
      >
        <LineChart
          data={data?.series ?? []}
          color={theme.colors.success}
          formatValue={(v) => `$${v.toLocaleString()}`}
        />
      </ChartContainer>
    </div>
  )
}
