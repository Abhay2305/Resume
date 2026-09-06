import { theme } from '../../styles/theme'

interface DataPoint {
  label: string
  value: number
}

interface BarChartProps {
  data: DataPoint[]
  color?: string
  height?: number
  formatValue?: (value: number) => string
}

const PADDING = { top: 16, right: 16, bottom: 32, left: 56 }

export default function BarChart({
  data,
  color = theme.chart.series2,
  height = 180,
  formatValue,
}: BarChartProps) {
  const formatVal = formatValue || ((v: number) => v.toLocaleString())

  if (data.length === 0) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: theme.colors.textTertiary,
          fontSize: theme.typography.sizes.bodySmall,
          fontFamily: theme.typography.fontFamily,
        }}
      >
        No data available
      </div>
    )
  }

  const values = data.map((d) => d.value)
  const maxVal = Math.max(...values, 1)
  const chartW = 500
  const chartH = height - PADDING.top - PADDING.bottom
  const barGap = 4
  const barW = Math.max(((chartW - PADDING.left - PADDING.right) / data.length) - barGap, 4)

  const gridLines = 4
  const gridValues = Array.from({ length: gridLines + 1 }, (_, i) => (maxVal * i) / gridLines)

  return (
    <svg
      viewBox={`0 0 ${chartW} ${height}`}
      width="100%"
      height={height}
      style={{ display: 'block' }}
      role="img"
      aria-label="Bar chart"
    >
      {gridValues.map((val, i) => {
        const y = PADDING.top + (1 - val / maxVal) * chartH
        return (
          <g key={i}>
            <line
              x1={PADDING.left}
              y1={y}
              x2={chartW - PADDING.right}
              y2={y}
              stroke={theme.colors.border}
              strokeWidth={1}
              strokeDasharray={i === 0 ? undefined : '4 4'}
            />
            <text
              x={PADDING.left - 8}
              y={y + 4}
              textAnchor="end"
              fill={theme.colors.textTertiary}
              fontSize={theme.typography.sizes.tiny}
              fontFamily={theme.typography.fontFamily}
            >
              {formatVal(val)}
            </text>
          </g>
        )
      })}

      {data.map((d, i) => {
        const x = PADDING.left + i * (barW + barGap) + barGap / 2
        const barH = (d.value / maxVal) * chartH
        const y = PADDING.top + chartH - barH
        return (
          <g key={i}>
            <rect
              x={x}
              y={y}
              width={barW}
              height={barH}
              fill={color}
              rx={2}
            />
            {data.length <= 7 && (
              <text
                x={x + barW / 2}
                y={PADDING.top + chartH + 16}
                textAnchor="middle"
                fill={theme.colors.textTertiary}
                fontSize={theme.typography.sizes.tiny}
                fontFamily={theme.typography.fontFamily}
              >
                {d.label.length > 5 ? d.label.slice(5, 10) : d.label}
              </text>
            )}
          </g>
        )
      })}
    </svg>
  )
}
