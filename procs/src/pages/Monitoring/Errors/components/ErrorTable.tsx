import { theme } from '../../../../styles/theme'
import { DataTable, StatusBadge } from '../../../../components/shared'
import type { ErrorLog } from '../../../../types/monitoring'

interface ErrorTableProps {
  errors: ErrorLog[]
  loading: boolean
  error: string | null
  onRefresh: () => void
  onRowClick: (error: ErrorLog) => void
  page: number
  perPage: number
  total: number
  onPageChange: (page: number) => void
}

function getSeverityBadge(severity: string) {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
    critical: 'danger',
    high: 'warning',
    medium: 'info',
    low: 'neutral',
  }
  return map[severity] || 'neutral'
}

function getStatusBadge(status: string) {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
    resolved: 'success',
    acknowledged: 'warning',
    investigating: 'info',
    new: 'danger',
    wont_fix: 'neutral',
  }
  return map[status] || 'neutral'
}

function getMethodBadgeColor(method: string | null) {
  if (!method) return theme.colors.textTertiary
  const map: Record<string, string> = {
    GET: theme.colors.info,
    POST: theme.colors.success,
    PUT: theme.colors.warning,
    PATCH: theme.colors.warning,
    DELETE: theme.colors.danger,
  }
  return map[method.toUpperCase()] || theme.colors.textTertiary
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

export default function ErrorTable({
  errors,
  loading,
  error,
  onRefresh,
  onRowClick,
  page,
  perPage,
  total,
  onPageChange,
}: ErrorTableProps) {
  const columns = [
    {
      key: 'created_at',
      label: 'Timestamp',
      width: '150px',
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
          {formatDate(val as string)}
        </span>
      ),
    },
    {
      key: 'severity',
      label: 'Severity',
      width: '90px',
      render: (val: unknown) => (
        <StatusBadge status={getSeverityBadge(val as string)} label={val as string} />
      ),
    },
    {
      key: 'error_type',
      label: 'Type',
      width: '150px',
      truncate: true,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily, fontWeight: theme.typography.weights.medium }}>
          {val as string}
        </span>
      ),
    },
    {
      key: 'error_message',
      label: 'Message',
      truncate: true,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
          {val ? String(val).slice(0, 80) : '-'}
        </span>
      ),
    },
    {
      key: 'router',
      label: 'Router',
      width: '100px',
      render: (val: unknown) => (
        <span style={{
          fontSize: theme.typography.sizes.bodySmall,
          color: theme.colors.text,
          fontFamily: theme.typography.fontFamily,
          padding: '2px 6px',
          backgroundColor: theme.colors.background,
          borderRadius: theme.borderRadius.sm,
        }}>
          {(val as string) || '-'}
        </span>
      ),
    },
    {
      key: 'http_method',
      label: 'Method',
      width: '70px',
      render: (val: unknown) => {
        const method = val as string | null
        return method ? (
          <span style={{
            fontSize: theme.typography.sizes.bodySmall,
            fontFamily: theme.typography.fontFamily,
            fontWeight: theme.typography.weights.bold,
            color: getMethodBadgeColor(method),
          }}>
            {method}
          </span>
        ) : '-'
      },
    },
    {
      key: 'endpoint',
      label: 'Endpoint',
      width: '160px',
      truncate: true,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textTertiary, fontFamily: theme.typography.fontFamily }}>
          {val ? String(val) : '-'}
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
      key: 'occurrence_count',
      label: 'Count',
      width: '60px',
      align: 'right' as const,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily, fontVariantNumeric: 'tabular-nums' }}>
          {Number(val) || 1}
        </span>
      ),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={errors as unknown as Record<string, unknown>[]}
      loading={loading}
      error={error}
      errorRetry={onRefresh}
      empty="No errors found"
      onRowClick={(row) => onRowClick(row as unknown as ErrorLog)}
      pagination={{
        page,
        perPage,
        total,
        perPageOptions: [10, 20, 50],
        onPageChange,
      }}
      testId="error-table"
    />
  )
}
