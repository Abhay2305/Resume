import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { theme } from '../../styles/theme'
import Skeleton from './Skeleton'

interface MetricCardProps {
  title: string
  value: string | number
  trend?: number
  trendLabel?: string
  subtitle?: string
  icon?: React.ReactNode
  loading?: boolean
  error?: string
  size?: 'sm' | 'md' | 'lg'
  testId?: string
}

const sizeConfig = {
  sm: { valueSize: theme.typography.sizes.h2, padding: `${theme.spacing[3]} ${theme.spacing[4]}` },
  md: { valueSize: theme.typography.sizes.h1, padding: `${theme.spacing[4]} ${theme.spacing[5]}` },
  lg: { valueSize: theme.typography.sizes.display, padding: `${theme.spacing[5]} ${theme.spacing[6]}` },
}

export default function MetricCard({
  title,
  value,
  trend,
  trendLabel,
  subtitle,
  icon,
  loading = false,
  error,
  size = 'md',
  testId,
}: MetricCardProps) {
  const config = sizeConfig[size]

  if (loading) {
    return (
      <div
        data-testid={testId}
        style={{
          padding: config.padding,
          backgroundColor: theme.colors.surface,
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.md,
        }}
      >
        <Skeleton variant="text" width="40%" height="14px" />
        <div style={{ marginTop: theme.spacing[2] }}>
          <Skeleton variant="heading" width="50%" height="28px" />
        </div>
        <div style={{ marginTop: theme.spacing[1] }}>
          <Skeleton variant="text" width="60%" height="12px" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div
        data-testid={testId}
        style={{
          padding: config.padding,
          backgroundColor: theme.colors.dangerBg,
          border: `1px solid ${theme.colors.danger}30`,
          borderRadius: theme.borderRadius.md,
        }}
      >
        <div
          style={{
            fontSize: theme.typography.sizes.body,
            color: theme.colors.danger,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          {error}
        </div>
      </div>
    )
  }

  const trendColor =
    trend === undefined || trend === 0
      ? theme.colors.textTertiary
      : trend > 0
        ? theme.colors.success
        : theme.colors.danger

  const TrendIcon =
    trend === undefined || trend === 0 ? Minus : trend > 0 ? TrendingUp : TrendingDown

  return (
    <div
      data-testid={testId}
      style={{
        padding: config.padding,
        backgroundColor: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md,
        transition: 'box-shadow 150ms',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span
          style={{
            fontSize: theme.typography.sizes.bodySmall,
            fontWeight: theme.typography.weights.medium,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          {title}
        </span>
        {icon && (
          <span style={{ color: theme.colors.textTertiary, display: 'inline-flex' }}>{icon}</span>
        )}
      </div>
      <div
        style={{
          marginTop: theme.spacing[2],
          display: 'flex',
          alignItems: 'baseline',
          gap: theme.spacing[2],
        }}
      >
        <span
          style={{
            fontSize: config.valueSize,
            fontWeight: theme.typography.weights.bold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {trend !== undefined && (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px',
              fontSize: theme.typography.sizes.caption,
              fontWeight: theme.typography.weights.medium,
              color: trendColor,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            <TrendIcon size={14} />
            {trend > 0 ? '+' : ''}
            {trend}%
          </span>
        )}
      </div>
      {(subtitle || trendLabel) && (
        <div
          style={{
            marginTop: theme.spacing[1],
            fontSize: theme.typography.sizes.caption,
            color: theme.colors.textTertiary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          {subtitle || trendLabel}
        </div>
      )}
    </div>
  )
}
