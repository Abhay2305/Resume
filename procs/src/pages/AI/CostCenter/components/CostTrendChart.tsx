import { theme } from '../../../../styles/theme'
import { ChartContainer, LineChart } from '../../../../components/shared'
import type { AiCostChartResponse } from '../../../../types/ai-monitoring'

interface CostTrendChartProps {
  data: AiCostChartResponse | null
  loading: boolean
}

export default function CostTrendChart({ data, loading }: CostTrendChartProps) {
  const series = data?.series || []

  return (
    <ChartContainer title="Daily Cost Trend" height={200} loading={loading}>
      {series.length === 0 ? (
        <div style={{
          height: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: theme.colors.textTertiary,
          fontSize: theme.typography.sizes.bodySmall,
          fontFamily: theme.typography.fontFamily,
        }}>
          No trend data available
        </div>
      ) : (
        <LineChart
          data={series}
          height={200}
          formatValue={(v) => `$${v.toFixed(2)}`}
        />
      )}
    </ChartContainer>
  )
}
