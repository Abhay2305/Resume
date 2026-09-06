import { Inbox } from 'lucide-react'
import { theme } from '../../styles/theme'
import Button from './Button'

interface EmptyStateProps {
  icon?: React.ComponentType<{ size?: number; color?: string }>
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  testId?: string
}

export default function EmptyState({
  icon: IconProp,
  title,
  description,
  action,
  testId,
}: EmptyStateProps) {
  const Icon = IconProp || Inbox

  return (
    <div
      data-testid={testId}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: `${theme.spacing[10]} ${theme.spacing[6]}`,
        textAlign: 'center',
      }}
    >
      <Icon size={48} color={theme.colors.textTertiary} style={{ marginBottom: theme.spacing[4] }} />
      <h3
        style={{
          margin: 0,
          fontSize: theme.typography.sizes.h3,
          fontWeight: theme.typography.weights.semibold,
          color: theme.colors.text,
          fontFamily: theme.typography.fontFamily,
        }}
      >
        {title}
      </h3>
      {description && (
        <p
          style={{
            margin: 0,
            marginTop: theme.spacing[2],
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
            maxWidth: '400px',
          }}
        >
          {description}
        </p>
      )}
      {action && (
        <div style={{ marginTop: theme.spacing[5] }}>
          <Button variant="primary" onClick={action.onClick}>
            {action.label}
          </Button>
        </div>
      )}
    </div>
  )
}
