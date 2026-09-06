import { useState } from 'react'
import { theme } from '../../../../styles/theme'
import Modal from '../../../../components/shared/Modal'
import type { SystemConfig } from '../types'

interface ConfigDeleteModalProps {
  open: boolean
  config: SystemConfig | null
  onClose: () => void
  onConfirm: (key: string) => Promise<void>
}

export default function ConfigDeleteModal({ open, config, onClose, onConfirm }: ConfigDeleteModalProps) {
  const [loading, setLoading] = useState(false)

  const handleConfirm = async () => {
    if (!config) return
    setLoading(true)
    try {
      await onConfirm(config.key)
      onClose()
    } catch {
      // error handled by parent
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Delete Configuration"
      size="sm"
      footer={
        <div style={{ display: 'flex', gap: theme.spacing[3] }}>
          <button
            onClick={onClose}
            disabled={loading}
            style={{
              padding: '8px 16px',
              fontSize: theme.typography.sizes.body,
              fontWeight: theme.typography.weights.medium,
              fontFamily: theme.typography.fontFamily,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              backgroundColor: 'transparent',
              color: theme.colors.text,
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            style={{
              padding: '8px 16px',
              fontSize: theme.typography.sizes.body,
              fontWeight: theme.typography.weights.semibold,
              fontFamily: theme.typography.fontFamily,
              border: 'none',
              borderRadius: theme.borderRadius.md,
              backgroundColor: theme.colors.danger,
              color: theme.colors.textInverse,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      }
    >
      <p style={{ margin: 0, fontSize: theme.typography.sizes.body, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
        Are you sure you want to delete the configuration <strong>{config?.key}</strong>?
      </p>
      <p style={{ margin: 0, marginTop: theme.spacing[3], fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
        This action cannot be undone.
      </p>
    </Modal>
  )
}
