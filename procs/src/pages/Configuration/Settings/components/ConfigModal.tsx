import Modal from '../../../../components/shared/Modal'
import ConfigForm from './ConfigForm'
import type { SystemConfig } from '../types'

interface ConfigModalProps {
  open: boolean
  config?: SystemConfig | null
  onClose: () => void
  onSubmit: (data: Record<string, unknown>) => Promise<void>
}

export default function ConfigModal({ open, config, onClose, onSubmit }: ConfigModalProps) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={config ? 'Edit Configuration' : 'Create Configuration'}
      description={config ? `Editing ${config.key}` : 'Add a new system configuration'}
      size="md"
    >
      <ConfigForm config={config} onSubmit={onSubmit} onCancel={onClose} />
    </Modal>
  )
}
