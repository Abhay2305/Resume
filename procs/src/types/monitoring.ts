// ============================================================================
// Monitoring Types
// Shared TypeScript interfaces for all monitoring pages.
// ============================================================================

// ---------------------------------------------------------------------------
// Error Log
// ---------------------------------------------------------------------------

export interface ErrorLog {
  id: string
  error_type: string
  error_message: string
  error_fingerprint: string | null
  severity: string
  status: string
  endpoint: string | null
  http_method: string | null
  response_status: number | null
  module: string | null
  function: string | null
  file_path: string | null
  line_number: number | null
  router: string | null
  stack_trace: string | null
  request_payload: string | null
  ip_address: string | null
  user_agent: string | null
  processing_time_ms: number | null
  environment: string | null
  user_id: string | null
  session_id: string | null
  request_id: string | null
  correlation_id: string | null
  retry_count: number
  occurrence_count: number
  first_occurrence_at: string | null
  last_occurrence_at: string | null
  metadata_json: string | null
  created_at: string
}

export interface ErrorListResponse {
  items: ErrorLog[]
  total: number
  page: number
  size: number
  totalPages: number
}

export interface ErrorStatsResponse {
  total: number
  by_severity: Record<string, number>
  by_status: Record<string, number>
  top_types: Array<{ error_type: string; count: number }>
  resolution_rate: number
}

export interface ErrorFilters {
  page: number
  size: number
  severity?: string
  status?: string
  error_type?: string
  router?: string
  start_date?: string
  end_date?: string
  search?: string
}

// ---------------------------------------------------------------------------
// Audit Log
// ---------------------------------------------------------------------------

export interface AuditLog {
  id: string
  user_id: string | null
  session_id: string | null
  request_id: string | null
  correlation_id: string | null
  entity_type: string
  entity_id: string | null
  action: string
  description: string | null
  previous_state: string | null
  new_state: string | null
  ip_address: string | null
  user_agent: string | null
  endpoint: string | null
  http_method: string | null
  request_body: string | null
  response_status: number | null
  response_body_summary: string | null
  error_message: string | null
  processing_time_ms: number | null
  metadata_json: string | null
  tags: string | null
  created_at: string
}

export interface AuditLogListResponse {
  success: boolean
  items: AuditLog[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface AuditLogFilters {
  page: number
  limit: number
  entity_type?: string
  action?: string
  user_id?: string
  start_date?: string
  end_date?: string
  search?: string
}

// ---------------------------------------------------------------------------
// Metrics
// ---------------------------------------------------------------------------

export interface Metric {
  id: string
  metric_name: string
  metric_value: number
  dimensions: Record<string, unknown> | null
  recorded_at: string
}

export interface MetricListResponse {
  items: Metric[]
  total: number
  page: number
  size: number
}

export interface MetricSummary {
  request_count: number
  avg_response_time_ms: number
  error_rate: number
  ai_tokens_total: number
  ai_cost_total: number
  period_start: string
  period_end: string
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export interface HealthCheck {
  status: string
  timestamp: string
  version: string
  checks: {
    database: {
      status: string
      pool?: {
        size: number
        checked_out: number
        overflow: number
      }
    }
    system: {
      python_version: string
      platform: string
    }
  }
}

export interface ProcsHealthResponse {
  database: { status: string; latency: string }
  ai_providers: { status: string; latency: string }
  storage: { status: string; latency: string }
  background_jobs: { status: string; latency: string }
}

// ---------------------------------------------------------------------------
// Dashboard Charts
// ---------------------------------------------------------------------------

export interface TimeSeriesPoint {
  label: string
  value: number
}

export interface TimeSeriesResponse {
  series: TimeSeriesPoint[]
  total: number
  period: string
}
