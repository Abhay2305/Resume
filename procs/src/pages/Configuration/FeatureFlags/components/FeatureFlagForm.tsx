import { useState } from 'react'
import { theme } from '../../../../styles/theme'
import Switch from '../../../../components/shared/Switch'
import type { FeatureFlag } from '../types'

interface FeatureFlagFormProps {
  flag?: FeatureFlag | null
  onSubmit: (data: Record<string, unknown>) => Promise<void>
  onCancel: () => void
}

const ENVIRONMENTS = ['all', 'production', 'staging', 'development']

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

export default function FeatureFlagForm({ flag, onSubmit, onCancel }: FeatureFlagFormProps) {
  const [name, setName] = useState(flag?.name ?? '')
  const [description, setDescription] = useState(flag?.description ?? '')
  const [isEnabled, setIsEnabled] = useState(flag?.is_enabled ?? false)
  const [rolloutPercentage, setRolloutPercentage] = useState(flag?.rollout_percentage ?? 100)
  const [environment, setEnvironment] = useState(flag?.environment ?? 'all')
  const [allowedTiers, setAllowedTiers] = useState(flag?.allowed_tiers?.join(', ') ?? '')
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    if (!name.trim()) newErrors.name = 'Name is required'
    if (rolloutPercentage < 0 || rolloutPercentage > 100) newErrors.rollout_percentage = 'Must be 0-100'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    try {
      const tiers = allowedTiers
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)
      await onSubmit({
        name: name.trim(),
        description: description.trim() || undefined,
        is_enabled: isEnabled,
        rollout_percentage: rolloutPercentage,
        environment,
        allowed_tiers: tiers.length > 0 ? tiers : undefined,
      })
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
          <label style={labelStyle}>Name *</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={!!flag}
            // Name is immutable — it is the primary identifier used in API path params (/config/flags/{name})
            placeholder="e.g. new_dashboard"
            style={{
              ...inputStyle,
              opacity: flag ? 0.6 : 1,
              borderColor: errors.name ? theme.colors.danger : theme.colors.border,
            }}
          />
          {errors.name && <span style={{ color: theme.colors.danger, fontSize: theme.typography.sizes.caption, marginTop: '4px', display: 'block' }}>{errors.name}</span>}
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
          <label style={{ ...labelStyle, marginBottom: 0 }}>Enabled</label>
          <Switch checked={isEnabled} onChange={setIsEnabled} />
        </div>

        <div>
          <label style={labelStyle}>Rollout Percentage</label>
          <input
            type="number"
            min={0}
            max={100}
            value={rolloutPercentage}
            onChange={(e) => setRolloutPercentage(Number(e.target.value))}
            style={{
              ...inputStyle,
              borderColor: errors.rollout_percentage ? theme.colors.danger : theme.colors.border,
            }}
          />
          {errors.rollout_percentage && <span style={{ color: theme.colors.danger, fontSize: theme.typography.sizes.caption, marginTop: '4px', display: 'block' }}>{errors.rollout_percentage}</span>}
        </div>

        <div>
          <label style={labelStyle}>Environment</label>
          <select
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            style={{ ...inputStyle, cursor: 'pointer' }}
          >
            {ENVIRONMENTS.map((env) => (
              <option key={env} value={env}>{env}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={labelStyle}>Allowed Tiers (comma-separated)</label>
          <input
            value={allowedTiers}
            onChange={(e) => setAllowedTiers(e.target.value)}
            placeholder="e.g. premium, enterprise"
            style={inputStyle}
          />
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
          {submitting ? 'Saving...' : flag ? 'Save Changes' : 'Create Flag'}
        </button>
      </div>
    </form>
  )
}
