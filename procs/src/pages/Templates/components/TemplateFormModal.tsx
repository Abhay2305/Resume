import { useState, useRef, useEffect } from 'react'
import { Upload, X, Loader2 } from 'lucide-react'
import { theme } from '../../../styles/theme'
import Modal from '../../../components/shared/Modal'
import Button from '../../../components/shared/Button'
import {
  createTemplate,
  updateTemplate,
  uploadTemplateFile,
} from '../../../services/api/templateCms.service'
import type { TemplateCmsItem, TemplateFormData } from '../types'

interface TemplateFormModalProps {
  open: boolean
  onClose: () => void
  onSaved: () => void
  template?: TemplateCmsItem | null
}

const CATEGORIES = ['ATS', 'Corporate', 'Technology', 'Creative']
const STATUSES = ['draft', 'published', 'archived']
const LAYOUTS = ['single-column', 'two-column-left', 'two-column-right']
const HEADER_STYLES = ['left', 'center', 'banner']
const FONTS = ['Inter', 'Roboto', 'Open Sans', 'Lato', 'Montserrat', 'Source Sans Pro', 'Nunito', 'Poppins']
const DEFAULT_SECTIONS = ['header', 'summary', 'experience', 'education', 'skills', 'projects']

function getDefaultForm(): TemplateFormData {
  return {
    name: '',
    slug: '',
    description: '',
    category: 'ATS',
    status: 'draft',
    layout: 'single-column',
    headerStyle: 'left',
    fontFamily: 'Inter',
    primaryColor: '#7BC4BE',
    secondaryColor: '#F6B233',
    accentColor: '#3B82F6',
    backgroundColor: '#FFFFFF',
    textColor: '#0F172A',
    margins: 'normal',
    sectionOrder: [...DEFAULT_SECTIONS],
    sidebarSections: [],
  }
}

function buildDefinitionFromForm(form: TemplateFormData): Record<string, unknown> {
  return {
    layout: {
      structure: form.layout,
      headerStyle: form.headerStyle,
      margins: form.margins,
    },
    colors: {
      primary: form.primaryColor,
      secondary: form.secondaryColor,
      accent: form.accentColor,
      background: form.backgroundColor,
      text: form.textColor,
    },
    font: {
      heading: form.fontFamily,
      body: form.fontFamily,
    },
    sections: {
      order: form.sectionOrder,
      sidebar: form.sidebarSections,
    },
  }
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 12px',
  fontSize: theme.typography.sizes.body,
  fontFamily: theme.typography.fontFamily,
  border: `1px solid ${theme.colors.border}`,
  borderRadius: theme.borderRadius.md,
  backgroundColor: theme.colors.surface,
  color: theme.colors.text,
  outline: 'none',
  boxSizing: 'border-box',
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: theme.typography.sizes.bodySmall,
  fontWeight: theme.typography.weights.medium,
  color: theme.colors.textSecondary,
  marginBottom: theme.spacing[1],
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

export default function TemplateFormModal({ open, onClose, onSaved, template }: TemplateFormModalProps) {
  const isEdit = !!template
  const [form, setForm] = useState<TemplateFormData>(getDefaultForm)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [thumbFile, setThumbFile] = useState<File | null>(null)
  const [thumbPreview, setThumbPreview] = useState<string | null>(null)
  const [previewFiles, setPreviewFiles] = useState<File[]>([])
  const [previewPreviews, setPreviewPreviews] = useState<string[]>([])
  const thumbInputRef = useRef<HTMLInputElement>(null)
  const previewInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!open) {
      setForm(getDefaultForm())
      setThumbFile(null)
      setThumbPreview(null)
      setPreviewFiles([])
      setPreviewPreviews([])
      setError(null)
      return
    }
    if (template) {
      setForm({
        name: template.name,
        slug: template.slug || template.id,
        description: template.description || '',
        category: template.category,
        status: template.status === 'deprecated' ? 'draft' : template.status,
        layout: ((template.layout_schema?.structure as string) || 'single-column') as TemplateFormData['layout'],
        headerStyle: ((template.layout_schema?.headerStyle as string) || 'left') as TemplateFormData['headerStyle'],
        fontFamily: template.fonts?.heading || 'Inter',
        primaryColor: template.color_scheme?.primary || '#7BC4BE',
        secondaryColor: template.color_scheme?.secondary || '#F6B233',
        accentColor: template.colors?.accent || '#3B82F6',
        backgroundColor: template.colors?.background || '#FFFFFF',
        textColor: template.colors?.text || '#0F172A',
        margins: (template.template_definition as Record<string, unknown>)?.layout
          ? ((template.template_definition as Record<string, unknown>).layout as Record<string, string>).margins || 'normal'
          : 'normal',
        sectionOrder: template.template_definition
          ? ((template.template_definition as Record<string, unknown>).sections as Record<string, string[]>)?.order || [...DEFAULT_SECTIONS]
          : [...DEFAULT_SECTIONS],
        sidebarSections: template.template_definition
          ? ((template.template_definition as Record<string, unknown>).sections as Record<string, string[]>)?.sidebar || []
          : [],
      })
      if (template.thumbnail_url) setThumbPreview(template.thumbnail_url)
      if (template.preview_images) setPreviewPreviews(template.preview_images)
    } else {
      setForm(getDefaultForm())
    }
  }, [open, template])

  const handleThumbChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setThumbFile(file)
    const reader = new FileReader()
    reader.onload = (ev) => setThumbPreview(ev.target?.result as string)
    reader.readAsDataURL(file)
  }

  const handlePreviewChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return
    setPreviewFiles((prev) => [...prev, ...files])
    files.forEach((file) => {
      const reader = new FileReader()
      reader.onload = (ev) => setPreviewPreviews((prev) => [...prev, ev.target?.result as string])
      reader.readAsDataURL(file)
    })
  }

  const removePreviewImage = (index: number) => {
    setPreviewPreviews((prev) => prev.filter((_, i) => i !== index))
    setPreviewFiles((prev) => {
      const newFiles = [...prev]
      newFiles.splice(index, 1)
      return newFiles
    })
  }

  const handleSave = async () => {
    if (!form.name.trim()) {
      setError('Template name is required')
      return
    }
    if (!form.slug.trim()) {
      setError('Slug is required')
      return
    }

    setSaving(true)
    setError(null)

    try {
      const definition = buildDefinitionFromForm(form)
      const colorScheme = {
        primary: form.primaryColor,
        secondary: form.secondaryColor,
      }
      const layoutSchema = {
        structure: form.layout,
        headerStyle: form.headerStyle,
        fontFamily: form.fontFamily,
      }
      const colors = {
        accent: form.accentColor,
        background: form.backgroundColor,
        text: form.textColor,
      }

      let templateId: string

      if (isEdit && template) {
        await updateTemplate(template.id, {
          name: form.name,
          slug: form.slug,
          description: form.description || null,
          category: form.category,
          status: form.status,
          color_scheme: colorScheme,
          layout_schema: layoutSchema,
          colors,
          template_definition: definition,
          fonts: { heading: form.fontFamily, body: form.fontFamily },
        })
        templateId = template.id
      } else {
        const res = await createTemplate({
          id: form.slug,
          name: form.name,
          slug: form.slug,
          description: form.description || null,
          category: form.category,
          status: form.status,
          color_scheme: colorScheme,
          layout_schema: layoutSchema,
          colors,
          template_definition: definition,
          fonts: { heading: form.fontFamily, body: form.fontFamily },
        }) as { data?: { id?: string } }
        templateId = res?.data?.id || form.slug
      }

      if (thumbFile) {
        await uploadTemplateFile(templateId, 'thumbnail', thumbFile)
      }

      for (const file of previewFiles) {
        await uploadTemplateFile(templateId, 'preview', file)
      }

      onSaved()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save template')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Edit Template' : 'Create Template'}
      description={isEdit ? `Editing "${template?.name}"` : 'Create a new resume template'}
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button>
          <Button variant="primary" onClick={handleSave} loading={saving} icon={saving ? <Loader2 size={14} className="animate-spin" /> : undefined}>
            {isEdit ? 'Save Changes' : 'Create Template'}
          </Button>
        </>
      }
    >
      {error && (
        <div style={{ marginBottom: theme.spacing[4], padding: `${theme.spacing[3]} ${theme.spacing[4]}`, backgroundColor: theme.colors.dangerBg, border: `1px solid ${theme.colors.danger}30`, borderRadius: theme.borderRadius.md, color: theme.colors.danger, fontSize: theme.typography.sizes.bodySmall }}>
          {error}
        </div>
      )}

      {/* Basic Information */}
      <div style={{ marginBottom: theme.spacing[6] }}>
        <div style={sectionHeaderStyle}>Basic Information</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <label style={labelStyle}>Template Name *</label>
            <input style={inputStyle} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value, slug: e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') })} placeholder="e.g. Modern Blue" />
          </div>
          <div>
            <label style={labelStyle}>Slug *</label>
            <input style={inputStyle} value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} placeholder="e.g. modern-blue" />
          </div>
          <div>
            <label style={labelStyle}>Category</label>
            <select style={inputStyle} value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Status</label>
            <select style={inputStyle} value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as TemplateFormData['status'] })}>
              {STATUSES.map((s) => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
            </select>
          </div>
        </div>
        <div style={{ marginTop: theme.spacing[4] }}>
          <label style={labelStyle}>Description</label>
          <textarea style={{ ...inputStyle, minHeight: '60px', resize: 'vertical' }} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Brief description of the template" />
        </div>
      </div>

      {/* Assets */}
      <div style={{ marginBottom: theme.spacing[6] }}>
        <div style={sectionHeaderStyle}>Assets</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <label style={labelStyle}>Thumbnail</label>
            <input ref={thumbInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleThumbChange} />
            <div
              onClick={() => thumbInputRef.current?.click()}
              style={{
                width: '100%', height: '120px', border: `2px dashed ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md, display: 'flex', alignItems: 'center',
                justifyContent: 'center', cursor: 'pointer', overflow: 'hidden',
                backgroundColor: theme.colors.surfaceHover,
              }}
            >
              {thumbPreview ? (
                <img src={thumbPreview} alt="Thumbnail" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                <div style={{ textAlign: 'center', color: theme.colors.textTertiary }}>
                  <Upload size={24} style={{ margin: '0 auto 4px' }} />
                  <div style={{ fontSize: theme.typography.sizes.caption }}>Click to upload</div>
                </div>
              )}
            </div>
          </div>
          <div>
            <label style={labelStyle}>Preview Images</label>
            <input ref={previewInputRef} type="file" accept="image/*" multiple style={{ display: 'none' }} onChange={handlePreviewChange} />
            <div
              onClick={() => previewInputRef.current?.click()}
              style={{
                width: '100%', height: '120px', border: `2px dashed ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md, display: 'flex', alignItems: 'center',
                justifyContent: 'center', cursor: 'pointer', overflow: 'hidden',
                backgroundColor: theme.colors.surfaceHover,
              }}
            >
              {previewPreviews.length > 0 ? (
                <div style={{ display: 'flex', gap: '4px', padding: '4px', overflow: 'auto', width: '100%', height: '100%' }}>
                  {previewPreviews.map((src, i) => (
                    <div key={i} style={{ position: 'relative', flexShrink: 0, width: '80px', height: '100%' }}>
                      <img src={src} alt={`Preview ${i + 1}`} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: theme.borderRadius.sm }} />
                      <button
                        onClick={(e) => { e.stopPropagation(); removePreviewImage(i) }}
                        style={{ position: 'absolute', top: '2px', right: '2px', width: '16px', height: '16px', borderRadius: '50%', backgroundColor: theme.colors.danger, color: '#fff', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0 }}
                      >
                        <X size={10} />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: theme.colors.textTertiary }}>
                  <Upload size={24} style={{ margin: '0 auto 4px' }} />
                  <div style={{ fontSize: theme.typography.sizes.caption }}>Click to upload</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Layout */}
      <div style={{ marginBottom: theme.spacing[6] }}>
        <div style={sectionHeaderStyle}>Layout</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <label style={labelStyle}>Layout</label>
            <select style={inputStyle} value={form.layout} onChange={(e) => setForm({ ...form, layout: e.target.value as TemplateFormData['layout'] })}>
              {LAYOUTS.map((l) => <option key={l} value={l}>{l.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Header Style</label>
            <select style={inputStyle} value={form.headerStyle} onChange={(e) => setForm({ ...form, headerStyle: e.target.value as TemplateFormData['headerStyle'] })}>
              {HEADER_STYLES.map((h) => <option key={h} value={h}>{h.charAt(0).toUpperCase() + h.slice(1)}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Font</label>
            <select style={inputStyle} value={form.fontFamily} onChange={(e) => setForm({ ...form, fontFamily: e.target.value })}>
              {FONTS.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Colors */}
      <div style={{ marginBottom: theme.spacing[6] }}>
        <div style={sectionHeaderStyle}>Colors</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: theme.spacing[4] }}>
          {([
            ['primaryColor', 'Primary'],
            ['secondaryColor', 'Secondary'],
            ['accentColor', 'Accent'],
            ['backgroundColor', 'Background'],
            ['textColor', 'Text'],
          ] as const).map(([key, label]) => (
            <div key={key}>
              <label style={labelStyle}>{label}</label>
              <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                <input
                  type="color"
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  style={{ width: '32px', height: '32px', padding: 0, border: `1px solid ${theme.colors.border}`, borderRadius: theme.borderRadius.sm, cursor: 'pointer' }}
                />
                <input
                  type="text"
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  style={{ ...inputStyle, flex: 1 }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Spacing & Sections */}
      <div style={{ marginBottom: theme.spacing[6] }}>
        <div style={sectionHeaderStyle}>Spacing & Sections</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <label style={labelStyle}>Margins</label>
            <select style={inputStyle} value={form.margins} onChange={(e) => setForm({ ...form, margins: e.target.value })}>
              <option value="compact">Compact</option>
              <option value="normal">Normal</option>
              <option value="wide">Wide</option>
            </select>
          </div>
          <div>
            <label style={labelStyle}>Section Order (comma-separated)</label>
            <input
              style={inputStyle}
              value={form.sectionOrder.join(', ')}
              onChange={(e) => setForm({ ...form, sectionOrder: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) })}
              placeholder="header, summary, experience, education, skills"
            />
          </div>
        </div>
        <div style={{ marginTop: theme.spacing[4] }}>
          <label style={labelStyle}>Sidebar Sections (comma-separated)</label>
          <input
            style={inputStyle}
            value={form.sidebarSections.join(', ')}
            onChange={(e) => setForm({ ...form, sidebarSections: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) })}
            placeholder="e.g. skills, languages"
          />
        </div>
      </div>
    </Modal>
  )
}
