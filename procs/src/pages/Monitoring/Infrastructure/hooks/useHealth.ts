import { useState, useEffect, useCallback } from 'react'
import { getHealth, getProcsHealth } from '../../../../services/api/monitoring.service'
import type { HealthCheck, ProcsHealthResponse } from '../../../../types/monitoring'

interface UseHealthReturn {
  health: HealthCheck | null
  procsHealth: ProcsHealthResponse | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export function useHealth(): UseHealthReturn {
  const [health, setHealth] = useState<HealthCheck | null>(null)
  const [procsHealth, setProcsHealth] = useState<ProcsHealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [healthRes, procsRes] = await Promise.allSettled([
        getHealth(),
        getProcsHealth(),
      ])

      if (healthRes.status === 'fulfilled') setHealth(healthRes.value)
      if (procsRes.status === 'fulfilled') setProcsHealth(procsRes.value)
    } catch {
      setError('Failed to load health data. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return {
    health,
    procsHealth,
    loading,
    error,
    refresh: fetchData,
  }
}
