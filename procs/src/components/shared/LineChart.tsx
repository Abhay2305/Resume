import { useState, useRef, useCallback } from 'react'
import { theme } from '../../styles/theme'

interface DataPoint {
  label: string
  value: number
}

interface LineChartProps {
  data: DataPoint[]
  color?: string
  height?: number
  showDots?: boolean
  showGrid?: boolean
  formatValue?: (value: number) => string
}

const PADDING = { top: 16, right: 16, bottom: 32, left: 56 }
const CHART_W = 500

export default function LineChart({
  data,
  color = theme.chart.series1,
  height = 180,
  showDots = true,
  showGrid = true,
  formatValue,
}: LineChartProps) {
  const [tooltip, setTooltip] = useState<{ x: number; y: number; value: number; label: string } | null>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  const formatVal = formatValue || ((v: number) => v.toLocaleString())

  const safeData = data ?? []

  const values = safeData.map((d) => d.value)
  const maxVal = Math.max(...values, 1)
  const minVal = 0
  const range = maxVal - minVal || 1

  const chartH = height - PADDING.top - PADDING.bottom

  const points = safeData.length > 0
    ? safeData.map((d, i) => ({
        x: PADDING.left + (i / Math.max(safeData.length - 1, 1)) * (CHART_W - PADDING.left - PADDING.right),
        y: PADDING.top + (1 - (d.value - minVal) / range) * chartH,
        value: d.value,
        label: d.label,
      }))
    : []

  const pathD = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ')

  const lastPoint = points.length > 0 ? points[points.length - 1] : null
  const firstPoint = points.length > 0 ? points[0] : null
  const areaD = lastPoint && firstPoint
    ? `${pathD} L ${lastPoint.x} ${PADDING.top + chartH} L ${firstPoint.x} ${PADDING.top + chartH} Z`
    : ''

  const gridLines = 4
  const gridValues = Array.from({ length: gridLines + 1 }, (_, i) => minVal + (range * i) / gridLines)

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<SVGSVGElement>) => {
      const svg = svgRef.current
      if (!svg || points.length === 0) return
      const rect = svg.getBoundingClientRect()
      const scaleX = CHART_W / rect.width
      const mouseX = (e.clientX - rect.left) * scaleX

      let closest = points[0]
      let minDist = Math.abs(mouseX - closest.x)
      for (const p of points) {
        const dist = Math.abs(mouseX - p.x)
        if (dist < minDist) {
          minDist = dist
          closest = p
        }
      }

      setTooltip({
        x: closest.x,
        y: closest.y,
        value: closest.value,
        label: closest.label,
      })
    },
    [points],
  )

  const handleMouseLeave = useCallback(() => setTooltip(null), [])

  if (safeData.length === 0) {
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

  return (
    <div style={{ width: '100%', overflow: 'hidden' }}>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${CHART_W} ${height}`}
        width="100%"
        height={height}
        style={{ display: 'block' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        role="img"
        aria-label="Line chart"
      >
        {showGrid && gridValues.map((val, i) => {
          const y = PADDING.top + (1 - (val - minVal) / range) * chartH
          return (
            <g key={i}>
              <line
                x1={PADDING.left}
                y1={y}
                x2={CHART_W - PADDING.right}
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

        <defs>
          <linearGradient id={`gradient-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.15} />
            <stop offset="100%" stopColor={color} stopOpacity={0.01} />
          </linearGradient>
        </defs>

        <path d={areaD} fill={`url(#gradient-${color.replace('#', '')})`} />

        <path d={pathD} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />

        {showDots && points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r={3}
            fill={theme.colors.surface}
            stroke={color}
            strokeWidth={2}
          />
        ))}

        {tooltip && (
          <g>
            <line
              x1={tooltip.x}
              y1={PADDING.top}
              x2={tooltip.x}
              y2={PADDING.top + chartH}
              stroke={theme.colors.textTertiary}
              strokeWidth={1}
              strokeDasharray="4 4"
            />
            <circle cx={tooltip.x} cy={tooltip.y} r={5} fill={color} stroke={theme.colors.surface} strokeWidth={2} />
            <rect
              x={tooltip.x - 40}
              y={tooltip.y - 28}
              width={80}
              height={20}
              rx={4}
              fill={theme.colors.text}
              opacity={0.9}
            />
            <text
              x={tooltip.x}
              y={tooltip.y - 14}
              textAnchor="middle"
              fill={theme.colors.textInverse}
              fontSize={theme.typography.sizes.caption}
              fontFamily={theme.typography.fontFamily}
              fontWeight={theme.typography.weights.medium}
            >
              {formatVal(tooltip.value)}
            </text>
          </g>
        )}

        {safeData.length <= 7 && points.map((p, i) => (
          <text
            key={i}
            x={p.x}
            y={PADDING.top + chartH + 16}
            textAnchor="middle"
            fill={theme.colors.textTertiary}
            fontSize={theme.typography.sizes.tiny}
            fontFamily={theme.typography.fontFamily}
          >
            {safeData[i].label.length > 5 ? safeData[i].label.slice(5, 10) : safeData[i].label}
          </text>
        ))}
      </svg>
    </div>
  )
}
