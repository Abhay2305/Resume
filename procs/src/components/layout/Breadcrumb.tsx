import { Link } from 'react-router-dom'
import { useBreadcrumb } from '../../hooks/useBreadcrumb'
import { theme } from '../../styles/theme'

export default function Breadcrumb() {
  const items = useBreadcrumb()

  return (
    <nav aria-label="Breadcrumb">
      <ol
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing[1],
          listStyle: 'none',
          margin: 0,
          padding: 0,
        }}
      >
        {items.map((item, index) => {
          const isLast = index === items.length - 1
          return (
            <li
              key={item.route + index}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: theme.spacing[1],
              }}
            >
              {index > 0 && (
                <span
                  style={{
                    color: theme.colors.textTertiary,
                    fontSize: theme.typography.sizes.body,
                    userSelect: 'none',
                  }}
                  aria-hidden="true"
                >
                  {'>'}
                </span>
              )}
              {isLast ? (
                <span
                  aria-current="page"
                  style={{
                    fontSize: theme.typography.sizes.body,
                    fontWeight: theme.typography.weights.semibold,
                    color: theme.colors.text,
                  }}
                >
                  {item.label}
                </span>
              ) : (
                <Link
                  to={item.route}
                  style={{
                    fontSize: theme.typography.sizes.body,
                    fontWeight: theme.typography.weights.regular,
                    color: theme.colors.textSecondary,
                    textDecoration: 'none',
                    transition: 'color 150ms ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = theme.colors.primary
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = theme.colors.textSecondary
                  }}
                >
                  {item.label}
                </Link>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
