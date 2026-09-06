import { useNavigate } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { theme } from '../../styles/theme'

interface Breadcrumb {
  label: string
  href?: string
}

interface InspectorPanelProps {
  title: string
  subtitle?: string
  icon?: React.ReactNode
  actions?: React.ReactNode
  breadcrumbs?: Breadcrumb[]
  headerRight?: React.ReactNode
  children: React.ReactNode
  testId?: string
}

export default function InspectorPanel({
  title,
  subtitle,
  icon,
  actions,
  breadcrumbs,
  headerRight,
  children,
  testId,
}: InspectorPanelProps) {
  const navigate = useNavigate()

  return (
    <div data-testid={testId} style={{ padding: theme.layout.pagePadding }}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav
          aria-label="Breadcrumb"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[2],
            marginBottom: theme.spacing[4],
            fontSize: theme.typography.sizes.bodySmall,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          {breadcrumbs.map((crumb, i) => {
            const isLast = i === breadcrumbs.length - 1
            return (
              <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: theme.spacing[2] }}>
                {i > 0 && <ChevronRight size={14} color={theme.colors.textTertiary} />}
                {crumb.href && !isLast ? (
                  <button
                    onClick={() => navigate(crumb.href!)}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      color: theme.colors.primary,
                      cursor: 'pointer',
                      fontSize: 'inherit',
                      fontFamily: 'inherit',
                      textDecoration: 'none',
                    }}
                  >
                    {crumb.label}
                  </button>
                ) : (
                  <span style={{ color: isLast ? theme.colors.text : theme.colors.textSecondary }}>
                    {crumb.label}
                  </span>
                )}
              </span>
            )
          })}
        </nav>
      )}

      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: theme.spacing[6],
          gap: theme.spacing[4],
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[4], flex: 1, minWidth: 0 }}>
          {icon && <div style={{ flexShrink: 0 }}>{icon}</div>}
          <div style={{ minWidth: 0 }}>
            <h1
              style={{
                margin: 0,
                fontSize: theme.typography.sizes.h1,
                fontWeight: theme.typography.weights.bold,
                color: theme.colors.text,
                fontFamily: theme.typography.fontFamily,
                lineHeight: 1.2,
              }}
            >
              {title}
            </h1>
            {subtitle && (
              <p
                style={{
                  margin: 0,
                  marginTop: theme.spacing[1],
                  fontSize: theme.typography.sizes.bodySmall,
                  color: theme.colors.textSecondary,
                  fontFamily: theme.typography.fontFamily,
                }}
              >
                {subtitle}
              </p>
            )}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[3], flexShrink: 0 }}>
          {headerRight}
          {actions}
        </div>
      </div>

      {children}
    </div>
  )
}
