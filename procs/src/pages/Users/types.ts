export interface UserListItem {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  is_verified: boolean
  is_superuser: boolean
  avatar_url: string | null
  last_login_at: string | null
  created_at: string
}

export interface UserListResponse {
  items: UserListItem[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface UserListFilters {
  search: string
  is_active: boolean | null
  is_verified: boolean | null
  sort_by: string
  sort_order: 'asc' | 'desc'
  page: number
  limit: number
}

export interface UserProfile {
  job_title: string | null
  phone: string | null
  location: string | null
  company: string | null
  industry: string | null
}

export interface UserRole {
  id: string
  role_id: string
  role_name: string
  assigned_at: string
}

export interface UserDetail {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  is_verified: boolean
  is_superuser: boolean
  avatar_url: string | null
  timezone: string | null
  language: string
  last_login_at: string | null
  last_login_ip: string | null
  failed_login_attempts: number
  locked_until: string | null
  password_changed_at: string | null
  email_verified_at: string | null
  created_at: string
  updated_at: string
  profile: UserProfile | null
  roles: UserRole[]
}

export interface UserDetailResponse {
  success: boolean
  data: UserDetail
}

export interface UserTimelineEvent {
  id: string
  icon: string
  title: string
  description: string | null
  timestamp: string
  actor: string
  severity: 'info' | 'warning' | 'danger'
}

export interface UserTimelineResponse {
  success: boolean
  events: UserTimelineEvent[]
  total: number
  has_more: boolean
}

export interface UserSession {
  id: string
  ip_address: string | null
  user_agent: string | null
  device_type: string | null
  created_at: string
  expires_at: string | null
}

export interface UserSessionsResponse {
  success: boolean
  items: UserSession[]
  total: number
}
