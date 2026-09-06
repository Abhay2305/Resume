export interface ApiSuccessResponse<T> {
  success: boolean
  data: T
  request_id?: string
  correlation_id?: string
}

export interface ApiErrorResponse {
  success: boolean
  error: {
    code: string
    message: string
    details?: Array<{ field: string; message: string }>
  }
  request_id?: string
  correlation_id?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}
