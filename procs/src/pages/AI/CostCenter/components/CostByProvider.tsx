import { theme } from '../../../../styles/theme'
import { ChartContainer, BarChart } from '../../../../components/shared'
import type { AiCostChartResponse } from '../../../../types/ai-monitoring'

interface CostByProviderProps {
  data: AiCostChartResponse | null
  loading: boolean
}

export default function CostByProvider({ data, loading }: CostByProviderProps) {
  const chartData = (data?.by_provider || []).map((item) => ({
    label: item.provider,
    value: item.total_cost,
  }))

  return (
    <ChartContainer title="Cost by Provider" height={200} loading={loading}>
      {chartData.length === 0 ? (
        <div style={{
          height: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: theme.colors.textTertiary,
          fontSize: theme.typography.sizes.bodySmall,
          fontFamily: theme.typography.fontFamily,
        }}>
          No cost data available
        </div>
      ) : (
        <BarChart
          data={chartData}
          height={200}
          formatValue={(v) => `$${v.toFixed(2)}`}
        />
      )}
    </ChartContainer>
  )
}
