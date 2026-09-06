import { useState, useEffect, useCallback } from 'react'
import { getFeatureFlags, updateFeatureFlagByName } from '../../../../services/api/settings.service'
import { useToast } from '../../../../components/shared'
import type { FeatureFlag, FeatureFlagFilters } from '../types'

const DEFAULT_FILTERS: FeatureFlagFilters = {
  page: 1,
  size: 20,
}

interface UseFeatureFlagsReturn {
  flags: FeatureFlag[]
  total: number
  loading: boolean
  error: string | null
  filters: FeatureFlagFilters
  setFilters: (updates: Partial<FeatureFlagFilters>) => void
  toggleFlag: (name: string, enabled: boolean) => Promise<void>
  refresh: () => Promise<void>
}

export function useFeatureFlags(): UseFeatureFlagsReturn {
  const [flags, setFlags] = useState<FeatureFlag[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<FeatureFlagFilters>(DEFAULT_FILTERS)
  const { toast } = useToast()

  const fetchFlags = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await getFeatureFlags(filters) as {
        items?: FeatureFlag[]
        total?: number
      }
      setFlags(response.items || [])
      setTotal(response.total || 0)
    } catch {
      setError('Failed to load feature flags. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchFlags()
  }, [fetchFlags])

  const setFilters = useCallback((updates: Partial<FeatureFlagFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...updates,
      page: updates.page ?? prev.page,
    }))
  }, [])

  const toggleFlag = useCallback(async (name: string, enabled: boolean) => {
    const previousFlags = flags
    setFlags((prev) =>
      prev.map((f) => (f.name === name ? { ...f, is_enabled: enabled } : f))
    )
    try {
      await updateFeatureFlagByName(name, { is_enabled: enabled })
      toast({ variant: 'success', title: `Flag ${enabled ? 'enabled' : 'disabled'}` })
    } catch {
      setFlags(previousFlags)
      toast({ variant: 'error', title: 'Failed to update flag' })
    }
  }, [flags, toast])

  return {
    flags,
    total,
    loading,
    error,
    filters,
    setFilters,
    toggleFlag,
    refresh: fetchFlags,
  }
}
