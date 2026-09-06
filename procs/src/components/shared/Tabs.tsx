import { theme } from '../../styles/theme'

interface Tab {
  key: string
  label: string
  icon?: React.ReactNode
  count?: number
  disabled?: boolean
}

interface TabsProps {
  tabs: Tab[]
  activeKey: string
  onChange: (key: string) => void
  size?: 'sm' | 'md'
  testId?: string
}

export default function Tabs({ tabs, activeKey, onChange, size = 'md', testId }: TabsProps) {
  const fontSize = size === 'sm' ? theme.typography.sizes.bodySmall : theme.typography.sizes.body

  return (
    <div
      data-testid={testId}
      role="tablist"
      style={{
        display: 'flex',
        gap: 0,
        borderBottom: `1px solid ${theme.colors.border}`,
      }}
    >
      {tabs.map((tab) => {
        const isActive = tab.key === activeKey
        return (
          <button
            key={tab.key}
            role="tab"
            aria-selected={isActive}
            aria-disabled={tab.disabled}
            tabIndex={isActive ? 0 : -1}
            disabled={tab.disabled}
            onClick={() => !tab.disabled && onChange(tab.key)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: theme.spacing[2],
              padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
              fontSize,
              fontWeight: isActive ? theme.typography.weights.medium : theme.typography.weights.regular,
              fontFamily: theme.typography.fontFamily,
              color: isActive ? theme.colors.primary : theme.colors.textSecondary,
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: isActive ? `2px solid ${theme.colors.primary}` : '2px solid transparent',
              cursor: tab.disabled ? 'not-allowed' : 'pointer',
              opacity: tab.disabled ? 0.5 : 1,
              marginBottom: '-1px',
              transition: 'color 150ms, border-color 150ms',
            }}
          >
            {tab.icon && <span style={{ display: 'inline-flex' }}>{tab.icon}</span>}
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span
                style={{
                  padding: '1px 6px',
                  fontSize: theme.typography.sizes.tiny,
                  fontWeight: theme.typography.weights.medium,
                  color: isActive ? theme.colors.primary : theme.colors.textTertiary,
                  backgroundColor: isActive ? `${theme.colors.primary}10` : theme.colors.surfaceHover,
                  borderRadius: theme.borderRadius.full,
                }}
              >
                {tab.count}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
