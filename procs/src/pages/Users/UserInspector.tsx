import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Shield, Clock, Mail, Globe, Calendar } from 'lucide-react'
import InspectorPanel from '../../components/shared/InspectorPanel'
import Avatar from '../../components/shared/Avatar'
import StatusBadge from '../../components/shared/StatusBadge'
import Tabs from '../../components/shared/Tabs'
import Skeleton from '../../components/shared/Skeleton'
import Alert from '../../components/shared/Alert'
import Button from '../../components/shared/Button'
import Modal from '../../components/shared/Modal'
import KeyValueList from '../../components/shared/KeyValueList'
import { theme } from '../../styles/theme'
import { useUserInspector } from './hooks/useUserInspector'
import TimelineTab from './components/TimelineTab'
import ResumesTab from './components/ResumesTab'
import SessionsTab from './components/SessionsTab'
import type { UserDetail } from './types'

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

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        backgroundColor: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
          borderBottom: `1px solid ${theme.colors.border}`,
          backgroundColor: theme.colors.surfaceHover,
        }}
      >
        <h3
          style={{
            margin: 0,
            fontSize: theme.typography.sizes.bodySmall,
            fontWeight: theme.typography.weights.semibold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          {title}
        </h3>
      </div>
      <div style={{ padding: theme.spacing[4] }}>{children}</div>
    </div>
  )
}

function OverviewTab({ user }: { user: UserDetail }) {
  const profileItems = [
    { key: 'Job Title', value: user.profile?.job_title },
    { key: 'Phone', value: user.profile?.phone },
    { key: 'Location', value: user.profile?.location },
    { key: 'Company', value: user.profile?.company },
    { key: 'Industry', value: user.profile?.industry },
  ]

  const accountItems = [
    { key: 'Email', value: user.email, icon: <Mail size={14} color={theme.colors.textTertiary} /> },
    { key: 'Timezone', value: user.timezone || 'UTC', icon: <Globe size={14} color={theme.colors.textTertiary} /> },
    { key: 'Language', value: user.language?.toUpperCase() || 'EN' },
    {
      key: 'Last Login',
      value: user.last_login_at
        ? `${formatRelativeTime(user.last_login_at)}${user.last_login_ip ? ` (${user.last_login_ip})` : ''}`
        : '—',
      icon: <Clock size={14} color={theme.colors.textTertiary} />,
    },
    { key: 'Joined', value: formatDate(user.created_at), icon: <Calendar size={14} color={theme.colors.textTertiary} /> },
    { key: 'Updated', value: formatDate(user.updated_at) },
  ]

  const securityItems = [
    {
      key: 'Status',
      value: <StatusBadge status={user.is_active ? 'success' : 'danger'} label={user.is_active ? 'Active' : 'Inactive'} variant="dot" />,
    },
    {
      key: 'Verified',
      value: <StatusBadge status={user.is_verified ? 'success' : 'neutral'} label={user.is_verified ? 'Verified' : 'Unverified'} variant="dot" />,
    },
    {
      key: 'Superuser',
      value: user.is_superuser ? (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: theme.spacing[1], color: theme.colors.warning }}>
          <Shield size={14} /> Yes
        </span>
      ) : (
        'No'
      ),
    },
    { key: 'Failed Logins', value: String(user.failed_login_attempts) },
    { key: 'Locked Until', value: user.locked_until ? formatDateTime(user.locked_until) : '—' },
    { key: 'Password Changed', value: formatDate(user.password_changed_at) },
    { key: 'Email Verified', value: formatDate(user.email_verified_at) },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
      {user.profile && (
        <SectionCard title="Profile">
          <KeyValueList items={profileItems} columns={3} />
        </SectionCard>
      )}

      <SectionCard title="Account Details">
        <KeyValueList items={accountItems} columns={2} />
      </SectionCard>

      <SectionCard title="Security">
        <KeyValueList items={securityItems} columns={2} />
      </SectionCard>

      <SectionCard title="Roles">
        {user.roles.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[2] }}>
            {user.roles.map((role) => (
              <div
                key={role.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: theme.spacing[2],
                  fontSize: theme.typography.sizes.body,
                  color: theme.colors.text,
                  fontFamily: theme.typography.fontFamily,
                }}
              >
                <span
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: theme.colors.primary,
                    flexShrink: 0,
                  }}
                />
                <span>{role.role_name}</span>
                <span style={{ color: theme.colors.textTertiary, fontSize: theme.typography.sizes.caption }}>
                  (assigned {formatDate(role.assigned_at)})
                </span>
              </div>
            ))}
          </div>
        ) : (
          <span style={{ color: theme.colors.textTertiary, fontSize: theme.typography.sizes.bodySmall }}>
            No roles assigned
          </span>
        )}
      </SectionCard>
    </div>
  )
}

export default function UserInspector() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user, loading, error, deleteUser } = useUserInspector(id || '')
  const [activeTab, setActiveTab] = useState('overview')
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'resumes', label: 'Resumes' },
    { key: 'sessions', label: 'Sessions' },
    { key: 'timeline', label: 'Timeline' },
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

  if (error || !user) {
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
            onClick={() => navigate('/users')}
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
            Users
          </button>
        </nav>
        <Alert variant="error" title="User not found" action={{ label: 'Back to Users', onClick: () => navigate('/users') }}>
          {error || 'The requested user could not be found.'}
        </Alert>
      </div>
    )
  }

  const displayName = user.full_name || user.email

  const handleConfirmDelete = async () => {
    setDeleting(true)
    try {
      await deleteUser()
      setShowDeleteModal(false)
      navigate('/users')
    } catch {
      setDeleting(false)
    }
  }

  return (
    <div>
      <InspectorPanel
        title={displayName}
        subtitle={user.full_name ? user.email : undefined}
        breadcrumbs={[
          { label: 'Users', href: '/users' },
          { label: displayName },
        ]}
        icon={
          <Avatar
            src={user.avatar_url || undefined}
            name={displayName}
            size={64}
          />
        }
        headerRight={
          <div style={{ display: 'flex', gap: theme.spacing[2] }}>
            <Button variant="danger" size="sm" onClick={() => setShowDeleteModal(true)}>
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
            status={user.is_active ? 'success' : 'danger'}
            label={user.is_active ? 'Active' : 'Inactive'}
          />
          <StatusBadge
            status={user.is_verified ? 'success' : 'neutral'}
            label={user.is_verified ? 'Verified' : 'Unverified'}
          />
          {user.is_superuser && (
            <StatusBadge status="warning" label="Superuser" />
          )}
          <span
            style={{
              fontSize: theme.typography.sizes.caption,
              color: theme.colors.textTertiary,
              fontFamily: theme.typography.fontFamily,
              marginLeft: 'auto',
            }}
          >
            Joined {formatDate(user.created_at)}
          </span>
        </div>

        <Tabs tabs={tabs} activeKey={activeTab} onChange={setActiveTab} />

        <div style={{ marginTop: theme.spacing[4] }}>
          {activeTab === 'overview' && <OverviewTab user={user} />}
          {activeTab === 'resumes' && <ResumesTab userId={user.id} />}
          {activeTab === 'sessions' && <SessionsTab userId={user.id} />}
          {activeTab === 'timeline' && <TimelineTab userId={user.id} />}
        </div>
      </InspectorPanel>

      <Modal
        open={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete User"
        description={`Are you sure you want to delete ${displayName}? This action cannot be undone.`}
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowDeleteModal(false)} disabled={deleting}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleConfirmDelete} loading={deleting}>
              Delete
            </Button>
          </>
        }
      >
        <p
          style={{
            margin: 0,
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          The user will be soft-deleted and can be restored by an administrator.
        </p>
      </Modal>
    </div>
  )
}
