import { useState } from 'react'
import { theme } from '../../../styles/theme'
import { Modal } from '../../../components/shared'
import { useAuditLogs } from './hooks/useAuditLogs'
import AuditLogTable from './components/AuditLogTable'
import type { AuditLog } from '../../../types/monitoring'

const ENTITY_TYPES = ['', 'user', 'resume', 'cover_letter', 'template', 'ai_execution', 'subscription', 'error', 'system', 'admin_auth', 'http_request']
const ACTIONS = ['', 'create', 'update', 'delete', 'login', 'login_failed', 'logout', 'error', 'export']

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

export default function SystemLogs() {
  const { logs, total, loading, error, filters, setFilters, refresh } = useAuditLogs()
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)
  const [searchInput, setSearchInput] = useState('')

  const handleSearch = (value: string) => {
    setSearchInput(value)
    setFilters({ search: value || undefined, page: 1 })
  }

  const handleEntityTypeChange = (value: string) => {
    setFilters({ entity_type: value || undefined, page: 1 })
  }

  const handleActionChange = (value: string) => {
    setFilters({ action: value || undefined, page: 1 })
  }

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{ marginBottom: theme.spacing[5] }}>
        <h1 style={{
          margin: 0,
          fontSize: theme.typography.sizes.h1,
          fontWeight: theme.typography.weights.bold,
          color: theme.colors.text,
          fontFamily: theme.typography.fontFamily,
        }}>
          System Logs
        </h1>
        <p style={{
          margin: 0,
          marginTop: theme.spacing[1],
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}>
          View audit trail of all system activities
        </p>
      </div>

      <div style={{
        display: 'flex',
        gap: theme.spacing[3],
        marginBottom: theme.spacing[4],
        flexWrap: 'wrap',
      }}>
        <input
          type="text"
          placeholder="Search logs..."
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
          onChange={(e) => handleEntityTypeChange(e.target.value)}
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
          onChange={(e) => handleActionChange(e.target.value)}
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

      <Modal
        open={!!selectedLog}
        onClose={() => setSelectedLog(null)}
        title="Audit Log Detail"
        size="lg"
      >
        {selectedLog && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
            <DetailRow label="Timestamp" value={formatDate(selectedLog.created_at)} />
            <DetailRow label="Action" value={selectedLog.action} />
            <DetailRow label="Entity Type" value={selectedLog.entity_type} />
            <DetailRow label="Entity ID" value={selectedLog.entity_id || '-'} />
            <DetailRow label="User ID" value={selectedLog.user_id || '-'} />
            <DetailRow label="Description" value={selectedLog.description || '-'} />
            <DetailRow label="IP Address" value={selectedLog.ip_address || '-'} />
            <DetailRow label="HTTP Method" value={selectedLog.http_method || '-'} />
            <DetailRow label="Endpoint" value={selectedLog.endpoint || '-'} />
            <DetailRow label="Response Status" value={selectedLog.response_status?.toString() || '-'} />
            <DetailRow label="Processing Time" value={selectedLog.processing_time_ms ? `${selectedLog.processing_time_ms}ms` : '-'} />
            {selectedLog.error_message && (
              <DetailRow label="Error Message" value={selectedLog.error_message} />
            )}
            {selectedLog.metadata_json && (
              <div>
                <span style={{ fontSize: theme.typography.sizes.bodySmall, fontWeight: theme.typography.weights.medium, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                  Metadata
                </span>
                <pre style={{
                  marginTop: theme.spacing[1],
                  padding: theme.spacing[3],
                  backgroundColor: theme.colors.background,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  fontSize: theme.typography.sizes.bodySmall,
                  color: theme.colors.text,
                  fontFamily: theme.typography.fontFamily,
                  overflow: 'auto',
                  maxHeight: '200px',
                }}>
                  {selectedLog.metadata_json}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', gap: theme.spacing[3] }}>
      <span style={{
        minWidth: '140px',
        fontSize: theme.typography.sizes.bodySmall,
        fontWeight: theme.typography.weights.medium,
        color: theme.colors.textSecondary,
        fontFamily: theme.typography.fontFamily,
      }}>
        {label}
      </span>
      <span style={{
        fontSize: theme.typography.sizes.body,
        color: theme.colors.text,
        fontFamily: theme.typography.fontFamily,
        wordBreak: 'break-all',
      }}>
        {value}
      </span>
    </div>
  )
}
