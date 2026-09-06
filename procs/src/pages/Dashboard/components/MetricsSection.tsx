import { Users, FileText, Zap, AlertTriangle, DollarSign, BarChart3 } from 'lucide-react'
import MetricCard from '../../../components/shared/MetricCard'
import { theme } from '../../../styles/theme'
import type { DashboardMetric } from '../types'

interface MetricsSectionProps {
  metrics: DashboardMetric[]
  loading: boolean
  error: string | null
}

const iconMap: Record<string, React.ReactNode> = {
  total_users: <Users size={20} />,
  active_users: <Users size={20} />,
  total_resumes: <FileText size={20} />,
  ai_requests: <Zap size={20} />,
  system_errors: <AlertTriangle size={20} />,
  revenue_mtd: <DollarSign size={20} />,
}

const formatValue = (metric: DashboardMetric): string => {
  if (metric.id === 'revenue_mtd') {
    return `$${metric.value.toLocaleString()}`
  }
  return metric.value.toLocaleString()
}

export default function MetricsSection({ metrics, loading, error }: MetricsSectionProps) {
  if (loading && metrics.length === 0) {
    return (
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: theme.spacing[4],
          marginBottom: theme.spacing[6],
        }}
        className="dashboard-metrics-grid"
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <MetricCard key={i} title="" value="" loading />
        ))}
      </div>
    )
  }

  if (error && metrics.length === 0) {
    return (
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: theme.spacing[4],
          marginBottom: theme.spacing[6],
        }}
        className="dashboard-metrics-grid"
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <MetricCard key={i} title="Error" value="-" error="Failed to load" />
        ))}
      </div>
    )
  }

  if (metrics.length === 0) return null

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[6],
      }}
      className="dashboard-metrics-grid"
    >
      {metrics.map((metric) => (
        <MetricCard
          key={metric.id}
          title={metric.title}
          value={formatValue(metric)}
          trend={metric.trend}
          subtitle={metric.subtitle}
          icon={iconMap[metric.id] || <BarChart3 size={20} />}
          testId={`metric-${metric.id}`}
        />
      ))}
    </div>
  )
}
