import DataTable from '../../../components/shared/DataTable'
import StatusBadge from '../../../components/shared/StatusBadge'
import Alert from '../../../components/shared/Alert'
import Pagination from '../../../components/shared/Pagination'
import { theme } from '../../../styles/theme'
import { useUserResumes } from '../hooks/useUserResumes'

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

interface ResumesTabProps {
  userId: string
}

export default function ResumesTab({ userId }: ResumesTabProps) {
  const { resumes, total, page, loading, error, setPage, refresh } = useUserResumes(userId)

  const columns = [
    {
      key: 'title',
      label: 'Title',
      render: (value: unknown) => (
        <span style={{ fontWeight: theme.typography.weights.medium, color: theme.colors.text }}>
          {String(value)}
        </span>
      ),
    },
    {
      key: 'template_name',
      label: 'Template',
      render: (value: unknown) => (
        <span style={{ color: theme.colors.textSecondary }}>{String(value || '—')}</span>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value: unknown) => {
        const status = value as 'draft' | 'published'
        return (
          <StatusBadge
            status={status === 'published' ? 'success' : 'warning'}
            label={status.charAt(0).toUpperCase() + status.slice(1)}
            variant="dot"
          />
        )
      },
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (value: unknown) => formatDate(String(value)),
    },
    {
      key: 'updated_at',
      label: 'Updated',
      render: (value: unknown) => formatDate(String(value)),
    },
  ]

  if (error) {
    return (
      <Alert variant="error" title="Error loading resumes" action={{ label: 'Retry', onClick: refresh }}>
        {error}
      </Alert>
    )
  }

  return (
    <div>
      <DataTable
        columns={columns}
        data={resumes as unknown as Record<string, unknown>[]}
        loading={loading}
        empty="No resumes found for this user"
      />
      {total > 10 && (
        <div style={{ marginTop: theme.spacing[3] }}>
          <Pagination
            page={page}
            perPage={10}
            total={total}
            onPageChange={setPage}
          />
        </div>
      )}
    </div>
  )
}
