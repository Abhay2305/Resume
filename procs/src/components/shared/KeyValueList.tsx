import { theme } from '../../styles/theme'

interface KeyValueItem {
  key: string
  value: React.ReactNode
  icon?: React.ReactNode
}

interface KeyValueListProps {
  items: KeyValueItem[]
  columns?: 1 | 2 | 3
  testId?: string
}

export default function KeyValueList({ items, columns = 2, testId }: KeyValueListProps) {
  return (
    <div
      data-testid={testId}
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: `${theme.spacing[4]} ${theme.spacing[6]}`,
      }}
    >
      {items.map((item) => (
        <div key={item.key} style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[1] }}>
          <span
            style={{
              fontSize: theme.typography.sizes.caption,
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.textTertiary,
              fontFamily: theme.typography.fontFamily,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            {item.key}
          </span>
          <span
            style={{
              fontSize: theme.typography.sizes.body,
              color: theme.colors.text,
              fontFamily: theme.typography.fontFamily,
              display: 'flex',
              alignItems: 'center',
              gap: theme.spacing[2],
              wordBreak: 'break-word',
            }}
          >
            {item.icon && <span style={{ flexShrink: 0, display: 'inline-flex' }}>{item.icon}</span>}
            {item.value ?? '—'}
          </span>
        </div>
      ))}
    </div>
  )
}
