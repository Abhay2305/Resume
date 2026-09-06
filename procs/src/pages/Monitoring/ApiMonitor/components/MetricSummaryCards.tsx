import { theme } from '../../../../styles/theme'
import { MetricCard } from '../../../../components/shared'
import type { MetricSummary } from '../../../../types/monitoring'

interface MetricSummaryCardsProps {
  summary: MetricSummary | null
  loading: boolean
}

export default function MetricSummaryCards({ summary, loading }: MetricSummaryCardsProps) {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: theme.spacing[4],
      marginBottom: theme.spacing[5],
    }}>
      <MetricCard
        title="Total Requests"
        value={summary?.request_count ?? 0}
        loading={loading}
        testId="metric-total-requests"
      />
      <MetricCard
        title="Avg Response Time"
        value={summary ? `${Math.round(summary.avg_response_time_ms)}ms` : '0ms'}
        loading={loading}
        testId="metric-avg-response"
      />
      <MetricCard
        title="Error Rate"
        value={summary ? `${(summary.error_rate * 100).toFixed(1)}%` : '0%'}
        loading={loading}
        testId="metric-error-rate"
      />
    </div>
  )
}
