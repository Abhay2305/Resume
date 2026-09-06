import { useState, useEffect, useCallback } from 'react'
import { getAnalyticsFeatures } from '../../../services/api/analytics.service'
import type { FeatureUsageResponse } from '../types'

interface UseFeatureUsageResult {
  data: FeatureUsageResponse | null
  period: string
  setPeriod: (p: string) => void
  loading: boolean
  error: string | null
}

export function useFeatureUsage(): UseFeatureUsageResult {
  const [data, setData] = useState<FeatureUsageResponse | null>(null)
  const [period, setPeriod] = useState('30d')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await getAnalyticsFeatures({ period }) as FeatureUsageResponse
      setData(response)
    } catch {
      setError('Failed to load feature usage data. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [period])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, period, setPeriod, loading, error }
}
