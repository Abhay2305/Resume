import { useState, useEffect, useCallback } from 'react'
import { getAnalyticsFunnels } from '../../../services/api/analytics.service'
import type { FunnelsResponse } from '../types'

interface UseFunnelsResult {
  data: FunnelsResponse | null
  loading: boolean
  error: string | null
}

export function useFunnels(): UseFunnelsResult {
  const [data, setData] = useState<FunnelsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await getAnalyticsFunnels() as FunnelsResponse
      setData(response)
    } catch {
      setError('Failed to load funnel data. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error }
}
