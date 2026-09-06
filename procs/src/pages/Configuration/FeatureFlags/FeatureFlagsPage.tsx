import { useState } from 'react'
import { Plus } from 'lucide-react'
import { theme } from '../../../styles/theme'
import Button from '../../../components/shared/Button'
import MetricCard from '../../../components/shared/MetricCard'
import EmptyState from '../../../components/shared/EmptyState'
import FeatureFlagTable from './components/FeatureFlagTable'
import FeatureFlagModal from './components/FeatureFlagModal'
import FeatureFlagDeleteModal from './components/FeatureFlagDeleteModal'
import { useFeatureFlags } from './hooks/useFeatureFlags'
import { createFeatureFlag, deleteFeatureFlagByName, updateFeatureFlagByName } from '../../../services/api/settings.service'
import { useToast } from '../../../components/shared'
import type { FeatureFlag } from './types'

export default function FeatureFlagsPage() {
  const { flags, total, loading, error, filters, setFilters, toggleFlag, refresh } = useFeatureFlags()
  const { toast } = useToast()

  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [editFlag, setEditFlag] = useState<FeatureFlag | null>(null)
  const [deleteFlag, setDeleteFlag] = useState<FeatureFlag | null>(null)

  const enabledCount = flags.filter((f) => f.is_enabled).length
  const disabledCount = flags.length - enabledCount

  const handleCreate = async (data: Record<string, unknown>) => {
    await createFeatureFlag(data)
    toast({ variant: 'success', title: 'Feature flag created' })
    setCreateModalOpen(false)
    refresh()
  }

  const handleEdit = async (data: Record<string, unknown>) => {
    if (!editFlag) return
    await updateFeatureFlagByName(editFlag.name, data)
    toast({ variant: 'success', title: 'Feature flag updated' })
    setEditFlag(null)
    refresh()
  }

  const handleDelete = async (name: string) => {
    await deleteFeatureFlagByName(name)
    toast({ variant: 'success', title: 'Feature flag deleted' })
    refresh()
  }

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: theme.spacing[6] }}>
        <div>
          <h1 style={{ margin: 0, fontSize: theme.typography.sizes.h1, fontWeight: theme.typography.weights.bold, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
            Feature Flags
          </h1>
          <p style={{ margin: 0, marginTop: theme.spacing[1], fontSize: theme.typography.sizes.body, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
            Manage feature flags and rollout configuration
          </p>
        </div>
        <Button icon={<Plus size={16} />} onClick={() => setCreateModalOpen(true)}>
          Create Flag
        </Button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: theme.spacing[4], marginBottom: theme.spacing[6] }}>
        <MetricCard title="Total Flags" value={total} loading={loading} size="sm" />
        <MetricCard title="Enabled" value={enabledCount} loading={loading} size="sm" />
        <MetricCard title="Disabled" value={disabledCount} loading={loading} size="sm" />
      </div>

      {total === 0 && !loading ? (
        <EmptyState
          title="No feature flags"
          description="Create your first feature flag to start controlling feature rollout."
          action={{ label: 'Create Flag', onClick: () => setCreateModalOpen(true) }}
        />
      ) : (
        <FeatureFlagTable
          flags={flags}
          total={total}
          loading={loading}
          error={error}
          page={filters.page}
          perPage={filters.size}
          onPageChange={(page) => setFilters({ page })}
          onPerPageChange={(size) => setFilters({ size, page: 1 })}
          onToggle={toggleFlag}
          onEdit={setEditFlag}
          onDelete={setDeleteFlag}
          onRetry={refresh}
        />
      )}

      <FeatureFlagModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSubmit={handleCreate}
      />
      <FeatureFlagModal
        open={!!editFlag}
        flag={editFlag}
        onClose={() => setEditFlag(null)}
        onSubmit={handleEdit}
      />
      <FeatureFlagDeleteModal
        open={!!deleteFlag}
        flag={deleteFlag}
        onClose={() => setDeleteFlag(null)}
        onConfirm={handleDelete}
      />
    </div>
  )
}
