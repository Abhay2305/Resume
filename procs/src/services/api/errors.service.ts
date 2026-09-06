import { apiGet, apiPost } from './apiService'
import { API_ENDPOINTS } from './endpoints'
import type { ErrorListResponse, ErrorStatsResponse, ErrorLog } from '../../types/monitoring'

export async function getErrors(params?: Record<string, string | number | boolean | undefined>): Promise<ErrorListResponse> {
  return apiGet(API_ENDPOINTS.ERRORS, { params })
}

export async function getErrorStats(params?: Record<string, string | number | boolean | undefined>): Promise<ErrorStatsResponse> {
  return apiGet(API_ENDPOINTS.ERROR_STATS, { params })
}

export async function getError(id: string): Promise<ErrorLog> {
  return apiGet(API_ENDPOINTS.ERROR_BY_ID(id))
}

export async function acknowledgeError(id: string): Promise<{ success: boolean; error: ErrorLog; message: string }> {
  return apiPost(API_ENDPOINTS.ERROR_ACKNOWLEDGE(id))
}

export async function resolveError(id: string): Promise<{ success: boolean; error: ErrorLog; message: string }> {
  return apiPost(API_ENDPOINTS.ERROR_RESOLVE(id))
}
