import { theme } from '../../../../styles/theme'
import { ChartContainer, BarChart } from '../../../../components/shared'

interface JobMetric {
  job_name: string
  status: string
  count: number
  avg_duration_ms: number
}

interface JobChartProps {
  jobs: JobMetric[]
  loading: boolean
}

export default function JobChart({ jobs, loading }: JobChartProps) {
  const chartData = jobs.map((j) => ({
    label: j.job_name.length > 12 ? j.job_name.slice(0, 12) + '...' : j.job_name,
    value: j.count,
  }))

  return (
    <ChartContainer
      title="Job Executions"
      subtitle="Execution count by job"
      loading={loading}
      height={220}
    >
      <BarChart
        data={chartData}
        color={theme.chart.series3}
        height={200}
        formatValue={(v) => v.toLocaleString()}
      />
    </ChartContainer>
  )
}
