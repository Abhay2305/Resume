import { theme } from '../../../styles/theme'
import type { Period } from '../hooks/useDashboard'

interface DashboardHeaderProps {
  period: Period
  onPeriodChange: (period: Period) => void
}

const periods: Period[] = ['24h', '7d', '30d']

export default function DashboardHeader({ period, onPeriodChange }: DashboardHeaderProps) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: theme.spacing[6],
      }}
    >
      <div>
        <h1
          style={{
            fontSize: theme.typography.sizes.h1,
            fontWeight: theme.typography.weights.semibold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            margin: 0,
          }}
        >
          Dashboard
        </h1>
        <p
          style={{
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
            marginTop: theme.spacing[1],
          }}
        >
          System overview and key metrics
        </p>
      </div>

      <div
        style={{
          display: 'flex',
          gap: theme.spacing[1],
          padding: theme.spacing[1],
          backgroundColor: theme.colors.neutralBg,
          borderRadius: theme.borderRadius.md,
          border: `1px solid ${theme.colors.border}`,
        }}
      >
        {periods.map((p) => (
          <button
            key={p}
            onClick={() => onPeriodChange(p)}
            style={{
              padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
              fontFamily: theme.typography.fontFamily,
              color: period === p ? theme.colors.textInverse : theme.colors.textSecondary,
              backgroundColor: period === p ? theme.colors.primary : 'transparent',
              border: 'none',
              borderRadius: theme.borderRadius.sm,
              cursor: 'pointer',
              transition: theme.transitions.fast,
            }}
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  )
}
