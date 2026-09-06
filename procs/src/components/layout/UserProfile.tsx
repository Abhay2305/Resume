import { useAuth } from '../../context/AuthContext'
import { theme } from '../../styles/theme'

interface UserProfileProps {
  isCollapsed: boolean
}

function getInitials(name: string | null): string {
  if (!name) return '?'
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export default function UserProfile({ isCollapsed }: UserProfileProps) {
  const { admin, logout } = useAuth()

  if (!admin) return null

  return (
    <div
      style={{
        borderTop: `1px solid ${theme.colors.border}`,
        padding: isCollapsed ? theme.spacing[2] : `${theme.spacing[3]} ${theme.spacing[4]}`,
        display: 'flex',
        flexDirection: isCollapsed ? 'column' : 'row',
        alignItems: 'center',
        gap: isCollapsed ? 0 : theme.spacing[3],
        justifyContent: isCollapsed ? 'center' : 'space-between',
        minHeight: theme.layout.headerHeight,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing[3],
          overflow: 'hidden',
          minWidth: 0,
        }}
      >
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: theme.borderRadius.full,
            backgroundColor: theme.colors.primary,
            color: theme.colors.textInverse,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: theme.typography.sizes.caption,
            fontWeight: theme.typography.weights.semibold,
            flexShrink: 0,
          }}
        >
          {getInitials(admin.full_name)}
        </div>
        {!isCollapsed && (
          <div style={{ minWidth: 0 }}>
            <div
              style={{
                fontSize: theme.typography.sizes.body,
                fontWeight: theme.typography.weights.semibold,
                color: theme.colors.text,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {admin.full_name || 'Admin'}
            </div>
            <div
              style={{
                fontSize: theme.typography.sizes.caption,
                color: theme.colors.textTertiary,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {admin.email}
            </div>
          </div>
        )}
      </div>
      {!isCollapsed && (
        <button
          onClick={() => logout()}
          aria-label="Sign out"
          style={{
            fontSize: theme.typography.sizes.caption,
            color: theme.colors.textSecondary,
            backgroundColor: 'transparent',
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.sm,
            padding: `${theme.spacing[1]} ${theme.spacing[2]}`,
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            transition: 'background-color 150ms ease, color 150ms ease',
            outline: 'none',
            flexShrink: 0,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = theme.colors.dangerBg
            e.currentTarget.style.color = theme.colors.danger
            e.currentTarget.style.borderColor = theme.colors.danger
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent'
            e.currentTarget.style.color = theme.colors.textSecondary
            e.currentTarget.style.borderColor = theme.colors.border
          }}
          onFocus={(e) => {
            e.currentTarget.style.boxShadow = `0 0 0 2px ${theme.colors.primary}40`
          }}
          onBlur={(e) => {
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          Sign out
        </button>
      )}
    </div>
  )
}
