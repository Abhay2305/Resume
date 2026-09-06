import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import DataTable from '../../components/shared/DataTable'
import StatusBadge from '../../components/shared/StatusBadge'
import { theme } from '../../styles/theme'
import { useResumeList } from './hooks/useResumeList'
import { getResumeStats, getTemplates } from '../../services/api/resume.service'
import ResumeStatsCards from './components/ResumeStatsCards'
import type { ResumeListItem, ResumeStats, TemplateListItem } from './types'

function formatRelativeTime(dateStr: string | null): string {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`
  return date.toLocaleDateString()
}

export default function ResumeList() {
  const navigate = useNavigate()
  const { resumes, total, loading, error, filters, searchInput, setSearchInput, setFilters, refresh } = useResumeList()
  const [stats, setStats] = useState<ResumeStats | null>(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [templates, setTemplates] = useState<TemplateListItem[]>([])

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await getResumeStats() as { data?: ResumeStats }
        setStats(response.data || null)
      } catch {
        // Stats load failure is non-critical
      } finally {
        setStatsLoading(false)
      }
    }
    fetchStats()
  }, [])

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await getTemplates() as { data?: { items?: TemplateListItem[] } }
        setTemplates(response.data?.items || [])
      } catch {
        // Templates load failure is non-critical
      }
    }
    fetchTemplates()
  }, [])

  const columns = [
    {
      key: 'id',
      label: 'ID',
      width: '80px',
      render: (value: unknown) => (
        <span style={{ fontFamily: 'monospace', fontSize: theme.typography.sizes.caption, color: theme.colors.textTertiary }}>
          {String(value).slice(0, 8)}
        </span>
      ),
    },
    {
      key: 'title',
      label: 'Title',
      sortable: true,
      render: (value: unknown) => (
        <span style={{ fontWeight: theme.typography.weights.medium, color: theme.colors.text }}>
          {String(value || 'Untitled')}
        </span>
      ),
    },
    {
      key: 'user_email',
      label: 'Owner',
      sortable: false,
      render: (value: unknown) => (
        <span style={{ color: value ? theme.colors.text : theme.colors.textTertiary }}>
          {String(value || '—')}
        </span>
      ),
    },
    {
      key: 'template_name',
      label: 'Template',
      sortable: false,
      render: (value: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.bodySmall, color: theme.colors.textSecondary }}>
          {String(value || '—')}
        </span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      width: '100px',
      render: (value: unknown) => {
        const status = value as string
        return (
          <StatusBadge
            status={status === 'published' ? 'success' : 'warning'}
            label={status === 'published' ? 'Published' : 'Draft'}
            variant="dot"
          />
        )
      },
    },
    {
      key: 'created_at',
      label: 'Created',
      sortable: true,
      width: '120px',
      render: (value: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary }}>
          {formatRelativeTime(value as string)}
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
          {formatRelativeTime(value as string)}
        </span>
      ),
    },
  ]

  const handleRowClick = (row: Record<string, unknown>) => {
    const resume = row as unknown as ResumeListItem
    navigate(`/resumes/${resume.id}`)
  }

  const handleSort = (key: string, direction: 'asc' | 'desc') => {
    setFilters({ sort_by: key, sort_order: direction })
  }

  const handlePageChange = (page: number) => {
    setFilters({ page })
  }

  const handlePerPageChange = (perPage: number) => {
    setFilters({ limit: perPage, page: 1 })
  }

  return (
    <div style={{ padding: theme.layout.pagePadding }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: theme.spacing[6],
        }}
      >
        <div>
          <h1
            style={{
              fontSize: theme.typography.sizes.h1,
              fontWeight: theme.typography.weights.bold,
              color: theme.colors.text,
              fontFamily: theme.typography.fontFamily,
              margin: 0,
            }}
          >
            Resumes
          </h1>
          <p
            style={{
              fontSize: theme.typography.sizes.bodySmall,
              color: theme.colors.textSecondary,
              fontFamily: theme.typography.fontFamily,
              margin: 0,
              marginTop: theme.spacing[1],
            }}
          >
            Manage user resumes and their content
          </p>
        </div>
      </div>

      <ResumeStatsCards stats={stats} loading={statsLoading} />

      <div
        style={{
          display: 'flex',
          gap: theme.spacing[3],
          marginBottom: theme.spacing[4],
          flexWrap: 'wrap',
        }}
      >
        <div
          style={{
            position: 'relative',
            flex: '1',
            minWidth: '200px',
            maxWidth: '400px',
          }}
        >
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
            placeholder="Search by title or owner..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            aria-label="Search resumes"
            style={{
              width: '100%',
              padding: `${theme.spacing[2]} ${theme.spacing[3]} ${theme.spacing[2]} '36px'`,
              paddingLeft: '36px',
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

        <select
          value={filters.status || ''}
          onChange={(e) => setFilters({ status: e.target.value || null })}
          aria-label="Filter by status"
          style={{
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
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="published">Published</option>
        </select>

        <select
          value={filters.template || ''}
          onChange={(e) => setFilters({ template: e.target.value || null })}
          aria-label="Filter by template"
          style={{
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
          <option value="">All Templates</option>
          {templates.map((template) => (
            <option key={template.id} value={template.id}>
              {template.name}
            </option>
          ))}
        </select>
      </div>

      <DataTable
        columns={columns}
        data={resumes as unknown as Record<string, unknown>[]}
        loading={loading}
        error={error}
        errorRetry={refresh}
        empty="No resumes found"
        sortable
        onSort={handleSort}
        onRowClick={handleRowClick}
        pagination={{
          page: filters.page,
          perPage: filters.limit,
          total,
          perPageOptions: [10, 20, 50],
          onPageChange: handlePageChange,
          onPerPageChange: handlePerPageChange,
        }}
      />
    </div>
  )
}
