import { theme } from '../../styles/theme'

type SkeletonVariant = 'text' | 'heading' | 'avatar' | 'card' | 'table' | 'chart' | 'custom'

interface SkeletonProps {
  variant?: SkeletonVariant
  width?: string | number
  height?: string | number
  lines?: number
  animated?: boolean
  testId?: string
}

const shimmerKeyframes = `
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
`

function injectStyles() {
  if (typeof document !== 'undefined' && !document.getElementById('skeleton-styles')) {
    const style = document.createElement('style')
    style.id = 'skeleton-styles'
    style.textContent = shimmerKeyframes
    document.head.appendChild(style)
  }
}

const variantDefaults: Record<SkeletonVariant, { width: string; height: string }> = {
  text: { width: '100%', height: '16px' },
  heading: { width: '60%', height: '24px' },
  avatar: { width: '40px', height: '40px' },
  card: { width: '100%', height: '120px' },
  table: { width: '100%', height: '48px' },
  chart: { width: '100%', height: '300px' },
  custom: { width: '100%', height: '40px' },
}

export default function Skeleton({
  variant = 'text',
  width,
  height,
  lines = 1,
  animated = true,
  testId,
}: SkeletonProps) {
  injectStyles()

  const defaults = variantDefaults[variant]
  const w = width || defaults.width
  const h = height || defaults.height

  const baseStyle: React.CSSProperties = {
    width: w,
    height: h,
    backgroundColor: theme.colors.border,
    borderRadius: variant === 'avatar' ? '50%' : theme.borderRadius.sm,
    backgroundImage: animated
      ? 'linear-gradient(90deg, transparent 25%, rgba(255,255,255,0.4) 50%, transparent 75%)'
      : undefined,
    backgroundSize: animated ? '200% 100%' : undefined,
    animation: animated ? 'shimmer 1.5s ease-in-out infinite' : undefined,
  }

  if (variant === 'text' && lines > 1) {
    return (
      <div data-testid={testId} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            style={{
              ...baseStyle,
              width: i === lines - 1 ? '70%' : '100%',
            }}
          />
        ))}
      </div>
    )
  }

  return <div data-testid={testId} style={baseStyle} />
}
