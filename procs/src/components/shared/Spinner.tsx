import { theme } from '../../styles/theme'

const spinKeyframes = `
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
`

function injectStyles() {
  if (typeof document !== 'undefined' && !document.getElementById('spinner-styles')) {
    const style = document.createElement('style')
    style.id = 'spinner-styles'
    style.textContent = spinKeyframes
    document.head.appendChild(style)
  }
}

interface SpinnerProps {
  size?: number
  color?: string
  label?: string
  testId?: string
}

export default function Spinner({
  size = 20,
  color = theme.colors.primary,
  label,
  testId,
}: SpinnerProps) {
  injectStyles()

  return (
    <svg
      data-testid={testId}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      role={label ? 'status' : 'presentation'}
      aria-label={label}
      style={{ animation: 'spin 1s linear infinite' }}
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke={theme.colors.border}
        strokeWidth="3"
        fill="none"
      />
      <path
        d="M12 2a10 10 0 0 1 10 10"
        stroke={color}
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
      />
    </svg>
  )
}
