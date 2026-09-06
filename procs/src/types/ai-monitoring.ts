// ============================================================================
// AI Monitoring Types
// TypeScript interfaces for AI monitoring data structures.
// ============================================================================

// ---------------------------------------------------------------------------
// Execution Log
// ---------------------------------------------------------------------------

export interface AiExecutionLog {
  id: string
  prompt_package_id: string
  provider: string
  model: string
  status: string
  total_tokens: number | null
  estimated_cost: number | null
  execution_time_ms: number | null
  created_at: string
}

export interface AiExecutionListResponse {
  items: AiExecutionLog[]
  total: number
  page: number
  size: number
}

export interface AiExecutionFilters {
  page: number
  size: number
  provider?: string
  status?: string
  start_date?: string
  end_date?: string
}

// ---------------------------------------------------------------------------
// Execution Stats
// ---------------------------------------------------------------------------

export interface AiExecutionStatsResponse {
  total_executions: number
  success_rate: number
  failure_rate: number
  avg_latency_ms: number
  total_retries: number
  by_status: Record<string, number>
  daily_trend: Array<{ label: string; value: number }>
}

// ---------------------------------------------------------------------------
// Cost Analytics (matches dashboard /charts/ai-cost response)
// ---------------------------------------------------------------------------

export interface AiCostChartResponse {
  series: Array<{ label: string; value: number }>
  by_provider: Array<{ provider: string; total_cost: number }>
  total_cost: number
  period: string
}

// ---------------------------------------------------------------------------
// Token Analytics
// ---------------------------------------------------------------------------

export interface AiTokenModelBreakdown {
  model: string
  tokens: number
  percentage: number
}

export interface AiTokenResponse {
  total_tokens: number
  by_model: AiTokenModelBreakdown[]
  daily_trend: Array<{ label: string; value: number }>
  avg_tokens_per_request: number
  period: string
}

// ---------------------------------------------------------------------------
// Provider Stats
// ---------------------------------------------------------------------------

export interface AiProviderModelStats {
  model: string
  executions: number
  tokens: number
}

export interface AiProviderDetail {
  name: string
  healthy: boolean
  total_executions: number
  success_rate: number
  avg_latency_ms: number
  total_cost: number
  total_tokens: number
  models: AiProviderModelStats[]
}

export interface AiProviderStatsResponse {
  providers: AiProviderDetail[]
}
