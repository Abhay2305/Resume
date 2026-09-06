import { useState, useEffect, useCallback } from 'react'
import { getAuditLogs } from '../../../../services/api/monitoring.service'
import type { AuditLog, AuditLogFilters } from '../../../../types/monitoring'

const DEFAULT_FILTERS: AuditLogFilters = {
  page: 1,
  limit: 20,
}

interface UseAuditLogsReturn {
  logs: AuditLog[]
  total: number
  totalPages: number
  loading: boolean
  error: string | null
  filters: AuditLogFilters
  setFilters: (updates: Partial<AuditLogFilters>) => void
  refresh: () => Promise<void>
}

export function useAuditLogs(): UseAuditLogsReturn {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<AuditLogFilters>(DEFAULT_FILTERS)

  const fetchLogs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: Record<string, string | number | boolean | undefined> = {
        page: filters.page,
        limit: filters.limit,
      }
      if (filters.entity_type) params.entity_type = filters.entity_type
      if (filters.action) params.action = filters.action
      if (filters.user_id) params.user_id = filters.user_id
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date
      if (filters.search) params.search = filters.search

      const response = await getAuditLogs(params)
      setLogs(response.items || [])
      setTotal(response.total || 0)
      setTotalPages(response.totalPages || 1)
    } catch {
      setError('Failed to load audit logs. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchLogs()
  }, [fetchLogs])

  const setFilters = useCallback((updates: Partial<AuditLogFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...updates,
      page: updates.page ?? prev.page,
    }))
  }, [])

  return {
    logs,
    total,
    totalPages,
    loading,
    error,
    filters,
    setFilters,
    refresh: fetchLogs,
  }
}
