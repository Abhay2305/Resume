import { useState, useEffect, useCallback, useRef } from 'react'
import { getErrors, getErrorStats } from '../../../../services/api/errors.service'
import type { ErrorLog, ErrorFilters, ErrorStatsResponse } from '../../../../types/monitoring'

const DEFAULT_FILTERS: ErrorFilters = {
  page: 1,
  size: 20,
}

const AUTO_REFRESH_INTERVAL = 15000

interface UseErrorsReturn {
  errors: ErrorLog[]
  total: number
  totalPages: number
  stats: ErrorStatsResponse | null
  loading: boolean
  error: string | null
  filters: ErrorFilters
  setFilters: (updates: Partial<ErrorFilters>) => void
  refresh: () => Promise<void>
  autoRefresh: boolean
  setAutoRefresh: (v: boolean) => void
}

export function useErrors(): UseErrorsReturn {
  const [errors, setErrors] = useState<ErrorLog[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [stats, setStats] = useState<ErrorStatsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<ErrorFilters>(DEFAULT_FILTERS)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchErrors = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: Record<string, string | number | boolean | undefined> = {
        page: filters.page,
        size: filters.size,
      }
      if (filters.severity) params.severity = filters.severity
      if (filters.status) params.status = filters.status
      if (filters.error_type) params.error_type = filters.error_type
      if (filters.router) params.router = filters.router
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date
      if (filters.search) params.search = filters.search

      const [errorsRes, statsRes] = await Promise.all([
        getErrors(params),
        getErrorStats(),
      ])
      setErrors(errorsRes.items || [])
      setTotal(errorsRes.total || 0)
      setTotalPages(errorsRes.totalPages || 1)
      setStats(statsRes)
    } catch {
      setError('Failed to load errors. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchErrors()
  }, [fetchErrors])

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchErrors, AUTO_REFRESH_INTERVAL)
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [autoRefresh, fetchErrors])

  const setFilters = useCallback((updates: Partial<ErrorFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...updates,
      page: updates.page ?? prev.page,
    }))
  }, [])

  return {
    errors,
    total,
    totalPages,
    stats,
    loading,
    error,
    filters,
    setFilters,
    refresh: fetchErrors,
    autoRefresh,
    setAutoRefresh,
  }
}
