import { useState, useEffect, useCallback } from 'react'
import { getMetrics, getMetricsSummary } from '../../../../services/api/monitoring.service'
import type { MetricSummary } from '../../../../types/monitoring'

interface JobMetric {
  job_name: string
  status: string
  count: number
  avg_duration_ms: number
}

interface UseJobMetricsReturn {
  jobs: JobMetric[]
  summary: MetricSummary | null
  loading: boolean
  error: string | null
  statusFilter: string
  setStatusFilter: (s: string) => void
  refresh: () => Promise<void>
}

export function useJobMetrics(): UseJobMetricsReturn {
  const [jobs, setJobs] = useState<JobMetric[]>([])
  const [summary, setSummary] = useState<MetricSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState('')

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const now = new Date()
      const start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      const params = {
        metric_name: 'job_execution',
        start_time: start.toISOString(),
        end_time: now.toISOString(),
      }

      const [metricsRes, summaryRes] = await Promise.allSettled([
        getMetrics(params),
        getMetricsSummary({ start_time: start.toISOString(), end_time: now.toISOString() }),
      ])

      if (metricsRes.status === 'fulfilled') {
        const metrics = metricsRes.value.items || []
        const jobMap = new Map<string, JobMetric>()

        for (const m of metrics) {
          const dims = (m.dimensions || {}) as Record<string, unknown>
          const jobName = (dims.job_name as string) || 'unknown'
          const status = (dims.status as string) || 'unknown'
          const duration = (dims.duration_ms as number) || 0
          const key = `${jobName}-${status}`

          if (!jobMap.has(key)) {
            jobMap.set(key, { job_name: jobName, status, count: 0, avg_duration_ms: 0 })
          }
          const job = jobMap.get(key)!
          job.count += 1
          job.avg_duration_ms = (job.avg_duration_ms * (job.count - 1) + duration) / job.count
        }

        setJobs(Array.from(jobMap.values()))
      }

      if (summaryRes.status === 'fulfilled') {
        setSummary(summaryRes.value)
      }
    } catch {
      setError('Failed to load job metrics. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const filteredJobs = statusFilter
    ? jobs.filter((j) => j.status === statusFilter)
    : jobs

  return {
    jobs: filteredJobs,
    summary,
    loading,
    error,
    statusFilter,
    setStatusFilter,
    refresh: fetchData,
  }
}
