import { useState, useEffect, useCallback } from 'react'
import { Shield, Clock, Mail, Globe, Calendar, User, Briefcase, CreditCard, Lock, Eye, Pencil } from 'lucide-react'
import Modal from '../../../components/shared/Modal'
import Tabs from '../../../components/shared/Tabs'
import Button from '../../../components/shared/Button'
import StatusBadge from '../../../components/shared/StatusBadge'
import Skeleton from '../../../components/shared/Skeleton'
import Alert from '../../../components/shared/Alert'
import Avatar from '../../../components/shared/Avatar'
import KeyValueList from '../../../components/shared/KeyValueList'
import { theme } from '../../../styles/theme'
import { useUserInspector } from '../hooks/useUserInspector'
import TimelineTab from './TimelineTab'
import ResumesTab from './ResumesTab'
import type { UserDetail } from '../types'

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

function inputStyle(editable: boolean): React.CSSProperties {
  return {
    width: '100%',
    padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
    border: `1px solid ${editable ? theme.colors.border : 'transparent'}`,
    borderRadius: theme.borderRadius.sm,
    fontSize: theme.typography.sizes.body,
    fontFamily: theme.typography.fontFamily,
    backgroundColor: editable ? theme.colors.surface : 'transparent',
    color: theme.colors.text,
    outline: editable ? 'none' : undefined,
  }
}

function selectStyle(editable: boolean): React.CSSProperties {
  return {
    width: '100%',
    padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
    border: `1px solid ${editable ? theme.colors.border : 'transparent'}`,
    borderRadius: theme.borderRadius.sm,
    fontSize: theme.typography.sizes.body,
    fontFamily: theme.typography.fontFamily,
    backgroundColor: editable ? theme.colors.surface : 'transparent',
    color: theme.colors.text,
    outline: editable ? 'none' : undefined,
    cursor: editable ? 'pointer' : 'default',
  }
}

function ProfileTab({ user, editable, formData, onFormChange }: {
  user: UserDetail
  editable: boolean
  formData: Record<string, unknown>
  onFormChange: (field: string, value: unknown) => void
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
      <SectionCard title="Personal Information">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
              Full Name
            </label>
            {editable ? (
              <input
                type="text"
                value={(formData.full_name as string) || ''}
                onChange={(e) => onFormChange('full_name', e.target.value)}
                style={inputStyle(true)}
              />
            ) : (
              <span style={{ fontSize: theme.typography.sizes.body, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
                {user.full_name || '—'}
              </span>
            )}
          </div>
          <div>
            <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
              Email
            </label>
            <span style={{ fontSize: theme.typography.sizes.body, color: theme.colors.text, fontFamily: theme.typography.fontFamily, display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
              <Mail size={14} color={theme.colors.textTertiary} />
              {user.email}
            </span>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Professional Information">
        <KeyValueList
          items={[
            { key: 'Job Title', value: user.profile?.job_title },
            { key: 'Company', value: user.profile?.company },
            { key: 'Industry', value: user.profile?.industry },
            { key: 'Phone', value: user.profile?.phone },
            { key: 'Location', value: user.profile?.location },
          ]}
          columns={3}
        />
      </SectionCard>

      <SectionCard title="Resume Statistics">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: theme.spacing[4] }}>
          {[
            { label: 'Total Resumes', value: '—' },
            { label: 'Published', value: '—' },
            { label: 'Drafts', value: '—' },
          ].map((stat) => (
            <div key={stat.label} style={{ textAlign: 'center', padding: theme.spacing[3], backgroundColor: theme.colors.surfaceHover, borderRadius: theme.borderRadius.sm }}>
              <div style={{ fontSize: theme.typography.sizes.h2, fontWeight: theme.typography.weights.bold, color: theme.colors.primary, fontFamily: theme.typography.fontFamily }}>
                {stat.value}
              </div>
              <div style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginTop: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Account Information">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
              Timezone
            </label>
            {editable ? (
              <select
                value={(formData.timezone as string) || 'UTC'}
                onChange={(e) => onFormChange('timezone', e.target.value)}
                style={selectStyle(true)}
              >
                {['UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles', 'Europe/London', 'Europe/Paris', 'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney'].map((tz) => (
                  <option key={tz} value={tz}>{tz}</option>
                ))}
              </select>
            ) : (
              <span style={{ fontSize: theme.typography.sizes.body, color: theme.colors.text, fontFamily: theme.typography.fontFamily, display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
                <Globe size={14} color={theme.colors.textTertiary} />
                {user.timezone || 'UTC'}
              </span>
            )}
          </div>
          <div>
            <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
              Language
            </label>
            {editable ? (
              <select
                value={(formData.language as string) || 'en'}
                onChange={(e) => onFormChange('language', e.target.value)}
                style={selectStyle(true)}
              >
                {['en', 'es', 'fr', 'de', 'ja', 'zh', 'pt', 'ar'].map((lang) => (
                  <option key={lang} value={lang}>{lang.toUpperCase()}</option>
                ))}
              </select>
            ) : (
              <span style={{ fontSize: theme.typography.sizes.body, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
                {(user.language || 'en').toUpperCase()}
              </span>
            )}
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4], marginTop: theme.spacing[4] }}>
          <div>
            <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
              Joined
            </label>
            <span style={{ fontSize: theme.typography.sizes.body, color: theme.colors.text, fontFamily: theme.typography.fontFamily, display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
              <Calendar size={14} color={theme.colors.textTertiary} />
              {formatDate(user.created_at)}
            </span>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
              Last Updated
            </label>
            <span style={{ fontSize: theme.typography.sizes.body, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
              {formatDate(user.updated_at)}
            </span>
          </div>
        </div>
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

function SubscriptionTab() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
      <SectionCard title="Subscription Information">
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[3], alignItems: 'center', padding: theme.spacing[6] }}>
          <CreditCard size={40} color={theme.colors.textTertiary} />
          <span style={{ fontSize: theme.typography.sizes.body, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily, textAlign: 'center' }}>
            Subscription data is managed through the user self-service portal.
          </span>
        </div>
      </SectionCard>
    </div>
  )
}

function SecurityTab({ user, editable, formData, onFormChange }: {
  user: UserDetail
  editable: boolean
  formData: Record<string, unknown>
  onFormChange: (field: string, value: unknown) => void
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
      <SectionCard title="Account Status">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing[4] }}>
          <div>
            <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
              Status
            </label>
            {editable ? (
              <select
                value={(formData.is_active as boolean) ? 'true' : 'false'}
                onChange={(e) => onFormChange('is_active', e.target.value === 'true')}
                style={selectStyle(true)}
              >
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            ) : (
              <StatusBadge status={user.is_active ? 'success' : 'danger'} label={user.is_active ? 'Active' : 'Inactive'} variant="dot" />
            )}
          </div>
          <div>
            <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
              Verified
            </label>
            {editable ? (
              <select
                value={(formData.is_verified as boolean) ? 'true' : 'false'}
                onChange={(e) => onFormChange('is_verified', e.target.value === 'true')}
                style={selectStyle(true)}
              >
                <option value="true">Verified</option>
                <option value="false">Unverified</option>
              </select>
            ) : (
              <StatusBadge status={user.is_verified ? 'success' : 'neutral'} label={user.is_verified ? 'Verified' : 'Unverified'} variant="dot" />
            )}
          </div>
        </div>
        <div style={{ marginTop: theme.spacing[4] }}>
          <label style={{ display: 'block', fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary, marginBottom: theme.spacing[1], fontFamily: theme.typography.fontFamily }}>
            Superuser
          </label>
          {editable ? (
            <select
              value={(formData.is_superuser as boolean) ? 'true' : 'false'}
              onChange={(e) => onFormChange('is_superuser', e.target.value === 'true')}
              style={selectStyle(true)}
            >
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          ) : (
            <span style={{ fontSize: theme.typography.sizes.body, color: user.is_superuser ? theme.colors.warning : theme.colors.text, fontFamily: theme.typography.fontFamily, display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
              {user.is_superuser && <Shield size={14} />}
              {user.is_superuser ? 'Yes' : 'No'}
            </span>
          )}
        </div>
      </SectionCard>

      <SectionCard title="Security Details">
        <KeyValueList
          items={[
            { key: 'Failed Logins', value: String(user.failed_login_attempts) },
            { key: 'Locked Until', value: user.locked_until ? formatDateTime(user.locked_until) : '—' },
            { key: 'Password Changed', value: formatDate(user.password_changed_at) },
            { key: 'Email Verified', value: formatDate(user.email_verified_at) },
            { key: 'Last Login', value: user.last_login_at ? `${formatRelativeTime(user.last_login_at)}${user.last_login_ip ? ` (${user.last_login_ip})` : ''}` : '—', icon: <Clock size={14} color={theme.colors.textTertiary} /> },
          ]}
          columns={2}
        />
      </SectionCard>
    </div>
  )
}

function ModalLoadingSkeleton() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
      <div style={{ display: 'flex', gap: theme.spacing[4] }}>
        <Skeleton variant="avatar" width={48} height={48} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: theme.spacing[2] }}>
          <Skeleton variant="heading" width="200px" />
          <Skeleton variant="text" width="150px" />
        </div>
      </div>
      <Skeleton variant="text" width="100%" height="40px" />
      {Array.from({ length: 3 }).map((_, i) => (
        <Skeleton key={i} variant="card" height="120px" />
      ))}
    </div>
  )
}

interface UserDetailModalProps {
  open: boolean
  onClose: () => void
  userId: string | null
  initialMode?: 'view' | 'edit'
  onUserUpdated?: () => void
  onUserDeleted?: () => void
}

export default function UserDetailModal({
  open,
  onClose,
  userId,
  initialMode = 'view',
  onUserUpdated,
  onUserDeleted,
}: UserDetailModalProps) {
  const { user, loading, error, refresh, updateUser, deleteUser } = useUserInspector(userId || '')
  const [activeTab, setActiveTab] = useState('profile')
  const [mode, setMode] = useState<'view' | 'edit'>(initialMode)
  const [formData, setFormData] = useState<Record<string, unknown>>({})
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      setMode(initialMode)
      setActiveTab('profile')
      setSaveError(null)
      setShowDeleteConfirm(false)
    }
  }, [open, initialMode])

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        timezone: user.timezone || 'UTC',
        language: user.language || 'en',
        is_active: user.is_active,
        is_verified: user.is_verified,
        is_superuser: user.is_superuser,
      })
    }
  }, [user])

  const handleFormChange = useCallback((field: string, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }, [])

  const handleSave = useCallback(async () => {
    if (!user) return
    setSaving(true)
    setSaveError(null)
    try {
      await updateUser(formData)
      setMode('view')
      onUserUpdated?.()
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to update user. Please try again.')
    } finally {
      setSaving(false)
    }
  }, [user, formData, updateUser, onUserUpdated])

  const handleDelete = useCallback(async () => {
    if (!user) return
    setDeleting(true)
    try {
      await deleteUser()
      setShowDeleteConfirm(false)
      onUserDeleted?.()
      onClose()
    } catch {
      setSaveError('Failed to delete user. Please try again.')
    } finally {
      setDeleting(false)
    }
  }, [user, deleteUser, onUserDeleted, onClose])

  const handleCancelEdit = useCallback(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        timezone: user.timezone || 'UTC',
        language: user.language || 'en',
        is_active: user.is_active,
        is_verified: user.is_verified,
        is_superuser: user.is_superuser,
      })
    }
    setMode('view')
    setSaveError(null)
  }, [user])

  const tabs = [
    { key: 'profile', label: 'Profile', icon: <User size={14} /> },
    { key: 'activity', label: 'Activity', icon: <Clock size={14} /> },
    { key: 'resumes', label: 'Resumes', icon: <Briefcase size={14} /> },
    { key: 'subscription', label: 'Subscription', icon: <CreditCard size={14} /> },
    { key: 'security', label: 'Security', icon: <Lock size={14} /> },
  ]

  const displayName = user ? (user.full_name || user.email) : ''

  return (
    <>
      <Modal
        open={open && !showDeleteConfirm}
        onClose={onClose}
        title={loading ? 'User Details' : displayName}
        description={loading ? undefined : user?.email}
        size="lg"
        footer={
          mode === 'edit' ? (
            <>
              <Button variant="secondary" onClick={handleCancelEdit} disabled={saving}>
                Cancel
              </Button>
              <Button variant="primary" onClick={handleSave} loading={saving}>
                Save Changes
              </Button>
            </>
          ) : (
            <>
              <Button variant="danger" size="sm" onClick={() => setShowDeleteConfirm(true)}>
                Delete
              </Button>
              <div style={{ flex: 1 }} />
              <Button variant="ghost" size="sm" onClick={onClose}>
                Close
              </Button>
              <Button variant="primary" size="sm" icon={<Pencil size={14} />} onClick={() => setMode('edit')}>
                Edit
              </Button>
            </>
          )
        }
      >
        {loading && <ModalLoadingSkeleton />}

        {error && !loading && (
          <Alert variant="error" title="Error loading user" action={{ label: 'Retry', onClick: refresh }}>
            {error}
          </Alert>
        )}

        {saveError && (
          <div style={{ marginBottom: theme.spacing[4] }}>
            <Alert variant="error" title="Error" action={{ label: 'Dismiss', onClick: () => setSaveError(null) }}>
              {saveError}
            </Alert>
          </div>
        )}

        {user && !loading && (
          <>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: theme.spacing[3],
                marginBottom: theme.spacing[4],
                paddingBottom: theme.spacing[4],
                borderBottom: `1px solid ${theme.colors.border}`,
              }}
            >
              <Avatar src={user.avatar_url || undefined} name={displayName} size={48} />
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
                  <span style={{ fontSize: theme.typography.sizes.h3, fontWeight: theme.typography.weights.semibold, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
                    {displayName}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2], marginTop: theme.spacing[1] }}>
                  <StatusBadge status={user.is_active ? 'success' : 'danger'} label={user.is_active ? 'Active' : 'Inactive'} variant="dot" />
                  <StatusBadge status={user.is_verified ? 'success' : 'neutral'} label={user.is_verified ? 'Verified' : 'Unverified'} variant="dot" />
                  {user.is_superuser && <StatusBadge status="warning" label="Superuser" />}
                  {mode === 'edit' && (
                    <span style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.info, backgroundColor: theme.colors.infoBg, padding: `2px ${theme.spacing[2]}`, borderRadius: theme.borderRadius.sm, fontFamily: theme.typography.fontFamily }}>
                      Editing
                    </span>
                  )}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[1] }}>
                {mode === 'view' && (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<Eye size={14} />}
                      onClick={() => setMode('view')}
                      style={{ color: mode === 'view' ? theme.colors.primary : theme.colors.textTertiary }}
                    >
                      View
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<Pencil size={14} />}
                      onClick={() => setMode('edit')}
                      style={{ color: theme.colors.textTertiary }}
                    >
                      Edit
                    </Button>
                  </>
                )}
              </div>
            </div>

            <Tabs tabs={tabs} activeKey={activeTab} onChange={setActiveTab} size="sm" />

            <div style={{ marginTop: theme.spacing[4] }}>
              {activeTab === 'profile' && (
                <ProfileTab user={user} editable={mode === 'edit'} formData={formData} onFormChange={handleFormChange} />
              )}
              {activeTab === 'activity' && <TimelineTab userId={user.id} />}
              {activeTab === 'resumes' && <ResumesTab userId={user.id} />}
              {activeTab === 'subscription' && <SubscriptionTab />}
              {activeTab === 'security' && (
                <SecurityTab user={user} editable={mode === 'edit'} formData={formData} onFormChange={handleFormChange} />
              )}
            </div>
          </>
        )}
      </Modal>

      <Modal
        open={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        title="Delete User"
        description={`Are you sure you want to delete ${displayName}? This action cannot be undone.`}
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowDeleteConfirm(false)} disabled={deleting}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDelete} loading={deleting}>
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
    </>
  )
}
