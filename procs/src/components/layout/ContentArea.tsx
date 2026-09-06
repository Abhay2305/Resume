import { theme } from '../../styles/theme'

interface ContentAreaProps {
  children: React.ReactNode
  isOverlay: boolean
}

export default function ContentArea({ children, isOverlay }: ContentAreaProps) {
  return (
    <main
      id="main-content"
      style={{
        flex: 1,
        overflowY: 'auto',
        overflowX: 'hidden',
        padding: theme.layout.pagePadding,
        backgroundColor: theme.colors.background,
        width: isOverlay ? '100%' : undefined,
        transition: isOverlay ? 'none' : 'width 200ms ease-in-out',
      }}
    >
      {children}
    </main>
  )
}
