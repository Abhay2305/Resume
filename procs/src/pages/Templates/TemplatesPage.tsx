import { useState, useEffect } from 'react'
import { Search, Plus, Eye, Edit3, Copy, Trash2, ArrowUpCircle, ArrowDownCircle, FileText } from 'lucide-react'
import { theme } from '../../styles/theme'
import DataTable from '../../components/shared/DataTable'
import Button from '../../components/shared/Button'
import Modal from '../../components/shared/Modal'
import StatusBadge from '../../components/shared/StatusBadge'
import { useTemplatesCms } from './hooks/useTemplatesCms'
import {
  publishTemplate,
  archiveTemplate,
  deleteTemplate,
  duplicateTemplate,
} from '../../services/api/templateCms.service'
import TemplateFormModal from './components/TemplateFormModal'
import TemplateViewModal from './components/TemplateViewModal'
import { ActionMenu, EmptyState } from '../../components/shared'
import type { ActionMenuItem } from '../../components/shared'
import type { TemplateCmsItem } from './types'

const FileTextIcon = FileText as React.ComponentType<{ size?: number; color?: string }>

const CATEGORIES = ['', 'ATS', 'Corporate', 'Technology', 'Creative']
const STATUSES = ['', 'draft', 'published', 'archived', 'deprecated']

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

function statusBadgeVariant(status: string): 'success' | 'warning' | 'danger' | 'neutral' {
  switch (status) {
    case 'published': return 'success'
    case 'draft': return 'warning'
    case 'deprecated': return 'danger'
    default: return 'neutral'
  }
}

export default function TemplatesPage() {
  const { templates, total, loading, error, filters, searchInput, setSearchInput, setFilters, refresh } = useTemplatesCms()
  const [actionError, setActionError] = useState<string | null>(null)

  const [showFormModal, setShowFormModal] = useState(false)
  const [editTemplate, setEditTemplate] = useState<TemplateCmsItem | null>(null)
  const [viewTemplate, setViewTemplate] = useState<TemplateCmsItem | null>(null)
  const [showDeleteModal, setShowDeleteModal] = useState<TemplateCmsItem | null>(null)
  const [showDuplicateModal, setShowDuplicateModal] = useState<TemplateCmsItem | null>(null)
  const [duplicateName, setDuplicateName] = useState('')
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const handlePublish = async (id: string) => {
    try {
      setActionError(null)
      setActionLoading(id)
      await publishTemplate(id)
      refresh()
    } catch {
      setActionError('Failed to publish template')
    } finally {
      setActionLoading(null)
    }
  }

  const handleArchive = async (id: string) => {
    try {
      setActionError(null)
      setActionLoading(id)
      await archiveTemplate(id)
      refresh()
    } catch {
      setActionError('Failed to archive template')
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async () => {
    if (!showDeleteModal) return
    try {
      setActionError(null)
      setActionLoading(showDeleteModal.id)
      await deleteTemplate(showDeleteModal.id)
      setShowDeleteModal(null)
      refresh()
    } catch {
      setActionError('Failed to delete template')
    } finally {
      setActionLoading(null)
    }
  }

  const handleDuplicate = async () => {
    if (!showDuplicateModal || !duplicateName) return
    try {
      setActionError(null)
      setActionLoading(showDuplicateModal.id)
      await duplicateTemplate(showDuplicateModal.id, {
        new_id: duplicateName.toLowerCase().replace(/\s+/g, '-'),
        new_name: duplicateName,
      })
      setShowDuplicateModal(null)
      setDuplicateName('')
      refresh()
    } catch {
      setActionError('Failed to duplicate template')
    } finally {
      setActionLoading(null)
    }
  }

  const handleCreate = () => {
    setEditTemplate(null)
    setShowFormModal(true)
  }

  const handleEdit = (template: TemplateCmsItem) => {
    setEditTemplate(template)
    setShowFormModal(true)
  }

  const getRowActions = (t: TemplateCmsItem): ActionMenuItem[] => [
    {
      key: 'view',
      label: 'View',
      icon: <Eye size={14} />,
      onClick: () => setViewTemplate(t),
    },
    {
      key: 'edit',
      label: 'Edit',
      icon: <Edit3 size={14} />,
      onClick: () => handleEdit(t),
    },
    {
      key: 'duplicate',
      label: 'Duplicate',
      icon: <Copy size={14} />,
      onClick: () => {
        setShowDuplicateModal(t)
        setDuplicateName(`${t.name} (Copy)`)
      },
    },
    {
      key: 'publish',
      label: 'Publish',
      icon: <ArrowUpCircle size={14} />,
      onClick: () => handlePublish(t.id),
      divider: true,
    },
    {
      key: 'archive',
      label: 'Unpublish',
      icon: <ArrowDownCircle size={14} />,
      onClick: () => handleArchive(t.id),
      divider: true,
    },
    {
      key: 'delete',
      label: 'Delete',
      icon: <Trash2 size={14} />,
      onClick: () => setShowDeleteModal(t),
      variant: 'danger',
      divider: true,
    },
  ]

  const columns = [
    {
      key: 'thumbnail_url',
      label: '',
      width: '48px',
      render: (_: unknown, row: Record<string, unknown>) => {
        const t = row as unknown as TemplateCmsItem
        return (
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: theme.borderRadius.sm,
              background: t.thumbnail_url
                ? `url(${t.thumbnail_url}) center/cover`
                : `linear-gradient(135deg, ${t.color_scheme?.primary || '#7BC4BE'} 0%, ${t.color_scheme?.secondary || '#F6B233'} 100%)`,
              border: `1px solid ${theme.colors.border}`,
              flexShrink: 0,
            }}
          />
        )
      },
    },
    {
      key: 'name',
      label: 'Name',
      sortable: true,
      render: (value: unknown, row: Record<string, unknown>) => (
        <div style={{ minWidth: 0 }}>
          <div
            style={{
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.text,
              fontSize: theme.typography.sizes.body,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              maxWidth: '200px',
            }}
            title={String(value)}
          >
            {String(value)}
          </div>
          <div
            style={{
              fontSize: theme.typography.sizes.caption,
              color: theme.colors.textTertiary,
              fontFamily: 'monospace',
              whiteSpace: 'nowrap',
            }}
          >
            {String(row.id)}
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      label: 'Category',
      sortable: true,
      width: '120px',
      render: (value: unknown) => (
        <span
          style={{
            display: 'inline-block',
            padding: '2px 8px',
            fontSize: theme.typography.sizes.caption,
            fontWeight: theme.typography.weights.medium,
            color: theme.colors.textSecondary,
            backgroundColor: theme.colors.neutralBg,
            borderRadius: theme.borderRadius.sm,
            border: `1px solid ${theme.colors.border}`,
          }}
        >
          {String(value || '—')}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      width: '110px',
      render: (value: unknown) => (
        <StatusBadge
          status={statusBadgeVariant(String(value))}
          label={String(value)}
          variant="badge"
          size="sm"
        />
      ),
    },
    {
      key: 'version',
      label: 'Version',
      width: '80px',
      align: 'center' as const,
      render: (value: unknown) => (
        <span
          style={{
            fontVariantNumeric: 'tabular-nums',
            fontSize: theme.typography.sizes.bodySmall,
            color: theme.colors.textSecondary,
            fontWeight: theme.typography.weights.medium,
          }}
        >
          v{String(value)}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Created',
      sortable: true,
      width: '120px',
      render: (value: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary }}>
          {formatDate(String(value))}
        </span>
      ),
    },
    {
      key: 'updated_at',
      label: 'Updated',
      sortable: true,
      width: '120px',
      render: (value: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary }}>
          {formatDate(String(value))}
        </span>
      ),
    },
    {
      key: 'actions',
      label: '',
      width: '48px',
      align: 'center' as const,
      render: (_: unknown, row: Record<string, unknown>) => {
        const t = row as unknown as TemplateCmsItem
        const allActions = getRowActions(t)
        const filteredActions = allActions.filter((a) => {
          if (a.key === 'publish') return t.status !== 'published'
          if (a.key === 'archive') return t.status === 'published'
          return true
        })
        return <ActionMenu items={filteredActions} />
      },
    },
  ]

  const hasActiveFilters = searchInput !== '' || filters.category !== null || filters.status !== null
  const emptyTitle = hasActiveFilters ? 'No templates match your filters' : 'No templates found'
  const emptyDescription = hasActiveFilters
    ? 'Try adjusting your search or filter criteria.'
    : 'Create your first template to get started.'

  return (
    <div style={{ padding: theme.layout.pagePadding, fontFamily: theme.typography.fontFamily }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          flexDirection: isMobile ? 'column' : 'row',
          justifyContent: 'space-between',
          alignItems: isMobile ? 'stretch' : 'flex-start',
          gap: isMobile ? theme.spacing[3] : 0,
          marginBottom: theme.spacing[6],
        }}
      >
        <div>
          <h1
            style={{
              margin: 0,
              fontSize: theme.typography.sizes.h1,
              fontWeight: theme.typography.weights.bold,
              color: theme.colors.text,
              letterSpacing: '-0.02em',
            }}
          >
            Templates
          </h1>
          <p
            style={{
              margin: 0,
              marginTop: theme.spacing[1],
              fontSize: theme.typography.sizes.bodySmall,
              color: theme.colors.textSecondary,
            }}
          >
            Manage resume templates. Published templates appear automatically in Prompt Resume.
          </p>
        </div>
        <Button variant="primary" onClick={handleCreate} icon={<Plus size={16} />} aria-label="Create Template" fullWidth={isMobile}>
          Create Template
        </Button>
      </div>

      {/* Error Messages */}
      {actionError && (
        <div
          style={{
            marginBottom: theme.spacing[4],
            padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
            backgroundColor: theme.colors.dangerBg,
            border: `1px solid ${theme.colors.danger}30`,
            borderRadius: theme.borderRadius.md,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <span style={{ color: theme.colors.danger, fontSize: theme.typography.sizes.bodySmall }}>{actionError}</span>
          <button
            onClick={() => setActionError(null)}
            style={{
              background: 'none',
              border: 'none',
              color: theme.colors.danger,
              cursor: 'pointer',
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
            }}
          >
            Dismiss
          </button>
        </div>
      )}

      {error && (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            marginBottom: theme.spacing[4],
            padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
            backgroundColor: theme.colors.dangerBg,
            border: `1px solid ${theme.colors.danger}30`,
            borderRadius: theme.borderRadius.md,
          }}
        >
          <span style={{ color: theme.colors.danger, fontSize: theme.typography.sizes.bodySmall }}>{error}</span>
        </div>
      )}

      {/* Filters */}
      <div
        style={{
          display: 'flex',
          gap: theme.spacing[3],
          marginBottom: theme.spacing[5],
          flexWrap: 'wrap',
          alignItems: 'center',
        }}
      >
        <div style={{ position: 'relative', flex: 1, minWidth: isMobile ? '100%' : '200px', maxWidth: isMobile ? '100%' : '320px' }}>
          <Search
            size={16}
            color={theme.colors.textTertiary}
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              pointerEvents: 'none',
            }}
          />
          <input
            type="text"
            placeholder="Search templates..."
            aria-label="Search templates"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            style={{
              width: '100%',
              height: '36px',
              padding: `${theme.spacing[2]} ${theme.spacing[3]} ${theme.spacing[2]} 36px`,
              fontSize: theme.typography.sizes.body,
              fontFamily: theme.typography.fontFamily,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              backgroundColor: theme.colors.surface,
              color: theme.colors.text,
              outline: 'none',
              boxSizing: 'border-box',
              transition: `border-color ${theme.transitions.fast}`,
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = theme.colors.primary
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = theme.colors.border
            }}
          />
        </div>
        <select
          value={filters.category || ''}
          aria-label="Filter by category"
          onChange={(e) => setFilters({ category: e.target.value || null })}
          style={{
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            fontFamily: theme.typography.fontFamily,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.sm,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            outline: 'none',
            cursor: 'pointer',
            height: '36px',
            minWidth: '140px',
          }}
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c || 'All Categories'}</option>
          ))}
        </select>
        <select
          value={filters.status || ''}
          aria-label="Filter by status"
          onChange={(e) => setFilters({ status: e.target.value || null })}
          style={{
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            fontFamily: theme.typography.fontFamily,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.sm,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            outline: 'none',
            cursor: 'pointer',
            height: '36px',
            minWidth: '140px',
          }}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s || 'All Statuses'}</option>
          ))}
        </select>
      </div>

      {/* Data Table or Empty State */}
      {!loading && !error && templates.length === 0 ? (
        <div role="status" aria-live="polite" style={{ border: `1px solid ${theme.colors.border}`, borderRadius: theme.borderRadius.md }}>
          <EmptyState
            icon={FileTextIcon}
            title={emptyTitle}
            description={emptyDescription}
            action={!hasActiveFilters ? { label: 'Create Template', onClick: handleCreate } : undefined}
          />
        </div>
      ) : (
        <DataTable
          columns={columns}
          data={templates as unknown as Record<string, unknown>[]}
          loading={loading}
          error={error}
          errorRetry={refresh}
          empty={emptyTitle}
          emptyIcon={FileTextIcon}
          sortable
          pagination={{
            page: filters.page,
            perPage: filters.limit,
            total,
            perPageOptions: [10, 20, 50],
            onPageChange: (p) => setFilters({ page: p }),
            onPerPageChange: (limit) => setFilters({ limit, page: 1 }),
          }}
        />
      )}

      {/* Create / Edit Modal */}
      <TemplateFormModal
        open={showFormModal}
        onClose={() => { setShowFormModal(false); setEditTemplate(null) }}
        onSaved={() => { setShowFormModal(false); setEditTemplate(null); refresh() }}
        template={editTemplate}
      />

      {/* View Modal */}
      <TemplateViewModal
        open={!!viewTemplate}
        onClose={() => setViewTemplate(null)}
        template={viewTemplate}
        onRefresh={refresh}
      />

      {/* Delete Modal */}
      <Modal
        open={!!showDeleteModal}
        onClose={() => setShowDeleteModal(null)}
        title="Delete Template"
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowDeleteModal(null)}>Cancel</Button>
            <Button variant="danger" onClick={handleDelete} loading={actionLoading === showDeleteModal?.id}>Delete</Button>
          </>
        }
      >
        <p style={{ margin: 0, fontSize: theme.typography.sizes.body, color: theme.colors.textSecondary }}>
          Are you sure you want to delete <strong style={{ color: theme.colors.text }}>{showDeleteModal?.name}</strong>? This action cannot be undone.
        </p>
      </Modal>

      {/* Duplicate Modal */}
      <Modal
        open={!!showDuplicateModal}
        onClose={() => setShowDuplicateModal(null)}
        title="Duplicate Template"
        description={`Create a copy of "${showDuplicateModal?.name}"`}
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowDuplicateModal(null)}>Cancel</Button>
            <Button variant="primary" onClick={handleDuplicate} disabled={!duplicateName.trim()} loading={actionLoading === showDuplicateModal?.id}>Duplicate</Button>
          </>
        }
      >
        <div>
          <label
            style={{
              display: 'block',
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.textSecondary,
              marginBottom: theme.spacing[2],
            }}
          >
            New Template Name
          </label>
          <input
            type="text"
            value={duplicateName}
            onChange={(e) => setDuplicateName(e.target.value)}
            style={{
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
            }}
          />
        </div>
      </Modal>
    </div>
  )
}
