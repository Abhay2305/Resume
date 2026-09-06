import { theme } from '../../../../styles/theme'
import DataTable from '../../../../components/shared/DataTable'
import Badge from '../../../../components/shared/Badge'
import type { SystemConfig } from '../types'

interface ConfigTableProps {
  configs: SystemConfig[]
  total: number
  loading: boolean
  error: string | null
  page: number
  perPage: number
  onPageChange: (page: number) => void
  onPerPageChange: (perPage: number) => void
  onEdit: (config: SystemConfig) => void
  onDelete: (config: SystemConfig) => void
  onRetry?: () => void
}

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`
  return date.toLocaleDateString()
}

function truncateValue(value: string, maxLen = 50): string {
  if (value.length <= maxLen) return value
  return value.slice(0, maxLen) + '...'
}

export default function ConfigTable({
  configs,
  total,
  loading,
  error,
  page,
  perPage,
  onPageChange,
  onPerPageChange,
  onEdit,
  onDelete,
  onRetry,
}: ConfigTableProps) {
  const columns = [
    {
      key: 'key',
      label: 'Key',
      sortable: true,
      render: (value: unknown) => (
        <span style={{ fontWeight: theme.typography.weights.medium, color: theme.colors.text, fontFamily: 'monospace', fontSize: theme.typography.sizes.bodySmall }}>
          {String(value)}
        </span>
      ),
    },
    {
      key: 'value',
      label: 'Value',
      render: (value: unknown) => (
        <span style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.bodySmall, fontFamily: theme.typography.fontFamily }}>
          {truncateValue(String(value))}
        </span>
      ),
    },
    {
      key: 'category',
      label: 'Category',
      width: '120px',
      render: (value: unknown) => {
        if (!value) return <span style={{ color: theme.colors.textTertiary }}>—</span>
        return <Badge variant="default">{String(value)}</Badge>
      },
    },
    {
      key: 'description',
      label: 'Description',
      render: (value: unknown) => (
        <span style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.bodySmall, fontFamily: theme.typography.fontFamily }}>
          {value ? truncateValue(String(value), 40) : <span style={{ color: theme.colors.textTertiary }}>—</span>}
        </span>
      ),
    },
    {
      key: 'is_public',
      label: 'Public',
      width: '80px',
      align: 'center' as const,
      render: (value: unknown) => (
        <Badge variant={value ? 'success' : 'default'}>
          {value ? 'Yes' : 'No'}
        </Badge>
      ),
    },
    {
      key: 'version',
      label: 'Version',
      width: '80px',
      align: 'center' as const,
      render: (value: unknown) => (
        <span style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.bodySmall, fontFamily: theme.typography.fontFamily }}>
          v{String(value)}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      width: '100px',
      sortable: true,
      render: (value: unknown) => (
        <span style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.bodySmall, fontFamily: theme.typography.fontFamily }}>
          {formatRelativeTime(String(value))}
        </span>
      ),
    },
    {
      key: 'actions',
      label: '',
      width: '100px',
      align: 'right' as const,
      render: (_value: unknown, row: Record<string, unknown>) => (
        <div style={{ display: 'flex', gap: theme.spacing[2], justifyContent: 'flex-end' }}>
          <button
            onClick={(e) => { e.stopPropagation(); onEdit(row as unknown as SystemConfig) }}
            style={{
              padding: '4px 8px',
              fontSize: theme.typography.sizes.caption,
              fontFamily: theme.typography.fontFamily,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              backgroundColor: 'transparent',
              color: theme.colors.textSecondary,
              cursor: 'pointer',
            }}
          >
            Edit
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(row as unknown as SystemConfig) }}
            style={{
              padding: '4px 8px',
              fontSize: theme.typography.sizes.caption,
              fontFamily: theme.typography.fontFamily,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              backgroundColor: 'transparent',
              color: theme.colors.danger,
              cursor: 'pointer',
            }}
          >
            Delete
          </button>
        </div>
      ),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={configs as unknown as Record<string, unknown>[]}
      loading={loading}
      error={error}
      errorRetry={onRetry}
      empty="No configurations found"
      sortable
      pagination={{
        page,
        perPage,
        total,
        perPageOptions: [10, 20, 50],
        onPageChange,
        onPerPageChange,
      }}
    />
  )
}
