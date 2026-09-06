import { theme } from '../../../../styles/theme'
import { ChartContainer, LineChart } from '../../../../components/shared'

interface ResponseTimeChartProps {
  data: Array<{ label: string; value: number }> | null
  loading: boolean
}

export default function ResponseTimeChart({ data, loading }: ResponseTimeChartProps) {
  const chartData = data ?? []

  return (
    <ChartContainer
      title="Response Time"
      subtitle="Average response time (ms)"
      loading={loading}
      height={220}
    >
      <LineChart
        data={chartData}
        color={theme.chart.series2}
        height={200}
        formatValue={(v) => `${Math.round(v)}ms`}
      />
    </ChartContainer>
  )
}
