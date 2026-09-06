export interface RevenueDataPoint {
  label: string
  value: number
}

export interface RevenueSummary {
  total_revenue: number
  growth: number
  avg_revenue: number
  total_transactions: number
}

export interface RevenueResponse {
  success: boolean
  summary: RevenueSummary
  series: RevenueDataPoint[]
  period: string
}

export interface FeatureUsageItem {
  name: string
  count: number
  trend: number
}

export interface FeatureUsageResponse {
  success: boolean
  items: FeatureUsageItem[]
  total: number
  period: string
}

export interface FunnelStep {
  name: string
  count: number
  percentage: number
}

export interface FunnelData {
  name: string
  steps: FunnelStep[]
  completion_rate: number
}

export interface FunnelsResponse {
  success: boolean
  funnels: FunnelData[]
}
