import { theme } from '../../../../styles/theme'
import { ChartContainer, BarChart } from '../../../../components/shared'
import type { AiTokenResponse } from '../../../../types/ai-monitoring'

interface TokenByModelProps {
  data: AiTokenResponse | null
  loading: boolean
}

export default function TokenByModel({ data, loading }: TokenByModelProps) {
  const chartData = (data?.by_model || []).map((item) => ({
    label: item.model,
    value: item.tokens,
  }))

  return (
    <ChartContainer title="Tokens by Model" height={200} loading={loading}>
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
          No token data available
        </div>
      ) : (
        <BarChart
          data={chartData}
          height={200}
          formatValue={(v) => v.toLocaleString()}
        />
      )}
    </ChartContainer>
  )
}
