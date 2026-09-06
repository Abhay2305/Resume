import { Menu, Search, Bell } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { theme } from '../../styles/theme'
import Breadcrumb from './Breadcrumb'

interface HeaderProps {
  onSidebarToggle: () => void
  isTablet: boolean
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

export default function Header({ onSidebarToggle, isTablet }: HeaderProps) {
  const { admin } = useAuth()

  return (
    <header
      style={{
        height: theme.layout.headerHeight,
        backgroundColor: theme.colors.surface,
        borderBottom: `1px solid ${theme.colors.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: `0 ${theme.spacing[6]}`,
        flexShrink: 0,
        position: 'sticky',
        top: 0,
        zIndex: 20,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing[3],
          minWidth: 0,
        }}
      >
        {isTablet && (
          <button
            onClick={onSidebarToggle}
            aria-label="Open navigation"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '32px',
              height: '32px',
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.sm,
              backgroundColor: theme.colors.surface,
              color: theme.colors.textSecondary,
              cursor: 'pointer',
              outline: 'none',
              flexShrink: 0,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.surfaceHover
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.surface
            }}
            onFocus={(e) => {
              e.currentTarget.style.boxShadow = `0 0 0 2px ${theme.colors.primary}40`
            }}
            onBlur={(e) => {
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <Menu size={20} />
          </button>
        )}
        <Breadcrumb />
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing[4],
          flexShrink: 0,
        }}
      >
        <button
          aria-label="Search"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[2],
            padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.surface,
            color: theme.colors.textTertiary,
            cursor: 'pointer',
            fontSize: theme.typography.sizes.body,
            outline: 'none',
            minWidth: '160px',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = theme.colors.borderStrong
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = theme.colors.border
          }}
          onFocus={(e) => {
            e.currentTarget.style.boxShadow = `0 0 0 2px ${theme.colors.primary}40`
          }}
          onBlur={(e) => {
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          <Search size={16} />
          <span>Search...</span>
        </button>

        <button
          aria-label="Notifications"
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '32px',
            height: '32px',
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.sm,
            backgroundColor: theme.colors.surface,
            color: theme.colors.textSecondary,
            cursor: 'pointer',
            outline: 'none',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = theme.colors.surfaceHover
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = theme.colors.surface
          }}
          onFocus={(e) => {
            e.currentTarget.style.boxShadow = `0 0 0 2px ${theme.colors.primary}40`
          }}
          onBlur={(e) => {
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          <Bell size={18} />
          <span
            style={{
              position: 'absolute',
              top: '-2px',
              right: '-2px',
              width: '16px',
              height: '16px',
              borderRadius: theme.borderRadius.full,
              backgroundColor: theme.colors.textTertiary,
              color: theme.colors.textInverse,
              fontSize: '10px',
              fontWeight: theme.typography.weights.semibold,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            0
          </span>
        </button>

        {admin && (
          <div
            title={admin.full_name || admin.email}
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
              cursor: 'default',
              flexShrink: 0,
            }}
          >
            {getInitials(admin.full_name)}
          </div>
        )}
      </div>
    </header>
  )
}
