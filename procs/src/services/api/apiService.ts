import api from './axios'

interface RequestOptions {
  params?: Record<string, string | number | boolean | undefined>
  headers?: Record<string, string>
}

export async function apiGet<T>(
  endpoint: string,
  options?: RequestOptions,
): Promise<T> {
  const response = await api.get<T>(endpoint, {
    params: options?.params,
    headers: options?.headers,
  })
  return response.data
}

export async function apiPost<T>(
  endpoint: string,
  data?: unknown,
  options?: RequestOptions,
): Promise<T> {
  const response = await api.post<T>(endpoint, data, {
    headers: options?.headers,
  })
  return response.data
}

export async function apiPut<T>(
  endpoint: string,
  data?: unknown,
  options?: RequestOptions,
): Promise<T> {
  const response = await api.put<T>(endpoint, data, {
    headers: options?.headers,
  })
  return response.data
}

export async function apiPatch<T>(
  endpoint: string,
  data?: unknown,
  options?: RequestOptions,
): Promise<T> {
  const response = await api.patch<T>(endpoint, data, {
    headers: options?.headers,
  })
  return response.data
}

export async function apiDelete<T>(
  endpoint: string,
  options?: RequestOptions,
): Promise<T> {
  const response = await api.delete<T>(endpoint, {
    headers: options?.headers,
  })
  return response.data
}
