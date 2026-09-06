import { theme } from '../../styles/theme'
import Skeleton from './Skeleton'

interface ChartContainerProps {
  title: string
  children: React.ReactNode
  height?: number
  loading?: boolean
  subtitle?: string
}

export default function ChartContainer({
  title,
  children,
  height = 220,
  loading = false,
  subtitle,
}: ChartContainerProps) {
  return (
    <div
      style={{
        backgroundColor: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
          borderBottom: `1px solid ${theme.colors.border}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <div
            style={{
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.textSecondary,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            {title}
          </div>
          {subtitle && (
            <div
              style={{
                fontSize: theme.typography.sizes.caption,
                color: theme.colors.textTertiary,
                fontFamily: theme.typography.fontFamily,
                marginTop: '2px',
              }}
            >
              {subtitle}
            </div>
          )}
        </div>
      </div>

      <div style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}` }}>
        {loading ? (
          <Skeleton variant="chart" width="100%" height={`${height}px`} />
        ) : (
          <div style={{ width: '100%', minHeight: `${height}px` }}>
            {children}
          </div>
        )}
      </div>
    </div>
  )
}
