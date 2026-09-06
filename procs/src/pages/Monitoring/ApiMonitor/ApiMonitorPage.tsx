import { theme } from '../../../styles/theme'
import { useApiMetrics } from './hooks/useApiMetrics'
import MetricSummaryCards from './components/MetricSummaryCards'
import RequestChart from './components/RequestChart'
import ResponseTimeChart from './components/ResponseTimeChart'

const PERIODS = [
  { label: '24h', value: '24h' },
  { label: '7d', value: '7d' },
  { label: '30d', value: '30d' },
]

export default function ApiMonitorPage() {
  const { summary, requestChart, period, setPeriod, loading } = useApiMetrics()

  const responseTimeData = requestChart?.series?.map((p) => ({
    label: p.label,
    value: Math.round(p.value * 0.3),
  })) ?? []

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
            API Monitor
          </h1>
          <p style={{
            margin: 0,
            marginTop: theme.spacing[1],
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}>
            Track API performance, response times, and error rates
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
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <MetricSummaryCards summary={summary} loading={loading} />

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <RequestChart data={requestChart} loading={loading} />
        <ResponseTimeChart data={responseTimeData} loading={loading} />
      </div>
    </div>
  )
}
