import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Pencil, Trash2 } from 'lucide-react'
import InspectorPanel from '../../components/shared/InspectorPanel'
import StatusBadge from '../../components/shared/StatusBadge'
import Tabs from '../../components/shared/Tabs'
import Skeleton from '../../components/shared/Skeleton'
import Alert from '../../components/shared/Alert'
import Button from '../../components/shared/Button'
import { theme } from '../../styles/theme'
import { useResumeInspector } from './hooks/useResumeInspector'
import ResumeOverviewTab from './components/ResumeOverviewTab'
import ResumeSectionsTab from './components/ResumeSectionsTab'
import ResumeVersionsTab from './components/ResumeVersionsTab'
import EditResumeModal from './components/EditResumeModal'
import DeleteResumeModal from './components/DeleteResumeModal'

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export default function ResumeInspector() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { resume, loading, error, updateResume, deleteResume } = useResumeInspector(id || '')
  const [activeTab, setActiveTab] = useState('overview')
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'sections', label: 'Sections' },
    { key: 'versions', label: 'Versions' },
  ]

  if (loading) {
    return (
      <div style={{ padding: theme.layout.pagePadding }}>
        <div style={{ marginBottom: theme.spacing[4] }}>
          <Skeleton variant="text" width="200px" height="14px" />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[4], marginBottom: theme.spacing[6] }}>
          <Skeleton variant="avatar" width={64} height={64} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[2] }}>
            <Skeleton variant="heading" width="200px" />
            <Skeleton variant="text" width="300px" />
          </div>
        </div>
        <Skeleton variant="text" width="100%" height="40px" />
        <div style={{ marginTop: theme.spacing[4], display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} variant="card" height="120px" />
          ))}
        </div>
      </div>
    )
  }

  if (error || !resume) {
    return (
      <div style={{ padding: theme.layout.pagePadding }}>
        <nav
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[2],
            marginBottom: theme.spacing[4],
            fontSize: theme.typography.sizes.bodySmall,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          <button
            onClick={() => navigate('/resumes')}
            style={{
              background: 'none',
              border: 'none',
              padding: 0,
              color: theme.colors.primary,
              cursor: 'pointer',
              fontSize: 'inherit',
              fontFamily: 'inherit',
            }}
          >
            Resumes
          </button>
        </nav>
        <Alert variant="error" title="Resume not found" action={{ label: 'Back to Resumes', onClick: () => navigate('/resumes') }}>
          {error || 'The requested resume could not be found.'}
        </Alert>
      </div>
    )
  }

  return (
    <div>
      <InspectorPanel
        title={resume.title}
        subtitle={resume.user_email}
        breadcrumbs={[
          { label: 'Resumes', href: '/resumes' },
          { label: resume.title },
        ]}
        headerRight={
          <div style={{ display: 'flex', gap: theme.spacing[2] }}>
            <Button variant="secondary" size="sm" onClick={() => setShowEditModal(true)}>
              <Pencil size={14} style={{ marginRight: theme.spacing[1] }} />
              Edit
            </Button>
            <Button variant="danger" size="sm" onClick={() => setShowDeleteModal(true)}>
              <Trash2 size={14} style={{ marginRight: theme.spacing[1] }} />
              Delete
            </Button>
          </div>
        }
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[3],
            marginBottom: theme.spacing[4],
            flexWrap: 'wrap',
          }}
        >
          <StatusBadge
            status={resume.status === 'published' ? 'success' : 'warning'}
            label={resume.status === 'published' ? 'Published' : 'Draft'}
          />
          <span
            style={{
              fontSize: theme.typography.sizes.bodySmall,
              color: theme.colors.textSecondary,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            Template: {resume.template_name}
          </span>
          <span
            style={{
              fontSize: theme.typography.sizes.caption,
              color: theme.colors.textTertiary,
              fontFamily: theme.typography.fontFamily,
              marginLeft: 'auto',
            }}
          >
            Created {formatDate(resume.created_at)}
          </span>
        </div>

        <Tabs tabs={tabs} activeKey={activeTab} onChange={setActiveTab} />

        <div style={{ marginTop: theme.spacing[4] }}>
          {activeTab === 'overview' && <ResumeOverviewTab resume={resume} />}
          {activeTab === 'sections' && <ResumeSectionsTab sections={resume.sections || []} />}
          {activeTab === 'versions' && <ResumeVersionsTab versions={resume.versions || []} />}
        </div>
      </InspectorPanel>

      <EditResumeModal
        open={showEditModal}
        onClose={() => setShowEditModal(false)}
        resume={resume}
        onSave={updateResume}
      />

      <DeleteResumeModal
        open={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        resumeTitle={resume.title}
        onDelete={async () => {
          await deleteResume()
          navigate('/resumes')
        }}
      />
    </div>
  )
}
