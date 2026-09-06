export interface AdminUser {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface AdminLoginRequest {
  email: string
  password: string
}

export interface AdminLoginResponse {
  access_token: string
  token_type: string
  admin: AdminUser
}
