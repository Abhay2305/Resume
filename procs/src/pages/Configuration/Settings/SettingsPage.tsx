import { useState, useMemo } from 'react'
import { Plus } from 'lucide-react'
import { theme } from '../../../styles/theme'
import Button from '../../../components/shared/Button'
import MetricCard from '../../../components/shared/MetricCard'
import EmptyState from '../../../components/shared/EmptyState'
import ConfigTable from './components/ConfigTable'
import ConfigModal from './components/ConfigModal'
import ConfigDeleteModal from './components/ConfigDeleteModal'
import { useSettings } from './hooks/useSettings'
import { createConfig, updateConfigByKey, deleteConfigByKey } from '../../../services/api/settings.service'
import { useToast } from '../../../components/shared'
import type { SystemConfig } from './types'

const CATEGORY_OPTIONS = ['', 'app', 'auth', 'billing', 'ai', 'notification']

export default function SettingsPage() {
  const { configs, total, loading, error, filters, setFilters, refresh } = useSettings()
  const { toast } = useToast()

  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [editConfig, setEditConfig] = useState<SystemConfig | null>(null)
  const [deleteConfig, setDeleteConfig] = useState<SystemConfig | null>(null)

  const publicCount = useMemo(() => configs.filter((c) => c.is_public).length, [configs])
  const privateCount = configs.length - publicCount

  const handleCreate = async (data: Record<string, unknown>) => {
    await createConfig(data)
    toast({ variant: 'success', title: 'Configuration created' })
    setCreateModalOpen(false)
    refresh()
  }

  const handleEdit = async (data: Record<string, unknown>) => {
    if (!editConfig) return
    await updateConfigByKey(editConfig.key, data)
    toast({ variant: 'success', title: 'Configuration updated' })
    setEditConfig(null)
    refresh()
  }

  const handleDelete = async (key: string) => {
    await deleteConfigByKey(key)
    toast({ variant: 'success', title: 'Configuration deleted' })
    refresh()
  }

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: theme.spacing[6] }}>
        <div>
          <h1 style={{ margin: 0, fontSize: theme.typography.sizes.h1, fontWeight: theme.typography.weights.bold, color: theme.colors.text, fontFamily: theme.typography.fontFamily }}>
            System Configuration
          </h1>
          <p style={{ margin: 0, marginTop: theme.spacing[1], fontSize: theme.typography.sizes.body, color: theme.colors.textSecondary, fontFamily: theme.typography.fontFamily }}>
            Manage system-wide configuration settings
          </p>
        </div>
        <Button icon={<Plus size={16} />} onClick={() => setCreateModalOpen(true)}>
          Create Config
        </Button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: theme.spacing[4], marginBottom: theme.spacing[6] }}>
        <MetricCard title="Total Configs" value={total} loading={loading} size="sm" />
        <MetricCard title="Public" value={publicCount} loading={loading} size="sm" />
        <MetricCard title="Private" value={privateCount} loading={loading} size="sm" />
      </div>

      <div style={{ marginBottom: theme.spacing[4], display: 'flex', alignItems: 'center', gap: theme.spacing[3] }}>
        <select
          value={filters.category}
          onChange={(e) => setFilters({ category: e.target.value, page: 1 })}
          style={{
            padding: '8px 12px',
            fontSize: theme.typography.sizes.body,
            fontFamily: theme.typography.fontFamily,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            outline: 'none',
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            cursor: 'pointer',
          }}
        >
          {CATEGORY_OPTIONS.map((cat) => (
            <option key={cat} value={cat}>{cat || 'All Categories'}</option>
          ))}
        </select>
      </div>

      {total === 0 && !loading && !filters.category ? (
        <EmptyState
          title="No configurations"
          description="Create your first system configuration to get started."
          action={{ label: 'Create Config', onClick: () => setCreateModalOpen(true) }}
        />
      ) : (
        <ConfigTable
          configs={configs}
          total={total}
          loading={loading}
          error={error}
          page={filters.page}
          perPage={filters.size}
          onPageChange={(page) => setFilters({ page })}
          onPerPageChange={(size) => setFilters({ size, page: 1 })}
          onEdit={setEditConfig}
          onDelete={setDeleteConfig}
          onRetry={refresh}
        />
      )}

      <ConfigModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSubmit={handleCreate}
      />
      <ConfigModal
        open={!!editConfig}
        config={editConfig}
        onClose={() => setEditConfig(null)}
        onSubmit={handleEdit}
      />
      <ConfigDeleteModal
        open={!!deleteConfig}
        config={deleteConfig}
        onClose={() => setDeleteConfig(null)}
        onConfirm={handleDelete}
      />
    </div>
  )
}
