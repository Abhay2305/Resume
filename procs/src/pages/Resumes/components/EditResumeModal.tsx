import { useState, useEffect } from 'react'
import Modal from '../../../components/shared/Modal'
import Button from '../../../components/shared/Button'
import { theme } from '../../../styles/theme'
import { getTemplates } from '../../../services/api/resume.service'
import type { ResumeDetail, ResumeUpdateData, TemplateListItem } from '../types'

interface EditResumeModalProps {
  open: boolean
  onClose: () => void
  resume: ResumeDetail
  onSave: (data: ResumeUpdateData) => Promise<void>
}

export default function EditResumeModal({ open, onClose, resume, onSave }: EditResumeModalProps) {
  const [title, setTitle] = useState(resume.title)
  const [templateId, setTemplateId] = useState(resume.template_id)
  const [status, setStatus] = useState<'draft' | 'published'>(resume.status)
  const [templates, setTemplates] = useState<TemplateListItem[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      setTitle(resume.title)
      setTemplateId(resume.template_id)
      setStatus(resume.status)
      setError(null)
    }
  }, [open, resume])

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await getTemplates() as { data?: { items?: TemplateListItem[] } }
        setTemplates(response.data?.items || [])
      } catch {
        // Templates load failure is non-critical
      }
    }
    if (open) {
      fetchTemplates()
    }
  }, [open])

  const handleSave = async () => {
    if (!title.trim()) {
      setError('Title is required.')
      return
    }

    setSaving(true)
    setError(null)

    try {
      await onSave({
        title: title.trim(),
        template_id: templateId,
        status,
      })
      onClose()
    } catch {
      setError('Failed to update resume. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Edit Resume"
      size="md"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </>
      }
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
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

        <div>
          <label
            htmlFor="resume-title"
            style={{
              display: 'block',
              marginBottom: theme.spacing[1],
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.text,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            Title
          </label>
          <input
            id="resume-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={saving}
            style={{
              width: '100%',
              padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              fontSize: theme.typography.sizes.body,
              fontFamily: theme.typography.fontFamily,
              backgroundColor: theme.colors.surface,
              color: theme.colors.text,
              outline: 'none',
            }}
          />
        </div>

        <div>
          <label
            htmlFor="resume-template"
            style={{
              display: 'block',
              marginBottom: theme.spacing[1],
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.text,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            Template
          </label>
          <select
            id="resume-template"
            value={templateId}
            onChange={(e) => setTemplateId(e.target.value)}
            disabled={saving}
            style={{
              width: '100%',
              padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              fontSize: theme.typography.sizes.body,
              fontFamily: theme.typography.fontFamily,
              backgroundColor: theme.colors.surface,
              color: theme.colors.text,
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="resume-status"
            style={{
              display: 'block',
              marginBottom: theme.spacing[1],
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.text,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            Status
          </label>
          <select
            id="resume-status"
            value={status}
            onChange={(e) => setStatus(e.target.value as 'draft' | 'published')}
            disabled={saving}
            style={{
              width: '100%',
              padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              fontSize: theme.typography.sizes.body,
              fontFamily: theme.typography.fontFamily,
              backgroundColor: theme.colors.surface,
              color: theme.colors.text,
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </div>
      </div>
    </Modal>
  )
}
