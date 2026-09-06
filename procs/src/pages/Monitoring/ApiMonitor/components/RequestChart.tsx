import { theme } from '../../../../styles/theme'
import { ChartContainer, LineChart } from '../../../../components/shared'
import type { TimeSeriesResponse } from '../../../../types/monitoring'

interface RequestChartProps {
  data: TimeSeriesResponse | null
  loading: boolean
}

export default function RequestChart({ data, loading }: RequestChartProps) {
  const chartData = data?.series?.map((p) => ({ label: p.label, value: p.value })) ?? []

  return (
    <ChartContainer
      title="Request Volume"
      subtitle="API requests over time"
      loading={loading}
      height={220}
    >
      <LineChart
        data={chartData}
        color={theme.chart.series1}
        height={200}
        formatValue={(v) => v.toLocaleString()}
      />
    </ChartContainer>
  )
}
