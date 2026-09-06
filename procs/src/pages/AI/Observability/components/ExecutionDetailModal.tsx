import { theme } from '../../../../styles/theme'
import { Modal, StatusBadge, Badge } from '../../../../components/shared'
import type { AiExecutionLog } from '../../../../types/ai-monitoring'

interface ExecutionDetailModalProps {
  execution: AiExecutionLog | null
  open: boolean
  onClose: () => void
}

function getStatusBadge(status: string) {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
    completed: 'success',
    failed: 'danger',
    pending: 'warning',
    running: 'info',
  }
  return map[status] || 'neutral'
}

function getProviderBadge(provider: string) {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'danger'> = {
    gemini: 'success',
    openai: 'primary',
    anthropic: 'warning',
  }
  return map[provider] || 'default' as const
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

export default function ExecutionDetailModal({ execution, open, onClose }: ExecutionDetailModalProps) {
  return (
    <Modal open={open} onClose={onClose} title="Execution Detail" size="lg">
      {execution && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
          <div style={{ display: 'flex', gap: theme.spacing[3], flexWrap: 'wrap' }}>
            <div>
              <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                Status
              </span>
              <div style={{ marginTop: theme.spacing[1] }}>
                <StatusBadge status={getStatusBadge(execution.status)} label={execution.status} />
              </div>
            </div>
            <div>
              <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
                Provider
              </span>
              <div style={{ marginTop: theme.spacing[1] }}>
                <Badge variant={getProviderBadge(execution.provider)}>{execution.provider}</Badge>
              </div>
            </div>
          </div>

          <DetailRow label="Execution ID" value={execution.id} />
          <DetailRow label="Model" value={execution.model} />
          <DetailRow label="Prompt Package ID" value={execution.prompt_package_id} />
          <DetailRow label="Timestamp" value={formatDate(execution.created_at)} />
          <DetailRow label="Total Tokens" value={execution.total_tokens != null ? execution.total_tokens.toLocaleString() : '-'} />
          <DetailRow label="Estimated Cost" value={execution.estimated_cost != null ? `$${execution.estimated_cost.toFixed(4)}` : '-'} />
          <DetailRow label="Latency" value={execution.execution_time_ms != null ? `${execution.execution_time_ms}ms` : '-'} />
        </div>
      )}
    </Modal>
  )
}
