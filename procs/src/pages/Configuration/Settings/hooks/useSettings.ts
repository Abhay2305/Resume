import { useState, useEffect, useCallback } from 'react'
import { getSettings } from '../../../../services/api/settings.service'
import type { SystemConfig, ConfigFilters } from '../types'

const DEFAULT_FILTERS: ConfigFilters = {
  category: '',
  page: 1,
  size: 20,
}

interface UseSettingsReturn {
  configs: SystemConfig[]
  total: number
  loading: boolean
  error: string | null
  filters: ConfigFilters
  setFilters: (updates: Partial<ConfigFilters>) => void
  refresh: () => Promise<void>
}

export function useSettings(): UseSettingsReturn {
  const [configs, setConfigs] = useState<SystemConfig[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<ConfigFilters>(DEFAULT_FILTERS)

  const fetchConfigs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await getSettings(filters) as {
        items?: SystemConfig[]
        total?: number
      }
      setConfigs(response.items || [])
      setTotal(response.total || 0)
    } catch {
      setError('Failed to load system configurations. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchConfigs()
  }, [fetchConfigs])

  const setFilters = useCallback((updates: Partial<ConfigFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...updates,
      page: updates.page ?? (updates.category !== undefined ? 1 : prev.page),
    }))
  }, [])

  return {
    configs,
    total,
    loading,
    error,
    filters,
    setFilters,
    refresh: fetchConfigs,
  }
}
