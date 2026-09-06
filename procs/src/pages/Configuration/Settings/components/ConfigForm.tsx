import { useState } from 'react'
import { theme } from '../../../../styles/theme'
import Switch from '../../../../components/shared/Switch'
import type { SystemConfig } from '../types'

interface ConfigFormProps {
  config?: SystemConfig | null
  onSubmit: (data: Record<string, unknown>) => Promise<void>
  onCancel: () => void
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 12px',
  fontSize: theme.typography.sizes.body,
  fontFamily: theme.typography.fontFamily,
  border: `1px solid ${theme.colors.border}`,
  borderRadius: theme.borderRadius.md,
  outline: 'none',
  backgroundColor: theme.colors.surface,
  color: theme.colors.text,
  boxSizing: 'border-box',
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: theme.typography.sizes.bodySmall,
  fontWeight: theme.typography.weights.medium,
  color: theme.colors.textSecondary,
  marginBottom: theme.spacing[1],
  fontFamily: theme.typography.fontFamily,
}

export default function ConfigForm({ config, onSubmit, onCancel }: ConfigFormProps) {
  const [key, setKey] = useState(config?.key ?? '')
  const [value, setValue] = useState(config?.value ?? '')
  const [category, setCategory] = useState(config?.category ?? '')
  const [description, setDescription] = useState(config?.description ?? '')
  const [isPublic, setIsPublic] = useState(config?.is_public ?? false)
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    if (!config && !key.trim()) newErrors.key = 'Key is required'
    if (!value.trim()) newErrors.value = 'Value is required'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    try {
      if (config) {
        await onSubmit({
          value: value.trim(),
          category: category.trim() || undefined,
          description: description.trim() || undefined,
          is_public: isPublic,
        })
      } else {
        await onSubmit({
          key: key.trim(),
          value: value.trim(),
          category: category.trim() || undefined,
          description: description.trim() || undefined,
          is_public: isPublic,
        })
      }
    } catch {
      setErrors({ submit: 'Operation failed. Please try again.' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
        <div>
          <label style={labelStyle}>Key *</label>
          <input
            value={key}
            onChange={(e) => setKey(e.target.value)}
            disabled={!!config}
            placeholder="e.g. app.maintenance_mode"
            style={{
              ...inputStyle,
              opacity: config ? 0.6 : 1,
              borderColor: errors.key ? theme.colors.danger : theme.colors.border,
            }}
          />
          {errors.key && <span style={{ color: theme.colors.danger, fontSize: theme.typography.sizes.caption, marginTop: '4px', display: 'block' }}>{errors.key}</span>}
        </div>

        <div>
          <label style={labelStyle}>Value *</label>
          <textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Configuration value"
            rows={3}
            style={{
              ...inputStyle,
              resize: 'vertical',
              borderColor: errors.value ? theme.colors.danger : theme.colors.border,
            }}
          />
          {errors.value && <span style={{ color: theme.colors.danger, fontSize: theme.typography.sizes.caption, marginTop: '4px', display: 'block' }}>{errors.value}</span>}
        </div>

        <div>
          <label style={labelStyle}>Category</label>
          <input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g. app, auth, billing"
            style={inputStyle}
          />
        </div>

        <div>
          <label style={labelStyle}>Description</label>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional description"
            style={inputStyle}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <label style={{ ...labelStyle, marginBottom: 0 }}>Public</label>
          <Switch checked={isPublic} onChange={setIsPublic} />
        </div>

        {errors.submit && (
          <div style={{ padding: '8px 12px', backgroundColor: theme.colors.dangerBg, color: theme.colors.danger, borderRadius: theme.borderRadius.md, fontSize: theme.typography.sizes.bodySmall }}>
            {errors.submit}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: theme.spacing[3], marginTop: theme.spacing[6] }}>
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
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
          type="submit"
          disabled={submitting}
          style={{
            padding: '8px 16px',
            fontSize: theme.typography.sizes.body,
            fontWeight: theme.typography.weights.semibold,
            fontFamily: theme.typography.fontFamily,
            border: 'none',
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.primary,
            color: theme.colors.textInverse,
            cursor: submitting ? 'not-allowed' : 'pointer',
            opacity: submitting ? 0.7 : 1,
          }}
        >
          {submitting ? 'Saving...' : config ? 'Save Changes' : 'Create Config'}
        </button>
      </div>
    </form>
  )
}
