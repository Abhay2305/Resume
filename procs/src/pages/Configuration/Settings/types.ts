export interface SystemConfig {
  id: string
  key: string
  value: string
  category: string | null
  description: string | null
  is_public: boolean
  version: number
  created_at: string
  updated_at: string
}

export interface ConfigListResponse {
  items: SystemConfig[]
  total: number
  page: number
  size: number
}

export interface ConfigCreateRequest {
  key: string
  value: string
  category?: string
  description?: string
  is_public?: boolean
}

export interface ConfigUpdateRequest {
  value?: string
  category?: string
  description?: string
  is_public?: boolean
}

export interface ConfigFilters {
  category: string
  page: number
  size: number
}
