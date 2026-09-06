import { theme } from '../../../../styles/theme'
import DataTable from '../../../../components/shared/DataTable'
import Switch from '../../../../components/shared/Switch'
import Badge from '../../../../components/shared/Badge'
import type { FeatureFlag } from '../types'

interface FeatureFlagTableProps {
  flags: FeatureFlag[]
  total: number
  loading: boolean
  error: string | null
  page: number
  perPage: number
  onPageChange: (page: number) => void
  onPerPageChange: (perPage: number) => void
  onToggle: (name: string, enabled: boolean) => void
  onEdit: (flag: FeatureFlag) => void
  onDelete: (flag: FeatureFlag) => void
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

export default function FeatureFlagTable({
  flags,
  total,
  loading,
  error,
  page,
  perPage,
  onPageChange,
  onPerPageChange,
  onToggle,
  onEdit,
  onDelete,
  onRetry,
}: FeatureFlagTableProps) {
  const columns = [
    {
      key: 'name',
      label: 'Name',
      sortable: true,
      render: (value: unknown) => (
        <span style={{ fontWeight: theme.typography.weights.medium, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
          {String(value)}
        </span>
      ),
    },
    {
      key: 'description',
      label: 'Description',
      render: (value: unknown) => (
        <span style={{ color: theme.colors.textSecondary, fontSize: theme.typography.sizes.bodySmall, fontFamily: theme.typography.fontFamily }}>
          {value ? String(value) : <span style={{ color: theme.colors.textTertiary }}>—</span>}
        </span>
      ),
    },
    {
      key: 'is_enabled',
      label: 'Enabled',
      width: '100px',
      render: (value: unknown, row: Record<string, unknown>) => (
        <Switch
          checked={Boolean(value)}
          onChange={(checked) => onToggle(String(row.name), checked)}
          size="sm"
        />
      ),
    },
    {
      key: 'rollout_percentage',
      label: 'Rollout',
      width: '90px',
      align: 'center' as const,
      render: (value: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, fontFamily: theme.typography.fontFamily }}>
          {String(value)}%
        </span>
      ),
    },
    {
      key: 'environment',
      label: 'Environment',
      width: '120px',
      render: (value: unknown) => {
        const env = String(value)
        const variant = env === 'production' ? 'danger' : env === 'staging' ? 'warning' : 'default'
        return <Badge variant={variant}>{env}</Badge>
      },
    },
    {
      key: 'allowed_tiers',
      label: 'Tiers',
      render: (value: unknown) => {
        const tiers = value as string[] | null
        if (!tiers || tiers.length === 0) return <span style={{ color: theme.colors.textTertiary, fontSize: theme.typography.sizes.bodySmall }}>All</span>
        return (
          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
            {tiers.map((tier) => (
              <Badge key={tier} variant="primary" size="sm">{tier}</Badge>
            ))}
          </div>
        )
      },
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
            onClick={(e) => { e.stopPropagation(); onEdit(row as unknown as FeatureFlag) }}
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
            onClick={(e) => { e.stopPropagation(); onDelete(row as unknown as FeatureFlag) }}
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
      data={flags as unknown as Record<string, unknown>[]}
      loading={loading}
      error={error}
      errorRetry={onRetry}
      empty="No feature flags found"
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
