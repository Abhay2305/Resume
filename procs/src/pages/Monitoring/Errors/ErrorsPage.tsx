import { useState } from 'react'
import { theme } from '../../../styles/theme'
import { MetricCard } from '../../../components/shared'
import { useErrors } from './hooks/useErrors'
import ErrorTable from './components/ErrorTable'
import ErrorDetailModal from './components/ErrorDetailModal'
import type { ErrorLog } from '../../../types/monitoring'

const SEVERITIES = ['', 'critical', 'high', 'medium', 'low']
const STATUSES = ['', 'new', 'acknowledged', 'investigating', 'resolved', 'wont_fix']

export default function ErrorsPage() {
  const {
    errors, total, stats, loading, error, filters, setFilters, refresh,
    autoRefresh, setAutoRefresh,
  } = useErrors()
  const [selectedError, setSelectedError] = useState<ErrorLog | null>(null)
  const [searchInput, setSearchInput] = useState('')

  const handleSearch = (value: string) => {
    setSearchInput(value)
    setFilters({ search: value || undefined, page: 1 })
  }

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: theme.spacing[5] }}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: theme.typography.sizes.h1,
            fontWeight: theme.typography.weights.bold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
          }}>
            Error Center
          </h1>
          <p style={{
            margin: 0,
            marginTop: theme.spacing[1],
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}>
            Real-time error monitoring and investigation
          </p>
        </div>
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[2],
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.bodySmall,
            fontWeight: theme.typography.weights.medium,
            color: autoRefresh ? theme.colors.success : theme.colors.textSecondary,
            backgroundColor: autoRefresh ? theme.colors.successBg : theme.colors.surface,
            border: `1px solid ${autoRefresh ? theme.colors.success : theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            cursor: 'pointer',
            fontFamily: theme.typography.fontFamily,
          }}
        >
          <span style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: autoRefresh ? theme.colors.success : theme.colors.textTertiary,
            animation: autoRefresh ? 'pulse 2s infinite' : 'none',
          }} />
          {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
        </button>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <MetricCard
          title="Total Errors"
          value={stats?.total ?? 0}
          loading={loading}
          testId="metric-total-errors"
        />
        <MetricCard
          title="Critical"
          value={stats?.by_severity?.critical ?? 0}
          loading={loading}
          testId="metric-critical"
        />
        <MetricCard
          title="Open"
          value={(stats?.by_status?.new ?? 0) + (stats?.by_status?.acknowledged ?? 0)}
          loading={loading}
          testId="metric-open"
        />
        <MetricCard
          title="Resolved"
          value={stats?.by_status?.resolved ?? 0}
          loading={loading}
          testId="metric-resolved"
        />
        <MetricCard
          title="Resolution Rate"
          value={`${Math.round((stats?.resolution_rate ?? 0) * 100)}%`}
          loading={loading}
          testId="metric-resolution"
        />
      </div>

      <div style={{
        display: 'flex',
        gap: theme.spacing[3],
        marginBottom: theme.spacing[4],
        flexWrap: 'wrap',
      }}>
        <input
          type="text"
          placeholder="Search errors..."
          value={searchInput}
          onChange={(e) => handleSearch(e.target.value)}
          style={{
            flex: 1,
            minWidth: '200px',
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            outline: 'none',
          }}
        />
        <select
          value={filters.severity || ''}
          onChange={(e) => setFilters({ severity: e.target.value || undefined, page: 1 })}
          style={{
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            outline: 'none',
            minWidth: '130px',
          }}
        >
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>{s || 'All Severities'}</option>
          ))}
        </select>
        <select
          value={filters.status || ''}
          onChange={(e) => setFilters({ status: e.target.value || undefined, page: 1 })}
          style={{
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            outline: 'none',
            minWidth: '130px',
          }}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s || 'All Statuses'}</option>
          ))}
        </select>
        <select
          value={filters.router || ''}
          onChange={(e) => setFilters({ router: e.target.value || undefined, page: 1 })}
          style={{
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            outline: 'none',
            minWidth: '130px',
          }}
        >
          <option value="">All Routers</option>
          <option value="errors">errors</option>
          <option value="templates">templates</option>
          <option value="resumes">resumes</option>
          <option value="cover_letters">cover_letters</option>
          <option value="config">config</option>
          <option value="metrics">metrics</option>
          <option value="auth">auth</option>
        </select>
      </div>

      <ErrorTable
        errors={errors}
        loading={loading}
        error={error}
        onRefresh={refresh}
        onRowClick={setSelectedError}
        page={filters.page}
        perPage={filters.size}
        total={total}
        onPageChange={(p) => setFilters({ page: p })}
      />

      <ErrorDetailModal
        error={selectedError}
        open={!!selectedError}
        onClose={() => setSelectedError(null)}
      />
    </div>
  )
}
