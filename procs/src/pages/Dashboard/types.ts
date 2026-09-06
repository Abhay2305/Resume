export interface DashboardStats {
  users: { total: number; active_24h: number }
  resumes: { total: number; created_24h: number }
  cover_letters: { total: number }
  ai_requests: { total: number; '24h': number }
  errors: { total: number; '24h': number }
  subscriptions: { active: number }
  opportunities: { total: number }
  ats_results: { total: number }
}

export interface DashboardActivity {
  id: string
  action: string
  subject: string
  subject_type: string
  timestamp: string
  admin_email?: string
  icon_type: string
  entity_label: string
}

export interface ActivityFeedResponse {
  activity: DashboardActivity[]
  has_more: boolean
  next_cursor: string | null
}

export interface DashboardHealth {
  database: { status: string; latency?: string }
  ai_providers: { status: string; latency?: string }
  storage: { status: string; latency?: string }
  background_jobs: { status: string; latency?: string }
}

export interface DashboardRecent {
  errors: Array<{ id: string; message: string; timestamp: string }>
  activity: DashboardActivity[]
}

export interface DashboardMetric {
  id: string
  title: string
  value: number
  trend: number
  subtitle: string
}

export interface DashboardMetricsResponse {
  metrics: DashboardMetric[]
  period: string
}

export interface ChartDataPoint {
  label: string
  value: number
}

export interface ChartSeriesResponse {
  series: ChartDataPoint[]
  total: number
  period: string
}

export interface AiCostChartResponse {
  series: ChartDataPoint[]
  by_provider: Array<{ provider: string; total_cost: number }>
  total_cost: number
  period: string
}
