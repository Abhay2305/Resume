import { theme } from '../../../../styles/theme'
import { ChartContainer, LineChart } from '../../../../components/shared'
import type { AiTokenResponse } from '../../../../types/ai-monitoring'

interface TokenTrendChartProps {
  data: AiTokenResponse | null
  loading: boolean
}

export default function TokenTrendChart({ data, loading }: TokenTrendChartProps) {
  const series = data?.daily_trend || []

  return (
    <ChartContainer title="Daily Token Trend" height={200} loading={loading}>
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
          formatValue={(v) => v.toLocaleString()}
        />
      )}
    </ChartContainer>
  )
}
