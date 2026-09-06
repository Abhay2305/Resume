import { apiGet } from './apiService'
import { API_ENDPOINTS } from './endpoints'
import type {
  AuditLogListResponse,
  MetricListResponse,
  MetricSummary,
  HealthCheck,
  ProcsHealthResponse,
  TimeSeriesResponse,
} from '../../types/monitoring'

export async function getAuditLogs(params?: Record<string, string | number | boolean | undefined>): Promise<AuditLogListResponse> {
  return apiGet(API_ENDPOINTS.AUDIT, { params })
}

export async function getMetrics(params?: Record<string, string | number | boolean | undefined>): Promise<MetricListResponse> {
  return apiGet(API_ENDPOINTS.METRICS, { params })
}

export async function getMetricsSummary(params: Record<string, string | number | boolean | undefined>): Promise<MetricSummary> {
  return apiGet(API_ENDPOINTS.METRICS_SUMMARY, { params })
}

export async function getHealth(): Promise<HealthCheck> {
  return apiGet(API_ENDPOINTS.HEALTH)
}

export async function getProcsHealth(): Promise<ProcsHealthResponse> {
  return apiGet(API_ENDPOINTS.PROCS_HEALTH)
}

export async function getChartRequests(period: string = '24h'): Promise<TimeSeriesResponse> {
  return apiGet(API_ENDPOINTS.PROCS_CHART_REQUESTS, { params: { period } })
}

export async function getChartErrors(period: string = '24h'): Promise<TimeSeriesResponse> {
  return apiGet(API_ENDPOINTS.PROCS_CHART_ERRORS, { params: { period } })
}

export async function getChartAiCost(period: string = '24h'): Promise<TimeSeriesResponse> {
  return apiGet(API_ENDPOINTS.PROCS_CHART_AI_COST, { params: { period } })
}
