import { theme } from '../../../../styles/theme'
import { DataTable, StatusBadge } from '../../../../components/shared'
import type { AuditLog } from '../../../../types/monitoring'

interface AuditLogTableProps {
  logs: AuditLog[]
  loading: boolean
  error: string | null
  onRefresh: () => void
  onRowClick: (log: AuditLog) => void
  page: number
  perPage: number
  total: number
  onPageChange: (page: number) => void
}

function getActionBadge(action: string) {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
    create: 'success',
    update: 'info',
    delete: 'danger',
    login: 'success',
    login_failed: 'danger',
    logout: 'neutral',
    error: 'danger',
    export: 'info',
  }
  return map[action] || 'neutral'
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

export default function AuditLogTable({
  logs,
  loading,
  error,
  onRefresh,
  onRowClick,
  page,
  perPage,
  total,
  onPageChange,
}: AuditLogTableProps) {
  const columns = [
    {
      key: 'created_at',
      label: 'Timestamp',
      width: '170px',
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
          {formatDate(val as string)}
        </span>
      ),
    },
    {
      key: 'action',
      label: 'Action',
      width: '120px',
      render: (val: unknown) => (
        <StatusBadge status={getActionBadge(val as string)} label={val as string} />
      ),
    },
    {
      key: 'entity_type',
      label: 'Entity',
      width: '120px',
    },
    {
      key: 'entity_id',
      label: 'Entity ID',
      width: '140px',
      truncate: true,
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textTertiary, fontFamily: theme.typography.fontFamily, fontVariantNumeric: 'tabular-nums' }}>
          {val ? String(val).slice(0, 8) + '...' : '-'}
        </span>
      ),
    },
    {
      key: 'description',
      label: 'Description',
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
          {val ? String(val) : '-'}
        </span>
      ),
      truncate: true,
    },
    {
      key: 'ip_address',
      label: 'IP Address',
      width: '130px',
      render: (val: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily, fontVariantNumeric: 'tabular-nums' }}>
          {val ? String(val) : '-'}
        </span>
      ),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={logs as unknown as Record<string, unknown>[]}
      loading={loading}
      error={error}
      errorRetry={onRefresh}
      empty="No audit logs found"
      onRowClick={(row) => onRowClick(row as unknown as AuditLog)}
      pagination={{
        page,
        perPage,
        total,
        perPageOptions: [10, 20, 50],
        onPageChange,
      }}
      testId="audit-log-table"
    />
  )
}
