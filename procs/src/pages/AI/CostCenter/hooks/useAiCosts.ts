import { useState, useEffect, useCallback } from 'react'
import { getDashboardChartAiCost } from '../../../../services/api/dashboard.service'
import type { AiCostChartResponse } from '../../../../types/ai-monitoring'

interface UseAiCostsReturn {
  data: AiCostChartResponse | null
  period: string
  setPeriod: (p: string) => void
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function useAiCosts(): UseAiCostsReturn {
  const [data, setData] = useState<AiCostChartResponse | null>(null)
  const [period, setPeriod] = useState('24h')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCosts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res: AiCostChartResponse = await getDashboardChartAiCost(period)
      setData(res)
    } catch {
      setError('Failed to load cost data')
    } finally {
      setLoading(false)
    }
  }, [period])

  useEffect(() => {
    fetchCosts()
  }, [fetchCosts])

  return { data, period, setPeriod, loading, error, refetch: fetchCosts }
}
