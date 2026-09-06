import { theme } from '../../../styles/theme'
import { ChartContainer, LineChart, BarChart } from '../../../components/shared'

interface DataPoint {
  label: string
  value: number
}

interface ChartsGridProps {
  chartRequests: DataPoint[] | null
  chartErrors: DataPoint[] | null
  chartAiCost: DataPoint[] | null
  loading?: boolean
}

export default function ChartsGrid({
  chartRequests,
  chartErrors,
  chartAiCost,
  loading = false,
}: ChartsGridProps) {
  const formatCost = (v: number) => `$${v.toFixed(2)}`

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[6],
      }}
      className="dashboard-charts-grid"
    >
      <ChartContainer
        title="Request Volume"
        subtitle="Audit log entries over time"
        loading={loading}
      >
        <LineChart
          data={chartRequests || []}
          color={theme.chart.series1}
          formatValue={(v) => v.toLocaleString()}
        />
      </ChartContainer>

      <ChartContainer
        title="System Errors"
        subtitle="Error count over time"
        loading={loading}
      >
        <BarChart
          data={chartErrors || []}
          color={theme.chart.series3}
          formatValue={(v) => v.toLocaleString()}
        />
      </ChartContainer>

      <ChartContainer
        title="AI Cost"
        subtitle="Estimated cost per day"
        loading={loading}
      >
        <LineChart
          data={chartAiCost || []}
          color={theme.chart.series5}
          formatValue={formatCost}
        />
      </ChartContainer>

      <div
        style={{
          backgroundColor: theme.colors.surface,
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.md,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '200px',
          gap: theme.spacing[3],
        }}
      >
        <div
          style={{
            fontSize: theme.typography.sizes.body,
            fontWeight: theme.typography.weights.medium,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          More charts coming soon
        </div>
        <div
          style={{
            fontSize: theme.typography.sizes.caption,
            color: theme.colors.textTertiary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          PROC-SPEC-2.4
        </div>
      </div>
    </div>
  )
}
