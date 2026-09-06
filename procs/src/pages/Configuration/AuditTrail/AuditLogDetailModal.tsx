import { theme } from '../../../styles/theme'
import { Modal, StatusBadge } from '../../../components/shared'
import type { AuditLog } from '../../../types/monitoring'

interface AuditLogDetailModalProps {
  log: AuditLog | null
  open: boolean
  onClose: () => void
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

function formatDate(iso: string | null) {
  if (!iso) return '-'
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
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

export default function AuditLogDetailModal({ log, open, onClose }: AuditLogDetailModalProps) {
  return (
    <Modal open={open} onClose={onClose} title="Audit Log Detail" size="lg">
      {log && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
          <div style={{ display: 'flex', gap: theme.spacing[3], flexWrap: 'wrap' }}>
            <div>
              <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                Action
              </span>
              <div style={{ marginTop: theme.spacing[1] }}>
                <StatusBadge status={getActionBadge(log.action)} label={log.action} />
              </div>
            </div>
            <div>
              <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                Entity
              </span>
              <div style={{ marginTop: theme.spacing[1] }}>
                <StatusBadge status="info" label={log.entity_type} />
              </div>
            </div>
          </div>

          <DetailRow label="Timestamp" value={formatDate(log.created_at)} />
          <DetailRow label="Entity ID" value={log.entity_id || '-'} />
          <DetailRow label="User ID" value={log.user_id || '-'} />
          <DetailRow label="Description" value={log.description || '-'} />
          <DetailRow label="IP Address" value={log.ip_address || '-'} />
          <DetailRow label="HTTP Method" value={log.http_method || '-'} />
          <DetailRow label="Endpoint" value={log.endpoint || '-'} />
          <DetailRow label="Response Status" value={log.response_status?.toString() || '-'} />
          <DetailRow label="Processing Time" value={log.processing_time_ms ? `${log.processing_time_ms}ms` : '-'} />
          {log.error_message && (
            <DetailRow label="Error Message" value={log.error_message} />
          )}
          {log.user_agent && (
            <DetailRow label="User Agent" value={log.user_agent} />
          )}
          {log.previous_state && (
            <div>
              <span style={{ fontSize: theme.typography.sizes.bodySmall, fontWeight: theme.typography.weights.medium, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                Previous State
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
                maxHeight: '120px',
              }}>
                {log.previous_state}
              </pre>
            </div>
          )}
          {log.new_state && (
            <div>
              <span style={{ fontSize: theme.typography.sizes.bodySmall, fontWeight: theme.typography.weights.medium, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                New State
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
                maxHeight: '120px',
              }}>
                {log.new_state}
              </pre>
            </div>
          )}
          {log.metadata_json && (
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
                {log.metadata_json}
              </pre>
            </div>
          )}
        </div>
      )}
    </Modal>
  )
}
