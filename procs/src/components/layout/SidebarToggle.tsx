import { ChevronLeft, ChevronRight } from 'lucide-react'
import { theme } from '../../styles/theme'

interface SidebarToggleProps {
  isCollapsed: boolean
  onToggle: () => void
}

export default function SidebarToggle({ isCollapsed, onToggle }: SidebarToggleProps) {
  return (
    <button
      onClick={onToggle}
      aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      aria-expanded={!isCollapsed}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '28px',
        height: '28px',
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.sm,
        backgroundColor: theme.colors.surface,
        color: theme.colors.textSecondary,
        cursor: 'pointer',
        transition: 'background-color 150ms ease, color 150ms ease',
        outline: 'none',
        flexShrink: 0,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = theme.colors.surfaceHover
        e.currentTarget.style.color = theme.colors.text
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = theme.colors.surface
        e.currentTarget.style.color = theme.colors.textSecondary
      }}
      onFocus={(e) => {
        e.currentTarget.style.boxShadow = `0 0 0 2px ${theme.colors.primary}40`
      }}
      onBlur={(e) => {
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
    </button>
  )
}
