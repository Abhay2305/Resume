export interface FeatureFlag {
  id: string
  name: string
  description: string | null
  is_enabled: boolean
  rollout_percentage: number
  allowed_tiers: string[] | null
  environment: string
  created_at: string
  updated_at: string
}

export interface FeatureFlagListResponse {
  items: FeatureFlag[]
  total: number
  page: number
  size: number
}

export interface FeatureFlagCreateRequest {
  name: string
  description?: string
  is_enabled?: boolean
  rollout_percentage?: number
  allowed_tiers?: string[]
  environment?: string
}

export interface FeatureFlagUpdateRequest {
  description?: string
  is_enabled?: boolean
  rollout_percentage?: number
  allowed_tiers?: string[]
  environment?: string
}

export interface FeatureFlagFilters {
  page: number
  size: number
}
