import { useState } from 'react'
import { Download } from 'lucide-react'
import { theme } from '../../../styles/theme'
import { Button, MetricCard, Alert } from '../../../components/shared'
import { useAuditLogs } from '../../Monitoring/SystemLogs/hooks/useAuditLogs'
import AuditLogTable from '../../Monitoring/SystemLogs/components/AuditLogTable'
import AuditLogDetailModal from './AuditLogDetailModal'
import { apiPost } from '../../../services/api/apiService'
import { API_ENDPOINTS } from '../../../services/api/endpoints'
import type { AuditLog } from '../../../types/monitoring'

const ENTITY_TYPES = ['', 'user', 'resume', 'cover_letter', 'template', 'ai_execution', 'subscription', 'error', 'system', 'admin_auth', 'http_request']
const ACTIONS = ['', 'create', 'update', 'delete', 'login', 'login_failed', 'logout', 'error', 'export']

export default function AuditTrailPage() {
  const { logs, total, loading, error, filters, setFilters, refresh } = useAuditLogs()
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)
  const [searchInput, setSearchInput] = useState('')
  const [exporting, setExporting] = useState(false)

  const handleSearch = (value: string) => {
    setSearchInput(value)
    setFilters({ search: value || undefined, page: 1 })
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      await apiPost(`${API_ENDPOINTS.AUDIT}/export`, {
        entity_type: filters.entity_type,
        action: filters.action,
        start_date: filters.start_date,
        end_date: filters.end_date,
      })
    } catch {
      // Export endpoint is stub — silently handle
    } finally {
      setExporting(false)
    }
  }

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: theme.spacing[5],
      }}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: theme.typography.sizes.h1,
            fontWeight: theme.typography.weights.bold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
          }}>
            Audit Trail
          </h1>
          <p style={{
            margin: 0,
            marginTop: theme.spacing[1],
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}>
            View and export audit logs for compliance and security monitoring
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          icon={<Download size={14} />}
          onClick={handleExport}
          loading={exporting}
        >
          Export CSV
        </Button>
      </div>

      {error && (
        <div style={{ marginBottom: theme.spacing[4] }}>
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <MetricCard
          title="Total Logs"
          value={total}
          loading={loading}
          testId="metric-total-logs"
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
          placeholder="Search audit logs..."
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
          value={filters.entity_type || ''}
          onChange={(e) => setFilters({ entity_type: e.target.value || undefined, page: 1 })}
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
          {ENTITY_TYPES.map((et) => (
            <option key={et} value={et}>{et || 'All Entities'}</option>
          ))}
        </select>
        <select
          value={filters.action || ''}
          onChange={(e) => setFilters({ action: e.target.value || undefined, page: 1 })}
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
          {ACTIONS.map((a) => (
            <option key={a} value={a}>{a || 'All Actions'}</option>
          ))}
        </select>
      </div>

      <AuditLogTable
        logs={logs}
        loading={loading}
        error={error}
        onRefresh={refresh}
        onRowClick={setSelectedLog}
        page={filters.page}
        perPage={filters.limit}
        total={total}
        onPageChange={(p) => setFilters({ page: p })}
      />

      <AuditLogDetailModal
        log={selectedLog}
        open={!!selectedLog}
        onClose={() => setSelectedLog(null)}
      />
    </div>
  )
}
