import { theme } from '../../../../styles/theme'
import { DataTable, StatusBadge, Badge } from '../../../../components/shared'
import type { AiExecutionLog } from '../../../../types/ai-monitoring'

interface ExecutionTableProps {
  executions: AiExecutionLog[]
  loading: boolean
  error: string | null
  onRefresh: () => void
  onRowClick: (execution: AiExecutionLog) => void
  page: number
  perPage: number
  total: number
  onPageChange: (page: number) => void
}

function getStatusBadge(status: string) {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
    completed: 'success',
    failed: 'danger',
    pending: 'warning',
    running: 'info',
  }
  return map[status] || 'neutral'
}

function getProviderBadge(provider: string) {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'danger'> = {
    gemini: 'success',
    openai: 'primary',
    anthropic: 'warning',
  }
  return map[provider] || 'default' as const
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

export default function ExecutionTable({
  executions,
  loading,
  error,
  onRefresh,
  onRowClick,
  page,
  perPage,
  total,
  onPageChange,
}: ExecutionTableProps) {
  const columns = [
    {
      key: 'created_at',
      label: 'Timestamp',
      width: '160px',
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
          {formatDate(val as string)}
        </span>
      ),
    },
    {
      key: 'provider',
      label: 'Provider',
      width: '110px',
      render: (val: unknown) => (
        <Badge variant={getProviderBadge(val as string)}>{val as string}</Badge>
      ),
    },
    {
      key: 'model',
      label: 'Model',
      width: '160px',
      truncate: true,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily, fontWeight: theme.typography.weights.medium }}>
          {val as string}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      width: '100px',
      render: (val: unknown) => (
        <StatusBadge status={getStatusBadge(val as string)} label={val as string} />
      ),
    },
    {
      key: 'total_tokens',
      label: 'Tokens',
      width: '80px',
      align: 'right' as const,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily, fontVariantNumeric: 'tabular-nums' }}>
          {val != null ? Number(val).toLocaleString() : '-'}
        </span>
      ),
    },
    {
      key: 'estimated_cost',
      label: 'Cost',
      width: '80px',
      align: 'right' as const,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily, fontVariantNumeric: 'tabular-nums' }}>
          {val != null ? `$${Number(val).toFixed(4)}` : '-'}
        </span>
      ),
    },
    {
      key: 'execution_time_ms',
      label: 'Latency',
      width: '90px',
      align: 'right' as const,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily, fontVariantNumeric: 'tabular-nums' }}>
          {val != null ? `${Number(val)}ms` : '-'}
        </span>
      ),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={executions as unknown as Record<string, unknown>[]}
      loading={loading}
      error={error}
      errorRetry={onRefresh}
      empty="No executions found"
      onRowClick={(row) => onRowClick(row as unknown as AiExecutionLog)}
      pagination={{
        page,
        perPage,
        total,
        perPageOptions: [10, 20, 50],
        onPageChange,
      }}
      testId="execution-table"
    />
  )
}
