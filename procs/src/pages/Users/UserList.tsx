import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Eye, Pencil, Trash2 } from 'lucide-react'
import DataTable from '../../components/shared/DataTable'
import StatusBadge from '../../components/shared/StatusBadge'
import Button from '../../components/shared/Button'
import { theme } from '../../styles/theme'
import { useUserList } from './hooks/useUserList'
import UserDetailModal from './components/UserDetailModal'
import type { UserListItem } from './types'

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

export default function UserList() {
  const navigate = useNavigate()
  const { users, total, loading, error, filters, searchInput, setSearchInput, setFilters, refresh } = useUserList()
  const [modalOpen, setModalOpen] = useState(false)
  const [modalUserId, setModalUserId] = useState<string | null>(null)
  const [modalMode, setModalMode] = useState<'view' | 'edit'>('view')

  const handleView = useCallback((e: React.MouseEvent, userId: string) => {
    e.stopPropagation()
    setModalUserId(userId)
    setModalMode('view')
    setModalOpen(true)
  }, [])

  const handleEdit = useCallback((e: React.MouseEvent, userId: string) => {
    e.stopPropagation()
    setModalUserId(userId)
    setModalMode('edit')
    setModalOpen(true)
  }, [])

  const handleDeleteRequest = useCallback((e: React.MouseEvent, userId: string) => {
    e.stopPropagation()
    setModalUserId(userId)
    setModalMode('view')
    setModalOpen(true)
  }, [])

  const handleModalClose = useCallback(() => {
    setModalOpen(false)
    setModalUserId(null)
  }, [])

  const handleUserUpdated = useCallback(() => {
    refresh()
  }, [refresh])

  const handleUserDeleted = useCallback(() => {
    refresh()
  }, [refresh])

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
      key: 'email',
      label: 'Email',
      sortable: true,
      render: (value: unknown) => (
        <span style={{ fontWeight: theme.typography.weights.medium, color: theme.colors.text }}>
          {String(value)}
        </span>
      ),
    },
    {
      key: 'full_name',
      label: 'Name',
      sortable: true,
      render: (value: unknown) => (
        <span style={{ color: value ? theme.colors.text : theme.colors.textTertiary }}>
          {String(value || '—')}
        </span>
      ),
    },
    {
      key: 'is_active',
      label: 'Status',
      sortable: true,
      width: '100px',
      render: (value: unknown) => {
        const isActive = value as boolean
        return (
          <StatusBadge
            status={isActive ? 'success' : 'danger'}
            label={isActive ? 'Active' : 'Inactive'}
            variant="dot"
          />
        )
      },
    },
    {
      key: 'is_verified',
      label: 'Verified',
      width: '100px',
      render: (value: unknown) => {
        const isVerified = Boolean(value)
        return (
          <span
            style={{
              color: isVerified ? theme.colors.success : theme.colors.textTertiary,
              fontSize: theme.typography.sizes.caption,
            }}
          >
            {isVerified ? 'Verified' : 'Unverified'}
          </span>
        )
      },
    },
    {
      key: 'last_login_at',
      label: 'Last Login',
      sortable: true,
      width: '120px',
      render: (value: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary }}>
          {formatRelativeTime(value as string | null)}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Joined',
      sortable: true,
      width: '120px',
      render: (value: unknown) => (
        <span style={{ fontSize: theme.typography.sizes.caption, color: theme.colors.textSecondary }}>
          {formatRelativeTime(value as string)}
        </span>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      width: '120px',
      render: (_value: unknown, row: Record<string, unknown>) => {
        const user = row as unknown as UserListItem
        return (
          <div style={{ display: 'flex', gap: theme.spacing[1] }} onClick={(e) => e.stopPropagation()}>
            <Button
              variant="ghost"
              size="sm"
              icon={<Eye size={14} />}
              onClick={(e) => handleView(e, user.id)}
              aria-label={`View ${user.full_name || user.email}`}
            />
            <Button
              variant="ghost"
              size="sm"
              icon={<Pencil size={14} />}
              onClick={(e) => handleEdit(e, user.id)}
              aria-label={`Edit ${user.full_name || user.email}`}
            />
            <Button
              variant="ghost"
              size="sm"
              icon={<Trash2 size={14} />}
              onClick={(e) => handleDeleteRequest(e, user.id)}
              aria-label={`Delete ${user.full_name || user.email}`}
              style={{ color: theme.colors.danger }}
            />
          </div>
        )
      },
    },
  ]

  const handleRowClick = (row: Record<string, unknown>) => {
    const user = row as unknown as UserListItem
    navigate(`/users/${user.id}`)
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
            Users
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
            Manage system users and their access
          </p>
        </div>
      </div>

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
            placeholder="Search by name or email..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            aria-label="Search users"
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
          value={filters.is_active === null ? '' : String(filters.is_active)}
          onChange={(e) => setFilters({ is_active: e.target.value === '' ? null : e.target.value === 'true' })}
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
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>

        <select
          value={filters.is_verified === null ? '' : String(filters.is_verified)}
          onChange={(e) => setFilters({ is_verified: e.target.value === '' ? null : e.target.value === 'true' })}
          aria-label="Filter by verified status"
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
          <option value="">All Verified</option>
          <option value="true">Verified</option>
          <option value="false">Unverified</option>
        </select>
      </div>

      <DataTable
        columns={columns}
        data={users as unknown as Record<string, unknown>[]}
        loading={loading}
        error={error}
        errorRetry={refresh}
        empty="No users found"
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

      <UserDetailModal
        open={modalOpen}
        onClose={handleModalClose}
        userId={modalUserId}
        initialMode={modalMode}
        onUserUpdated={handleUserUpdated}
        onUserDeleted={handleUserDeleted}
      />
    </div>
  )
}
