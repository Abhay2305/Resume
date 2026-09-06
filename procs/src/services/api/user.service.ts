import { apiGet, apiPut, apiDelete } from './apiService'
import { API_ENDPOINTS } from './endpoints'
import type { UserListFilters } from '../../pages/Users/types'

export async function getUsers(filters: UserListFilters) {
  const params: Record<string, string | number | boolean> = {
    page: filters.page,
    limit: filters.limit,
    sort_by: filters.sort_by,
    sort_order: filters.sort_order,
  }

  if (filters.search) params.search = filters.search
  if (filters.is_active !== null) params.is_active = filters.is_active
  if (filters.is_verified !== null) params.is_verified = filters.is_verified

  return apiGet(API_ENDPOINTS.PROCS_USERS, { params })
}

export async function getUserDetail(userId: string) {
  return apiGet(API_ENDPOINTS.PROCS_USER_BY_ID(userId))
}

export async function updateUser(userId: string, data: Record<string, unknown>) {
  return apiPut(API_ENDPOINTS.PROCS_USER_BY_ID(userId), data)
}

export async function deleteUser(userId: string) {
  return apiDelete(API_ENDPOINTS.PROCS_USER_BY_ID(userId))
}

export async function getUserTimeline(
  userId: string,
  params?: { limit?: number; offset?: number; action?: string }
) {
  return apiGet(API_ENDPOINTS.PROCS_USER_TIMELINE(userId), { params })
}

export async function getUserSessions(userId: string) {
  return apiGet(API_ENDPOINTS.PROCS_USER_SESSIONS(userId))
}
