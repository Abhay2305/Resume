import { theme } from '../../../../styles/theme'
import { Modal, StatusBadge } from '../../../../components/shared'
import type { ErrorLog } from '../../../../types/monitoring'

interface ErrorDetailModalProps {
  error: ErrorLog | null
  open: boolean
  onClose: () => void
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

function SectionHeader({ title }: { title: string }) {
  return (
    <div style={{
      fontSize: theme.typography.sizes.body,
      fontWeight: theme.typography.weights.semibold,
      color: theme.colors.text,
      fontFamily: theme.typography.fontFamily,
      paddingTop: theme.spacing[3],
      paddingBottom: theme.spacing[2],
      borderBottom: `1px solid ${theme.colors.border}`,
    }}>
      {title}
    </div>
  )
}

export default function ErrorDetailModal({ error, open, onClose }: ErrorDetailModalProps) {
  return (
    <Modal open={open} onClose={onClose} title="Error Detail" size="lg">
      {error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[3] }}>
          <div style={{ display: 'flex', gap: theme.spacing[3], flexWrap: 'wrap' }}>
            <div>
              <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                Severity
              </span>
              <div style={{ marginTop: theme.spacing[1] }}>
                <StatusBadge status={getSeverityBadge(error.severity)} label={error.severity} />
              </div>
            </div>
            <div>
              <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                Status
              </span>
              <div style={{ marginTop: theme.spacing[1] }}>
                <StatusBadge status={getStatusBadge(error.status)} label={error.status} />
              </div>
            </div>
          </div>

          <SectionHeader title="Error Information" />
          <DetailRow label="Error Type" value={error.error_type} />
          <DetailRow label="Message" value={error.error_message || '-'} />
          <DetailRow label="Timestamp" value={formatDate(error.created_at)} />
          <DetailRow label="Occurrence Count" value={error.occurrence_count.toString()} />
          <DetailRow label="First Seen" value={formatDate(error.first_occurrence_at)} />
          <DetailRow label="Last Seen" value={formatDate(error.last_occurrence_at)} />

          <SectionHeader title="Request Context" />
          <DetailRow label="Router" value={error.router || '-'} />
          <DetailRow label="Endpoint" value={error.endpoint || '-'} />
          <DetailRow label="HTTP Method" value={error.http_method || '-'} />
          <DetailRow label="Response Status" value={error.response_status?.toString() || '-'} />
          <DetailRow label="Processing Time" value={error.processing_time_ms ? `${error.processing_time_ms}ms` : '-'} />
          <DetailRow label="IP Address" value={error.ip_address || '-'} />
          <DetailRow label="User Agent" value={error.user_agent || '-'} />

          <SectionHeader title="Source Location" />
          <DetailRow label="Module" value={error.module || '-'} />
          <DetailRow label="Function" value={error.function || '-'} />
          <DetailRow label="File" value={error.file_path || '-'} />
          <DetailRow label="Line" value={error.line_number?.toString() || '-'} />

          <SectionHeader title="Identity" />
          <DetailRow label="User ID" value={error.user_id || '-'} />
          <DetailRow label="Session ID" value={error.session_id || '-'} />
          <DetailRow label="Request ID" value={error.request_id || '-'} />
          <DetailRow label="Correlation ID" value={error.correlation_id || '-'} />
          <DetailRow label="Environment" value={error.environment || '-'} />
          <DetailRow label="Retry Count" value={error.retry_count.toString()} />

          {error.stack_trace && (
            <div>
              <SectionHeader title="Stack Trace" />
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
                maxHeight: '300px',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
              }}>
                {error.stack_trace}
              </pre>
            </div>
          )}

          {error.request_payload && (
            <div>
              <SectionHeader title="Request Payload" />
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
                {error.request_payload}
              </pre>
            </div>
          )}

          {error.metadata_json && (
            <div>
              <SectionHeader title="Metadata" />
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
                {error.metadata_json}
              </pre>
            </div>
          )}
        </div>
      )}
    </Modal>
  )
}
