import Modal from '../../../../components/shared/Modal'
import FeatureFlagForm from './FeatureFlagForm'
import type { FeatureFlag } from '../types'

interface FeatureFlagModalProps {
  open: boolean
  flag?: FeatureFlag | null
  onClose: () => void
  onSubmit: (data: Record<string, unknown>) => Promise<void>
}

export default function FeatureFlagModal({ open, flag, onClose, onSubmit }: FeatureFlagModalProps) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={flag ? 'Edit Feature Flag' : 'Create Feature Flag'}
      description={flag ? `Editing ${flag.name}` : 'Add a new feature flag'}
      size="md"
    >
      <FeatureFlagForm flag={flag} onSubmit={onSubmit} onCancel={onClose} />
    </Modal>
  )
}
