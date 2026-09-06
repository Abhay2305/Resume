import { useState, useEffect, useCallback } from 'react'
import {
  getDashboardStats,
  getDashboardActivity,
  getDashboardHealth,
  getDashboardMetrics,
  getDashboardChartRequests,
  getDashboardChartErrors,
  getDashboardChartAiCost,
} from '../../../services/api/dashboard.service'
import type {
  DashboardStats,
  DashboardActivity,
  DashboardHealth,
  DashboardMetric,
  ChartDataPoint,
  ActivityFeedResponse,
} from '../types'

export type Period = '24h' | '7d' | '30d'

interface UseDashboardReturn {
  stats: DashboardStats | null
  activity: DashboardActivity[]
  activityHasMore: boolean
  activityLoadingMore: boolean
  health: DashboardHealth | null
  metrics: DashboardMetric[]
  chartRequests: ChartDataPoint[] | null
  chartErrors: ChartDataPoint[] | null
  chartAiCost: ChartDataPoint[] | null
  period: Period
  loading: boolean
  chartsLoading: boolean
  error: string | null
  setPeriod: (period: Period) => void
  refresh: () => Promise<void>
  loadMoreActivity: () => Promise<void>
}

export function useDashboard(): UseDashboardReturn {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [activity, setActivity] = useState<DashboardActivity[]>([])
  const [activityHasMore, setActivityHasMore] = useState(false)
  const [activityLoadingMore, setActivityLoadingMore] = useState(false)
  const [activityCursor, setActivityCursor] = useState<string | null>(null)
  const [health, setHealth] = useState<DashboardHealth | null>(null)
  const [metrics, setMetrics] = useState<DashboardMetric[]>([])
  const [chartRequests, setChartRequests] = useState<ChartDataPoint[] | null>(null)
  const [chartErrors, setChartErrors] = useState<ChartDataPoint[] | null>(null)
  const [chartAiCost, setChartAiCost] = useState<ChartDataPoint[] | null>(null)
  const [period, setPeriod] = useState<Period>('24h')
  const [loading, setLoading] = useState(true)
  const [chartsLoading, setChartsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchChartData = useCallback(async () => {
    setChartsLoading(true)
    try {
      const [reqData, errData, costData] = await Promise.allSettled([
        getDashboardChartRequests(period),
        getDashboardChartErrors(period),
        getDashboardChartAiCost(period),
      ])

      if (reqData.status === 'fulfilled') {
        const res = reqData.value as { series?: ChartDataPoint[] }
        setChartRequests(res.series || [])
      }
      if (errData.status === 'fulfilled') {
        const res = errData.value as { series?: ChartDataPoint[] }
        setChartErrors(res.series || [])
      }
      if (costData.status === 'fulfilled') {
        const res = costData.value as { series?: ChartDataPoint[] }
        setChartAiCost(res.series || [])
      }
    } catch {
      // Charts fail silently
    } finally {
      setChartsLoading(false)
    }
  }, [period])

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const [statsData, activityData, healthData, metricsData] = await Promise.allSettled([
        getDashboardStats(),
        getDashboardActivity(10),
        getDashboardHealth(),
        getDashboardMetrics(period),
      ])

      if (statsData.status === 'fulfilled') setStats(statsData.value as DashboardStats)
      if (activityData.status === 'fulfilled') {
        const res = activityData.value as ActivityFeedResponse
        setActivity(res.activity || [])
        setActivityHasMore(res.has_more)
        setActivityCursor(res.next_cursor)
      }
      if (healthData.status === 'fulfilled') setHealth(healthData.value as DashboardHealth)
      if (metricsData.status === 'fulfilled') {
        const response = metricsData.value as { metrics: DashboardMetric[] }
        setMetrics(response.metrics || [])
      }

      const failures = [statsData, activityData, healthData, metricsData].filter(
        (r) => r.status === 'rejected',
      )
      if (failures.length === 4) {
        setError('Failed to load dashboard data. Please try again.')
      }
    } catch {
      setError('Failed to load dashboard data. Please try again.')
    } finally {
      setLoading(false)
    }

    fetchChartData()
  }, [period, fetchChartData])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const loadMoreActivity = useCallback(async () => {
    if (!activityHasMore || activityLoadingMore || !activityCursor) return

    setActivityLoadingMore(true)
    try {
      const res = await getDashboardActivity(10, activityCursor) as ActivityFeedResponse
      setActivity((prev) => [...prev, ...(res.activity || [])])
      setActivityHasMore(res.has_more)
      setActivityCursor(res.next_cursor)
    } catch {
      // Load more fails silently
    } finally {
      setActivityLoadingMore(false)
    }
  }, [activityHasMore, activityLoadingMore, activityCursor])

  return {
    stats,
    activity,
    activityHasMore,
    activityLoadingMore,
    health,
    metrics,
    chartRequests,
    chartErrors,
    chartAiCost,
    period,
    loading,
    chartsLoading,
    error,
    setPeriod,
    refresh: fetchData,
    loadMoreActivity,
  }
}
