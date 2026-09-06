import { apiGet } from './apiService'
import { API_ENDPOINTS } from './endpoints'

export async function getAnalyticsRevenue(params?: Record<string, string | number | boolean | undefined>) {
  return apiGet(API_ENDPOINTS.ANALYTICS_REVENUE, { params })
}

export async function getAnalyticsFeatures(params?: Record<string, string | number | boolean | undefined>) {
  return apiGet(API_ENDPOINTS.ANALYTICS_FEATURES, { params })
}

export async function getAnalyticsFunnels(params?: Record<string, string | number | boolean | undefined>) {
  return apiGet(API_ENDPOINTS.ANALYTICS_FUNNELS, { params })
}
