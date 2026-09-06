import { theme } from '../../../styles/theme'
import { MetricCard } from '../../../components/shared'
import { useJobMetrics } from './hooks/useJobMetrics'
import JobTable from './components/JobTable'
import JobChart from './components/JobChart'

const STATUS_OPTIONS = ['', 'success', 'completed', 'failed', 'error', 'running', 'pending']

export default function BackgroundJobsPage() {
  const { jobs, loading, error, statusFilter, setStatusFilter, refresh } = useJobMetrics()

  const totalExecutions = jobs.reduce((sum, j) => sum + j.count, 0)
  const successCount = jobs.filter((j) => j.status === 'success' || j.status === 'completed').reduce((sum, j) => sum + j.count, 0)
  const successRate = totalExecutions > 0 ? ((successCount / totalExecutions) * 100).toFixed(1) : '0'
  const avgDuration = jobs.length > 0
    ? jobs.reduce((sum, j) => sum + j.avg_duration_ms * j.count, 0) / totalExecutions
    : 0

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
          Background Jobs
        </h1>
        <p style={{
          margin: 0,
          marginTop: theme.spacing[1],
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}>
          Monitor background job execution status and performance
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <MetricCard
          title="Total Executions"
          value={totalExecutions}
          loading={loading}
          testId="metric-total-executions"
        />
        <MetricCard
          title="Success Rate"
          value={`${successRate}%`}
          loading={loading}
          testId="metric-success-rate"
        />
        <MetricCard
          title="Avg Duration"
          value={avgDuration < 1000 ? `${Math.round(avgDuration)}ms` : `${(avgDuration / 1000).toFixed(1)}s`}
          loading={loading}
          testId="metric-avg-duration"
        />
      </div>

      <div style={{
        display: 'flex',
        gap: theme.spacing[3],
        marginBottom: theme.spacing[4],
      }}>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            outline: 'none',
            minWidth: '140px',
          }}
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s || 'All Statuses'}</option>
          ))}
        </select>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <JobTable jobs={jobs} loading={loading} error={error} onRefresh={refresh} />
        <JobChart jobs={jobs} loading={loading} />
      </div>
    </div>
  )
}
