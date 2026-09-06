import { useState, useEffect, useCallback } from 'react'
import { getMetrics, getMetricsSummary, getChartRequests } from '../../../../services/api/monitoring.service'
import type { Metric, MetricSummary, TimeSeriesResponse } from '../../../../types/monitoring'

interface UseApiMetricsReturn {
  metrics: Metric[]
  summary: MetricSummary | null
  requestChart: TimeSeriesResponse | null
  period: string
  setPeriod: (p: string) => void
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export function useApiMetrics(): UseApiMetricsReturn {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [summary, setSummary] = useState<MetricSummary | null>(null)
  const [requestChart, setRequestChart] = useState<TimeSeriesResponse | null>(null)
  const [period, setPeriod] = useState('24h')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const now = new Date()
      let start: Date
      if (period === '24h') start = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      else if (period === '7d') start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      else start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)

      const params = {
        start_time: start.toISOString(),
        end_time: now.toISOString(),
      }

      const [metricsRes, summaryRes, chartRes] = await Promise.allSettled([
        getMetrics({ ...params, page: 1, limit: 100 }),
        getMetricsSummary(params),
        getChartRequests(period),
      ])

      if (metricsRes.status === 'fulfilled') setMetrics(metricsRes.value.items || [])
      if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value)
      if (chartRes.status === 'fulfilled') setRequestChart(chartRes.value)
    } catch {
      setError('Failed to load API metrics. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [period])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return {
    metrics,
    summary,
    requestChart,
    period,
    setPeriod,
    loading,
    error,
    refresh: fetchData,
  }
}
