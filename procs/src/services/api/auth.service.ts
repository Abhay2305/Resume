import { apiGet, apiPost } from './apiService'
import { API_ENDPOINTS } from './endpoints'
import type { AdminLoginRequest, AdminLoginResponse, AdminUser } from '../../types/auth'

export async function loginAdmin(data: AdminLoginRequest): Promise<AdminLoginResponse> {
  return apiPost<AdminLoginResponse>(API_ENDPOINTS.AUTH_LOGIN, data)
}

export async function logoutAdmin(): Promise<void> {
  return apiPost(API_ENDPOINTS.AUTH_LOGOUT)
}

export async function getCurrentAdmin(token: string): Promise<AdminUser> {
  return apiGet<AdminUser>(API_ENDPOINTS.AUTH_ME, {
    headers: { Authorization: `Bearer ${token}` },
  })
}
