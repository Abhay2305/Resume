import { useState } from 'react'
import { ChevronUp, ChevronDown } from 'lucide-react'
import { theme } from '../../styles/theme'
import Skeleton from './Skeleton'
import EmptyState from './EmptyState'
import Pagination from './Pagination'
import Button from './Button'
import Alert from './Alert'

interface Column<T = Record<string, unknown>> {
  key: string
  label: string
  sortable?: boolean
  width?: string | number
  align?: 'left' | 'center' | 'right'
  render?: (value: unknown, row: T, index: number) => React.ReactNode
  truncate?: boolean
}

interface BulkAction {
  label: string
  icon?: React.ReactNode
  onClick: (selectedRows: unknown[]) => void
  variant?: 'primary' | 'danger'
}

interface PaginationConfig {
  page: number
  perPage: number
  total: number
  perPageOptions?: number[]
  onPageChange: (page: number) => void
  onPerPageChange?: (perPage: number) => void
}

interface DataTableProps<T = Record<string, unknown>> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  error?: string | null
  errorRetry?: () => void
  empty?: string
  emptyIcon?: React.ComponentType<{ size?: number; color?: string }>
  sortable?: boolean
  selectable?: boolean
  pagination?: PaginationConfig
  onSort?: (key: string, direction: 'asc' | 'desc') => void
  onRowClick?: (row: T, index: number) => void
  onSelectionChange?: (selectedRows: T[]) => void
  bulkActions?: BulkAction[]
  testId?: string
}

export default function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  loading = false,
  error = null,
  errorRetry,
  empty = 'No data available',
  emptyIcon,
  sortable = false,
  selectable = false,
  pagination,
  onSort,
  onRowClick,
  onSelectionChange,
  bulkActions,
  testId,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
  const [selected, setSelected] = useState<Set<number>>(new Set())

  const handleSort = (key: string) => {
    if (!sortable) return
    const newDir = sortKey === key && sortDir === 'asc' ? 'desc' : 'asc'
    setSortKey(key)
    setSortDir(newDir)
    onSort?.(key, newDir)
  }

  const handleSelectAll = () => {
    if (selected.size === data.length) {
      setSelected(new Set())
      onSelectionChange?.([])
    } else {
      const all = new Set(data.map((_, i) => i))
      setSelected(all)
      onSelectionChange?.(data)
    }
  }

  const handleSelectRow = (index: number) => {
    const next = new Set(selected)
    if (next.has(index)) {
      next.delete(index)
    } else {
      next.add(index)
    }
    setSelected(next)
    onSelectionChange?.(data.filter((_, i) => next.has(i)))
  }

  const displayColumns = selectable
    ? [{ key: '__select', label: '', sortable: false, width: '40px' as const }, ...columns]
    : columns

  if (loading) {
    return (
      <div data-testid={testId} style={{ border: `1px solid ${theme.colors.border}`, borderRadius: theme.borderRadius.md, overflow: 'hidden' }}>
        <div style={{ padding: `0 ${theme.spacing[4]}` }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', height: theme.layout.tableRowHeight, borderBottom: `1px solid ${theme.colors.divider}` }}>
              {displayColumns.map((col, j) => (
                <div key={j} style={{ flex: col.width ? undefined : 1, width: col.width, padding: `0 ${theme.spacing[4]}` }}>
                  <Skeleton variant="text" height="14px" />
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div data-testid={testId}>
        <Alert variant="error" title="Failed to load data" action={errorRetry ? { label: 'Retry', onClick: errorRetry } : undefined}>
          {error}
        </Alert>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div data-testid={testId} style={{ border: `1px solid ${theme.colors.border}`, borderRadius: theme.borderRadius.md }}>
        <EmptyState title={empty} icon={emptyIcon} />
      </div>
    )
  }

  return (
    <div data-testid={testId}>
      {selected.size > 0 && bulkActions && bulkActions.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[3],
            padding: `${theme.spacing[2]} ${theme.spacing[4]}`,
            marginBottom: theme.spacing[3],
            backgroundColor: theme.colors.primaryLight + '20',
            border: `1px solid ${theme.colors.primary}30`,
            borderRadius: theme.borderRadius.md,
          }}
        >
          <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
            {selected.size} selected
          </span>
          <div style={{ display: 'flex', gap: theme.spacing[2] }}>
            {bulkActions.map((action, i) => (
              <Button
                key={i}
                variant={action.variant || 'secondary'}
                size="sm"
                icon={action.icon}
                onClick={() => action.onClick(data.filter((_, idx) => selected.has(idx)))}
              >
                {action.label}
              </Button>
            ))}
          </div>
        </div>
      )}

      <div style={{ border: `1px solid ${theme.colors.border}`, borderRadius: theme.borderRadius.md, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontFamily: theme.typography.fontFamily,
              fontSize: theme.typography.sizes.body,
            }}
          >
            <thead>
              <tr>
                {displayColumns.map((col) => (
                  <th
                    key={col.key}
                    scope="col"
                    onClick={col.key === '__select' ? undefined : col.sortable !== false && sortable ? () => handleSort(col.key) : undefined}
                    onKeyDown={col.key === '__select' ? undefined : col.sortable !== false && sortable ? (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSort(col.key) } } : undefined}
                    tabIndex={col.key !== '__select' && col.sortable !== false && sortable ? 0 : undefined}
                    aria-sort={sortKey === col.key ? (sortDir === 'asc' ? 'ascending' : 'descending') : undefined}
                    style={{
                      padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
                      textAlign: (col.align || 'left') as 'left',
                      fontWeight: theme.typography.weights.medium,
                      fontSize: theme.typography.sizes.bodySmall,
                      color: theme.colors.textSecondary,
                      backgroundColor: theme.colors.surface,
                      borderBottom: `1px solid ${theme.colors.border}`,
                      whiteSpace: 'nowrap',
                      cursor: col.sortable !== false && sortable ? 'pointer' : 'default',
                      userSelect: 'none',
                      width: col.width,
                    }}
                  >
                    {col.key === '__select' ? (
                      <input
                        type="checkbox"
                        checked={selected.size === data.length && data.length > 0}
                        onChange={handleSelectAll}
                        aria-label="Select all"
                      />
                    ) : (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                        {col.label}
                        {sortable && col.sortable !== false && sortKey === col.key && (
                          sortDir === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />
                        )}
                      </span>
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  onClick={onRowClick ? () => onRowClick(row, rowIndex) : undefined}
                  style={{
                    cursor: onRowClick ? 'pointer' : 'default',
                    backgroundColor: selected.has(rowIndex) ? theme.colors.primaryLight + '10' : undefined,
                  }}
                  onMouseEnter={(e) => {
                    if (!selected.has(rowIndex)) {
                      (e.currentTarget as HTMLElement).style.backgroundColor = theme.colors.surfaceHover
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!selected.has(rowIndex)) {
                      (e.currentTarget as HTMLElement).style.backgroundColor = ''
                    }
                  }}
                >
                  {displayColumns.map((col) => (
                    <td
                      key={col.key}
                      style={{
                        padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
                        textAlign: (col.align || 'left') as 'left',
                        borderBottom: `1px solid ${theme.colors.divider}`,
                        color: theme.colors.text,
                        maxWidth: col.width || undefined,
                        overflow: col.truncate ? 'hidden' : undefined,
                        textOverflow: col.truncate ? 'ellipsis' : undefined,
                        whiteSpace: col.truncate ? 'nowrap' : undefined,
                      }}
                    >
                      {col.key === '__select' ? (
                        <input
                          type="checkbox"
                          checked={selected.has(rowIndex)}
                          onChange={() => handleSelectRow(rowIndex)}
                          onClick={(e) => e.stopPropagation()}
                          aria-label={`Select row ${rowIndex + 1}`}
                        />
                      ) : col.render ? (
                        col.render(row[col.key], row, rowIndex)
                      ) : (
                        <span title={col.truncate ? String(row[col.key] ?? '') : undefined}>
                          {String(row[col.key] ?? '')}
                        </span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {pagination && (
        <div style={{ marginTop: theme.spacing[3] }}>
          <Pagination
            page={pagination.page}
            perPage={pagination.perPage}
            total={pagination.total}
            perPageOptions={pagination.perPageOptions}
            onPageChange={pagination.onPageChange}
            onPerPageChange={pagination.onPerPageChange}
          />
        </div>
      )}
    </div>
  )
}
