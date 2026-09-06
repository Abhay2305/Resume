import { theme } from '../../styles/theme'
import NavItem from './NavItem'
import type { NavGroupConfig } from '../../config/navigation'

interface NavGroupProps {
  group: NavGroupConfig
  activeRoute: string
  isCollapsed: boolean
}

export default function NavGroup({ group, activeRoute, isCollapsed }: NavGroupProps) {
  return (
    <div style={{ marginBottom: theme.spacing[1] }}>
      {!isCollapsed && (
        <div
          style={{
            fontSize: theme.typography.sizes.tiny,
            fontWeight: theme.typography.weights.semibold,
            color: theme.colors.textTertiary,
            letterSpacing: '0.05em',
            padding: `${theme.spacing[2]} ${theme.spacing[2]} ${theme.spacing[1]}`,
            lineHeight: theme.typography.lineHeights.heading,
          }}
        >
          {group.label}
        </div>
      )}
      <div role="group" aria-label={group.label}>
        {group.items.map((item) => (
          <NavItem
            key={item.id}
            icon={item.icon}
            label={item.label}
            route={item.route}
            isActive={
              item.route === '/'
                ? activeRoute === '/'
                : activeRoute.startsWith(item.route)
            }
            isCollapsed={isCollapsed}
          />
        ))}
      </div>
    </div>
  )
}
