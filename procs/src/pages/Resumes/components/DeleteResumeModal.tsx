import { useState } from 'react'
import Modal from '../../../components/shared/Modal'
import Button from '../../../components/shared/Button'
import { theme } from '../../../styles/theme'

interface DeleteResumeModalProps {
  open: boolean
  onClose: () => void
  resumeTitle: string
  onDelete: () => Promise<void>
}

export default function DeleteResumeModal({ open, onClose, resumeTitle, onDelete }: DeleteResumeModalProps) {
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDelete = async () => {
    setDeleting(true)
    setError(null)

    try {
      await onDelete()
      onClose()
    } catch {
      setError('Failed to delete resume. Please try again.')
    } finally {
      setDeleting(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Delete Resume"
      description="This action cannot be undone."
      size="sm"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={deleting}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={deleting}>
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </>
      }
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[3] }}>
        {error && (
          <div
            style={{
              padding: theme.spacing[3],
              backgroundColor: theme.colors.dangerBg,
              border: `1px solid ${theme.colors.danger}`,
              borderRadius: theme.borderRadius.sm,
              color: theme.colors.danger,
              fontSize: theme.typography.sizes.bodySmall,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            {error}
          </div>
        )}

        <p
          style={{
            margin: 0,
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          Are you sure you want to delete <strong>{resumeTitle}</strong>?
        </p>
        <p
          style={{
            margin: 0,
            fontSize: theme.typography.sizes.bodySmall,
            color: theme.colors.textTertiary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          This will permanently remove the resume and all its sections. This action cannot be undone.
        </p>
      </div>
    </Modal>
  )
}
