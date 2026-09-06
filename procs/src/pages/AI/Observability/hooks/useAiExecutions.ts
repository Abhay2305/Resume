import { useState, useEffect, useCallback } from 'react'
import { getAiAdminExecutions, getAiAdminExecutionStats } from '../../../../services/api/ai.service'
import type { AiExecutionLog, AiExecutionFilters, AiExecutionStatsResponse } from '../../../../types/ai-monitoring'

const DEFAULT_FILTERS: AiExecutionFilters = {
  page: 1,
  size: 20,
}

interface UseAiExecutionsReturn {
  executions: AiExecutionLog[]
  total: number
  stats: AiExecutionStatsResponse | null
  loading: boolean
  error: string | null
  filters: AiExecutionFilters
  setFilters: (updates: Partial<AiExecutionFilters>) => void
  refresh: () => Promise<void>
}

export function useAiExecutions(): UseAiExecutionsReturn {
  const [executions, setExecutions] = useState<AiExecutionLog[]>([])
  const [total, setTotal] = useState(0)
  const [stats, setStats] = useState<AiExecutionStatsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<AiExecutionFilters>(DEFAULT_FILTERS)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: Record<string, string | number | boolean | undefined> = {
        page: filters.page,
        size: filters.size,
      }
      if (filters.provider) params.provider = filters.provider
      if (filters.status) params.status = filters.status
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date

      const [execRes, statsRes] = await Promise.all([
        getAiAdminExecutions(params),
        getAiAdminExecutionStats({ period: '24h' }),
      ])
      setExecutions(execRes.items || [])
      setTotal(execRes.total || 0)
      setStats(statsRes)
    } catch {
      setError('Failed to load execution data')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const setFilters = useCallback((updates: Partial<AiExecutionFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...updates,
      page: updates.page ?? prev.page,
    }))
  }, [])

  return {
    executions,
    total,
    stats,
    loading,
    error,
    filters,
    setFilters,
    refresh: fetchData,
  }
}
