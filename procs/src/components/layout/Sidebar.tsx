import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { navigationConfig } from '../../config/navigation'
import { theme } from '../../styles/theme'
import SidebarToggle from './SidebarToggle'
import NavGroup from './NavGroup'
import UserProfile from './UserProfile'

interface SidebarProps {
  isCollapsed: boolean
  isOverlayOpen: boolean
  onToggle: () => void
  onOverlayClose: () => void
}

export default function Sidebar({ isCollapsed, isOverlayOpen, onToggle, onOverlayClose }: SidebarProps) {
  const location = useLocation()

  useEffect(() => {
    if (isOverlayOpen) {
      onOverlayClose()
    }
  }, [location.pathname, isOverlayOpen, onOverlayClose])

  useEffect(() => {
    if (!isOverlayOpen) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onOverlayClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOverlayOpen, onOverlayClose])

  const sidebarContent = (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        width: isOverlayOpen ? '280px' : isCollapsed ? theme.layout.sidebarCollapsed : theme.layout.sidebarWidth,
        backgroundColor: theme.colors.surface,
        borderRight: `1px solid ${theme.colors.border}`,
        transition: isOverlayOpen ? 'none' : 'width 200ms ease-in-out',
        overflow: 'hidden',
        flexShrink: 0,
      }}
    >
      <div
        style={{
          height: theme.layout.headerHeight,
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
          padding: isCollapsed ? 0 : `0 ${theme.spacing[4]}`,
          borderBottom: `1px solid ${theme.colors.border}`,
          flexShrink: 0,
        }}
      >
        {!isCollapsed && (
          <span
            style={{
              fontSize: theme.typography.sizes.h3,
              fontWeight: theme.typography.weights.bold,
              color: theme.colors.primary,
              letterSpacing: '-0.01em',
            }}
          >
            PROCS
          </span>
        )}
        {!isOverlayOpen && <SidebarToggle isCollapsed={isCollapsed} onToggle={onToggle} />}
      </div>

      <nav
        aria-label="Main navigation"
        style={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          padding: `${theme.spacing[2]} ${isCollapsed ? theme.spacing[1] : theme.spacing[2]}`,
        }}
      >
        {navigationConfig.map((group) => (
          <NavGroup
            key={group.id}
            group={group}
            activeRoute={location.pathname}
            isCollapsed={isCollapsed}
          />
        ))}
      </nav>

      <UserProfile isCollapsed={isCollapsed} />
    </div>
  )

  return (
    <>
      {isOverlayOpen && (
        <div
          onClick={onOverlayClose}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 40,
            transition: 'opacity 200ms ease-in-out',
          }}
          aria-hidden="true"
        />
      )}
      <aside
        role="dialog"
        aria-modal={isOverlayOpen ? 'true' : undefined}
        style={
          isOverlayOpen
            ? {
                position: 'fixed',
                top: 0,
                left: 0,
                bottom: 0,
                zIndex: 50,
                transition: 'transform 200ms ease-in-out',
              }
            : {
                position: 'fixed',
                top: 0,
                left: 0,
                bottom: 0,
                zIndex: 30,
              }
        }
      >
        {sidebarContent}
      </aside>
    </>
  )
}
