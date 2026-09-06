import { useNavigate } from 'react-router-dom'
import { theme } from '../../styles/theme'
import type { LucideIcon } from 'lucide-react'

interface NavItemProps {
  icon: LucideIcon
  label: string
  route: string
  isActive: boolean
  isCollapsed: boolean
}

export default function NavItem({ icon: Icon, label, route, isActive, isCollapsed }: NavItemProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    navigate(route)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      navigate(route)
    }
  }

  return (
    <div
      role="menuitem"
      tabIndex={0}
      aria-current={isActive ? 'page' : undefined}
      title={isCollapsed ? label : undefined}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing[2],
        padding: `${theme.spacing[1]} ${theme.spacing[2]}`,
        paddingLeft: isCollapsed ? theme.spacing[2] : `calc(${theme.spacing[2]} + 3px)`,
        borderRadius: theme.borderRadius.md,
        cursor: 'pointer',
        backgroundColor: isActive
          ? `${theme.colors.primary}1A`
          : 'transparent',
        color: isActive ? theme.colors.primary : theme.colors.textSecondary,
        borderLeft: isActive ? `3px solid ${theme.colors.primary}` : '3px solid transparent',
        transition: 'background-color 150ms ease, color 150ms ease',
        fontSize: theme.typography.sizes.body,
        fontWeight: theme.typography.weights.medium,
        lineHeight: theme.typography.lineHeights.body,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        justifyContent: isCollapsed ? 'center' : 'flex-start',
        minHeight: '32px',
        outline: 'none',
      }}
      onMouseEnter={(e) => {
        if (!isActive) {
          e.currentTarget.style.backgroundColor = theme.colors.surfaceHover
        }
      }}
      onMouseLeave={(e) => {
        if (!isActive) {
          e.currentTarget.style.backgroundColor = 'transparent'
        }
      }}
      onFocus={(e) => {
        e.currentTarget.style.boxShadow = `0 0 0 2px ${theme.colors.primary}40`
      }}
      onBlur={(e) => {
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      <Icon size={20} strokeWidth={isActive ? 2.5 : 2} style={{ flexShrink: 0 }} />
      {!isCollapsed && <span>{label}</span>}
    </div>
  )
}
