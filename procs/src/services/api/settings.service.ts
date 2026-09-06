import { apiGet, apiPost, apiPut, apiDelete } from './apiService'
import { API_ENDPOINTS } from './endpoints'
import type { FeatureFlagFilters } from '../../pages/Configuration/FeatureFlags/types'
import type { ConfigFilters } from '../../pages/Configuration/Settings/types'

export async function getFeatureFlags(filters: FeatureFlagFilters) {
  const params: Record<string, string | number> = {
    page: filters.page,
    size: filters.size,
  }
  return apiGet(API_ENDPOINTS.CONFIG_FLAGS, { params })
}

export async function createFeatureFlag(data: Record<string, unknown>) {
  return apiPost(API_ENDPOINTS.CONFIG_FLAGS, data)
}

export async function updateFeatureFlagByName(name: string, data: Record<string, unknown>) {
  return apiPut(API_ENDPOINTS.CONFIG_FLAG_BY_NAME(name), data)
}

export async function deleteFeatureFlagByName(name: string) {
  return apiDelete(API_ENDPOINTS.CONFIG_FLAG_BY_NAME(name))
}

export async function getSettings(filters: ConfigFilters) {
  const params: Record<string, string | number> = {
    page: filters.page,
    size: filters.size,
  }
  if (filters.category) params.category = filters.category
  return apiGet(API_ENDPOINTS.CONFIG, { params })
}

export async function createConfig(data: Record<string, unknown>) {
  return apiPost(API_ENDPOINTS.CONFIG, data)
}

export async function updateConfigByKey(key: string, data: Record<string, unknown>) {
  return apiPut(API_ENDPOINTS.CONFIG_BY_KEY(key), data)
}

export async function deleteConfigByKey(key: string) {
  return apiDelete(API_ENDPOINTS.CONFIG_BY_KEY(key))
}
