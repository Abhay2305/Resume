import { theme } from '../../../../styles/theme'
import { DataTable, StatusBadge } from '../../../../components/shared'

interface JobMetric {
  job_name: string
  status: string
  count: number
  avg_duration_ms: number
}

interface JobTableProps {
  jobs: JobMetric[]
  loading: boolean
  error: string | null
  onRefresh: () => void
}

function getStatusBadge(status: string) {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
    success: 'success',
    completed: 'success',
    failed: 'danger',
    error: 'danger',
    running: 'info',
    pending: 'warning',
  }
  return map[status] || 'neutral'
}

function formatDuration(ms: number) {
  if (ms < 1000) return `${Math.round(ms)}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

export default function JobTable({ jobs, loading, error, onRefresh }: JobTableProps) {
  const columns = [
    {
      key: 'job_name',
      label: 'Job Name',
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily, fontWeight: theme.typography.weights.medium }}>
          {val as string}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      width: '120px',
      render: (val: unknown) => (
        <StatusBadge status={getStatusBadge(val as string)} label={val as string} />
      ),
    },
    {
      key: 'count',
      label: 'Count',
      width: '80px',
      align: 'right' as const,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily, fontVariantNumeric: 'tabular-nums' }}>
          {Number(val).toLocaleString()}
        </span>
      ),
    },
    {
      key: 'avg_duration_ms',
      label: 'Avg Duration',
      width: '120px',
      align: 'right' as const,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily, fontVariantNumeric: 'tabular-nums' }}>
          {formatDuration(Number(val))}
        </span>
      ),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={jobs as unknown as Record<string, unknown>[]}
      loading={loading}
      error={error}
      errorRetry={onRefresh}
      empty="No job metrics found"
      testId="job-table"
    />
  )
}
