import { useState, useEffect } from 'react'
import { theme } from '../../../styles/theme'
import Modal from '../../../components/shared/Modal'
import Button from '../../../components/shared/Button'
import Skeleton from '../../../components/shared/Skeleton'
import { getTemplateVersions, restoreTemplateVersion } from '../../../services/api/templateCms.service'
import type { TemplateCmsItem, TemplateVersion } from '../types'

interface TemplateViewModalProps {
  open: boolean
  onClose: () => void
  template: TemplateCmsItem | null
  onRefresh: () => void
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

const labelStyle: React.CSSProperties = {
  fontSize: theme.typography.sizes.caption,
  fontWeight: theme.typography.weights.medium,
  color: theme.colors.textTertiary,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  marginBottom: '4px',
}

const valueStyle: React.CSSProperties = {
  fontSize: theme.typography.sizes.body,
  color: theme.colors.text,
  fontFamily: theme.typography.fontFamily,
}

const sectionHeaderStyle: React.CSSProperties = {
  fontSize: theme.typography.sizes.caption,
  fontWeight: theme.typography.weights.semibold,
  color: theme.colors.primary,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  marginBottom: theme.spacing[3],
  paddingBottom: theme.spacing[2],
  borderBottom: `1px solid ${theme.colors.border}`,
}

export default function TemplateViewModal({ open, onClose, template, onRefresh }: TemplateViewModalProps) {
  const [versions, setVersions] = useState<TemplateVersion[]>([])
  const [versionsLoading, setVersionsLoading] = useState(false)
  const [restoring, setRestoring] = useState<string | null>(null)

  useEffect(() => {
    if (!open || !template) return
    setVersionsLoading(true)
    getTemplateVersions(template.id)
      .then((res) => {
        const data = res as { items?: TemplateVersion[] }
        setVersions(data.items || [])
      })
      .catch(() => setVersions([]))
      .finally(() => setVersionsLoading(false))
  }, [open, template])

  const handleRestore = async (version: TemplateVersion) => {
    if (!template) return
    setRestoring(version.id)
    try {
      await restoreTemplateVersion(template.id, version.id)
      onRefresh()
      onClose()
    } catch {
      // error handled silently
    } finally {
      setRestoring(null)
    }
  }

  if (!template) return null

  const def = template.template_definition as Record<string, unknown> | null
  const layout = def?.layout as Record<string, string> | undefined
  const colors = def?.colors as Record<string, string> | undefined
  const font = def?.font as Record<string, string> | undefined
  const sections = def?.sections as Record<string, string[]> | undefined

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={template.name}
      description={`Template ID: ${template.id}`}
      size="lg"
      footer={
        <Button variant="secondary" onClick={onClose}>Close</Button>
      }
    >
      {/* Thumbnail & Preview */}
      <div style={{ marginBottom: theme.spacing[6] }}>
        <div style={sectionHeaderStyle}>Assets</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <label style={labelStyle}>Thumbnail</label>
            <div style={{ width: '100%', height: '120px', borderRadius: theme.borderRadius.md, overflow: 'hidden', border: `1px solid ${theme.colors.border}`, backgroundColor: theme.colors.surfaceHover }}>
              {template.thumbnail_url ? (
                <img src={template.thumbnail_url} alt="Thumbnail" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <div style={{ width: '100%', height: '100%', background: `linear-gradient(135deg, ${template.color_scheme?.primary || '#7BC4BE'} 0%, ${template.color_scheme?.secondary || '#F6B233'} 100%)` }} />
              )}
            </div>
          </div>
          <div>
            <label style={labelStyle}>Preview Images</label>
            <div style={{ display: 'flex', gap: '4px', height: '120px', overflow: 'auto' }}>
              {template.preview_images && template.preview_images.length > 0 ? (
                template.preview_images.map((src, i) => (
                  <img key={i} src={src} alt={`Preview ${i + 1}`} style={{ height: '100%', borderRadius: theme.borderRadius.sm, objectFit: 'cover', flexShrink: 0 }} />
                ))
              ) : (
                <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.colors.textTertiary, fontSize: theme.typography.sizes.caption, backgroundColor: theme.colors.surfaceHover, borderRadius: theme.borderRadius.md }}>
                  No preview images
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Basic Info */}
      <div style={{ marginBottom: theme.spacing[6] }}>
        <div style={sectionHeaderStyle}>Basic Information</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <div style={labelStyle}>Name</div>
            <div style={valueStyle}>{template.name}</div>
          </div>
          <div>
            <div style={labelStyle}>Category</div>
            <div style={valueStyle}>{template.category}</div>
          </div>
          <div>
            <div style={labelStyle}>Status</div>
            <div style={{ ...valueStyle, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{
                width: '8px', height: '8px', borderRadius: '50%',
                backgroundColor: template.status === 'published' ? theme.colors.success : template.status === 'archived' ? theme.colors.textSecondary : theme.colors.warning,
              }} />
              {template.status}
            </div>
          </div>
          <div>
            <div style={labelStyle}>Version</div>
            <div style={valueStyle}>v{template.version}</div>
          </div>
          <div>
            <div style={labelStyle}>Created</div>
            <div style={valueStyle}>{formatDate(template.created_at)}</div>
          </div>
          <div>
            <div style={labelStyle}>Updated</div>
            <div style={valueStyle}>{formatDate(template.updated_at)}</div>
          </div>
          <div>
            <div style={labelStyle}>Published</div>
            <div style={valueStyle}>{formatDate(template.published_at)}</div>
          </div>
          <div>
            <div style={labelStyle}>Usage Count</div>
            <div style={valueStyle}>{template.usage_count}</div>
          </div>
        </div>
        {template.description && (
          <div style={{ marginTop: theme.spacing[4] }}>
            <div style={labelStyle}>Description</div>
            <div style={valueStyle}>{template.description}</div>
          </div>
        )}
      </div>

      {/* Template Definition */}
      <div style={{ marginBottom: theme.spacing[6] }}>
        <div style={sectionHeaderStyle}>Template Definition</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <div style={labelStyle}>Layout</div>
            <div style={valueStyle}>{layout?.structure || '—'}</div>
          </div>
          <div>
            <div style={labelStyle}>Header Style</div>
            <div style={valueStyle}>{layout?.headerStyle || '—'}</div>
          </div>
          <div>
            <div style={labelStyle}>Font</div>
            <div style={valueStyle}>{font?.heading || '—'}</div>
          </div>
          <div>
            <div style={labelStyle}>Margins</div>
            <div style={valueStyle}>{layout?.margins || '—'}</div>
          </div>
        </div>
        <div style={{ marginTop: theme.spacing[4] }}>
          <div style={labelStyle}>Colors</div>
          <div style={{ display: 'flex', gap: theme.spacing[3], marginTop: '4px' }}>
            {colors && Object.entries(colors).map(([name, hex]) => (
              <div key={name} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '16px', height: '16px', borderRadius: '4px', backgroundColor: hex, border: `1px solid ${theme.colors.border}`, display: 'inline-block' }} />
                <span style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary }}>{name}</span>
              </div>
            ))}
          </div>
        </div>
        {sections && (
          <div style={{ marginTop: theme.spacing[4] }}>
            <div style={labelStyle}>Section Order</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
              {(sections.order || []).map((s: string, i: number) => (
                <span key={i} style={{ padding: '2px 8px', backgroundColor: theme.colors.surfaceHover, borderRadius: theme.borderRadius.sm, fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary }}>
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Version History */}
      <div>
        <div style={sectionHeaderStyle}>Version History</div>
        {versionsLoading ? (
          <Skeleton variant="text" lines={3} />
        ) : versions.length === 0 ? (
          <div style={{ color: theme.colors.textTertiary, fontSize: theme.typography.sizes.bodySmall }}>No version history available</div>
        ) : (
          <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
            {versions.map((v) => (
              <div key={v.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: `${theme.spacing[2]} ${theme.spacing[3]}`, borderBottom: `1px solid ${theme.colors.divider}` }}>
                <div>
                  <span style={{ fontSize: theme.typography.sizes.body, fontWeight: theme.typography.weights.medium, color: theme.colors.text }}>v{v.version}</span>
                  <span style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.textTertiary, marginLeft: theme.spacing[2] }}>{formatDate(v.created_at)}</span>
                </div>
                {v.version !== template.version && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRestore(v)}
                    loading={restoring === v.id}
                    disabled={restoring !== null}
                  >
                    Restore
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Modal>
  )
}
