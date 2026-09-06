import { FileText, Mail, Cpu, TrendingUp } from 'lucide-react'
import { theme } from '../../styles/theme'
import { MetricCard, ChartContainer, BarChart, Alert } from '../../components/shared'
import { useFeatureUsage } from './hooks/useFeatureUsage'

const PERIODS = [
  { label: '7d', value: '7d' },
  { label: '30d', value: '30d' },
  { label: '90d', value: '90d' },
]

const FEATURE_ICONS: Record<string, typeof FileText> = {
  'Resumes Created': FileText,
  'Cover Letters Generated': Mail,
  'AI Requests': Cpu,
}

const FEATURE_COLORS: Record<string, string> = {
  'Resumes Created': theme.colors.primary,
  'Cover Letters Generated': theme.colors.info,
  'AI Requests': theme.colors.warning,
}

export default function FeatureUsage() {
  const { data, period, setPeriod, loading, error } = useFeatureUsage()

  const barData = data?.items.map((item) => ({
    label: item.name.replace(' Created', '').replace(' Generated', ''),
    value: item.count,
  })) ?? []

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: theme.spacing[5] }}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: theme.typography.sizes.h1,
            fontWeight: theme.typography.weights.bold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
          }}>
            Feature Usage
          </h1>
          <p style={{
            margin: 0,
            marginTop: theme.spacing[1],
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}>
            Track feature adoption and usage trends
          </p>
        </div>
        <div style={{ display: 'flex', gap: theme.spacing[2] }}>
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              style={{
                padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
                fontSize: theme.typography.sizes.bodySmall,
                fontWeight: period === p.value ? theme.typography.weights.semibold : theme.typography.weights.medium,
                color: period === p.value ? theme.colors.surface : theme.colors.textSecondary,
                backgroundColor: period === p.value ? theme.colors.primary : theme.colors.surface,
                border: `1px solid ${period === p.value ? theme.colors.primary : theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                cursor: 'pointer',
                fontFamily: theme.typography.fontFamily,
              }}
            >
              {p.label === '7d' ? '7 Days' : p.label === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div style={{ marginBottom: theme.spacing[4] }}>
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <MetricCard
          title="Total Usage"
          value={data?.total ?? 0}
          icon={<TrendingUp size={20} color={theme.colors.primary} />}
          loading={loading}
        />
        {data?.items.map((item) => {
          const Icon = FEATURE_ICONS[item.name] || FileText
          const color = FEATURE_COLORS[item.name] || theme.colors.textSecondary
          return (
            <MetricCard
              key={item.name}
              title={item.name}
              value={item.count}
              trend={item.trend}
              icon={<Icon size={20} color={color} />}
              loading={loading}
            />
          )
        })}
      </div>

      <ChartContainer
        title="Feature Usage Breakdown"
        subtitle={`Usage counts for ${period === '7d' ? '7 days' : period === '30d' ? '30 days' : '90 days'}`}
        loading={loading}
      >
        <BarChart data={barData} color={theme.colors.primary} />
      </ChartContainer>

      {!loading && data?.items && data.items.length > 0 && (
        <div style={{
          marginTop: theme.spacing[5],
          backgroundColor: theme.colors.surface,
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.md,
          overflow: 'hidden',
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: theme.typography.fontFamily }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${theme.colors.border}`, backgroundColor: theme.colors.neutralBg }}>
                <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'left', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>Feature</th>
                <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'right', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>Count</th>
                <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'right', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>Trend</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.name} style={{ borderBottom: `1px solid ${theme.colors.divider}` }}>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, fontSize: theme.typography.sizes.body, color: theme.colors.text, fontWeight: theme.typography.weights.medium }}>
                    {item.name}
                  </td>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'right', fontSize: theme.typography.sizes.body, color: theme.colors.text, fontVariantNumeric: 'tabular-nums' }}>
                    {item.count.toLocaleString()}
                  </td>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'right', fontSize: theme.typography.sizes.body }}>
                    <span style={{
                      color: item.trend > 0 ? theme.colors.success : item.trend < 0 ? theme.colors.danger : theme.colors.textTertiary,
                      fontWeight: theme.typography.weights.medium,
                    }}>
                      {item.trend > 0 ? '+' : ''}{item.trend}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
