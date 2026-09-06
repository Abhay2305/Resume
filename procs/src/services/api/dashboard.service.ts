import { apiGet } from './apiService'
import { API_ENDPOINTS } from './endpoints'
import type { AiCostChartResponse } from '../../types/ai-monitoring'

export async function getDashboardStats() {
  return apiGet(API_ENDPOINTS.DASHBOARD_STATS)
}

export async function getDashboardActivity(limit = 10, cursor?: string) {
  return apiGet(API_ENDPOINTS.DASHBOARD_ACTIVITY, {
    params: { limit, ...(cursor ? { cursor } : {}) },
  })
}

export async function getDashboardHealth() {
  return apiGet(API_ENDPOINTS.DASHBOARD_HEALTH)
}

export async function getDashboardRecent(limit = 5) {
  return apiGet(API_ENDPOINTS.DASHBOARD_RECENT, { params: { limit } })
}

export async function getDashboardMetrics(period: string = '24h') {
  return apiGet(API_ENDPOINTS.DASHBOARD_METRICS, { params: { period } })
}

export async function getDashboardChartRequests(period: string = '24h') {
  return apiGet(API_ENDPOINTS.DASHBOARD_CHART_REQUESTS, { params: { period } })
}

export async function getDashboardChartErrors(period: string = '24h') {
  return apiGet(API_ENDPOINTS.DASHBOARD_CHART_ERRORS, { params: { period } })
}

export async function getDashboardChartAiCost(period: string = '24h'): Promise<AiCostChartResponse> {
  return apiGet(API_ENDPOINTS.DASHBOARD_CHART_AI_COST, { params: { period } })
}
