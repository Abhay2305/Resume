import { useState, useEffect, useCallback } from 'react'
import { getAnalyticsRevenue } from '../../../services/api/analytics.service'
import type { RevenueResponse } from '../types'

interface UseRevenueResult {
  data: RevenueResponse | null
  period: string
  setPeriod: (p: string) => void
  loading: boolean
  error: string | null
}

export function useRevenue(): UseRevenueResult {
  const [data, setData] = useState<RevenueResponse | null>(null)
  const [period, setPeriod] = useState('30d')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await getAnalyticsRevenue({ period }) as RevenueResponse
      setData(response)
    } catch {
      setError('Failed to load revenue data. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [period])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, period, setPeriod, loading, error }
}
