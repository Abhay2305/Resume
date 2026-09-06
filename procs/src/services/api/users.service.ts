import { apiGet, apiPost, apiPut, apiDelete } from './apiService'
import { API_ENDPOINTS } from './endpoints'

export async function getUsers(params?: Record<string, string | number | boolean | undefined>) {
  return apiGet(API_ENDPOINTS.USERS, { params })
}

export async function getUserById(id: string) {
  return apiGet(API_ENDPOINTS.USER_BY_ID(id))
}

export async function createUser(data: unknown) {
  return apiPost(API_ENDPOINTS.USERS, data)
}

export async function updateUser(id: string, data: unknown) {
  return apiPut(API_ENDPOINTS.USER_BY_ID(id), data)
}

export async function deleteUser(id: string) {
  return apiDelete(API_ENDPOINTS.USER_BY_ID(id))
}
