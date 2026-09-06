import { ChevronLeft, ChevronRight } from 'lucide-react'
import { theme } from '../../styles/theme'

interface PaginationProps {
  page: number
  perPage: number
  total: number
  perPageOptions?: number[]
  onPageChange: (page: number) => void
  onPerPageChange?: (perPage: number) => void
  testId?: string
}

export default function Pagination({
  page,
  perPage,
  total,
  perPageOptions = [10, 25, 50, 100],
  onPageChange,
  onPerPageChange,
  testId,
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / perPage))
  const start = total === 0 ? 0 : (page - 1) * perPage + 1
  const end = Math.min(page * perPage, total)

  const getPageNumbers = (): (number | 'ellipsis')[] => {
    if (totalPages <= 5) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }
    const pages: (number | 'ellipsis')[] = [1]
    if (page > 3) pages.push('ellipsis')
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) {
      pages.push(i)
    }
    if (page < totalPages - 2) pages.push('ellipsis')
    pages.push(totalPages)
    return pages
  }

  const btnStyle = (active = false, disabled = false): React.CSSProperties => ({
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: '32px',
    height: '32px',
    padding: '0 8px',
    fontSize: theme.typography.sizes.bodySmall,
    fontWeight: active ? theme.typography.weights.medium : theme.typography.weights.regular,
    fontFamily: theme.typography.fontFamily,
    color: active ? theme.colors.textInverse : theme.colors.text,
    backgroundColor: active ? theme.colors.primary : 'transparent',
    border: active ? 'none' : `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.sm,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
  })

  return (
    <div
      data-testid={testId}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: theme.spacing[3],
      }}
    >
      <span
        style={{
          fontSize: theme.typography.sizes.bodySmall,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}
      >
        Showing {start}–{end} of {total}
      </span>

      <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          aria-label="Previous page"
          style={btnStyle(false, page <= 1)}
        >
          <ChevronLeft size={16} />
        </button>

        {getPageNumbers().map((p, i) =>
          p === 'ellipsis' ? (
            <span
              key={`e-${i}`}
              style={{
                padding: '0 4px',
                fontSize: theme.typography.sizes.bodySmall,
                color: theme.colors.textTertiary,
              }}
            >
              …
            </span>
          ) : (
            <button
              key={p}
              onClick={() => onPageChange(p)}
              aria-label={`Page ${p}`}
              aria-current={p === page ? 'page' : undefined}
              style={btnStyle(p === page)}
            >
              {p}
            </button>
          ),
        )}

        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          aria-label="Next page"
          style={btnStyle(false, page >= totalPages)}
        >
          <ChevronRight size={16} />
        </button>

        {onPerPageChange && (
          <select
            value={perPage}
            onChange={(e) => onPerPageChange(Number(e.target.value))}
            aria-label="Rows per page"
            style={{
              marginLeft: theme.spacing[2],
              padding: '4px 8px',
              fontSize: theme.typography.sizes.bodySmall,
              fontFamily: theme.typography.fontFamily,
              color: theme.colors.text,
              backgroundColor: theme.colors.surface,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              cursor: 'pointer',
            }}
          >
            {perPageOptions.map((opt) => (
              <option key={opt} value={opt}>
                {opt} / page
              </option>
            ))}
          </select>
        )}
      </div>
    </div>
  )
}
