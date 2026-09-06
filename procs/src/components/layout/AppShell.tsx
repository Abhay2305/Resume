import { useState, useCallback } from 'react'
import { theme } from '../../styles/theme'
import { useResponsive } from '../../hooks/useResponsive'
import Sidebar from './Sidebar'
import Header from './Header'
import ContentArea from './ContentArea'

interface AppShellProps {
  children: React.ReactNode
  isCollapsed: boolean
  toggleSidebar: () => void
}

export default function AppShell({ children, isCollapsed, toggleSidebar }: AppShellProps) {
  const { isTablet } = useResponsive()
  const [isOverlayOpen, setIsOverlayOpen] = useState(false)

  const handleOverlayClose = useCallback(() => {
    setIsOverlayOpen(false)
  }, [])

  const handleOverlayToggle = useCallback(() => {
    setIsOverlayOpen((prev) => !prev)
  }, [])

  const sidebarToggle = isTablet ? handleOverlayToggle : toggleSidebar

  return (
    <div
      style={{
        display: 'flex',
        minHeight: '100vh',
        backgroundColor: theme.colors.background,
      }}
    >
      <Sidebar
        isCollapsed={isCollapsed}
        isOverlayOpen={isOverlayOpen}
        onToggle={sidebarToggle}
        onOverlayClose={handleOverlayClose}
      />

      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          marginLeft: isOverlayOpen ? 0 : isCollapsed ? theme.layout.sidebarCollapsed : theme.layout.sidebarWidth,
          transition: isOverlayOpen ? 'none' : 'margin-left 200ms ease-in-out',
          minWidth: 0,
        }}
      >
        <Header onSidebarToggle={sidebarToggle} isTablet={isTablet} />
        <ContentArea isOverlay={isOverlayOpen}>
          {children}
        </ContentArea>
      </div>
    </div>
  )
}
