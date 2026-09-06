import { type ButtonHTMLAttributes, type ReactNode } from 'react'
import { Loader2 } from 'lucide-react'
import { theme } from '../../styles/theme'

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost'
type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  icon?: ReactNode
  iconPosition?: 'left' | 'right'
  fullWidth?: boolean
  testId?: string
}

const variantStyles: Record<ButtonVariant, React.CSSProperties> = {
  primary: {
    backgroundColor: theme.colors.primary,
    color: theme.colors.textInverse,
    border: 'none',
  },
  secondary: {
    backgroundColor: 'transparent',
    color: theme.colors.primary,
    border: `1px solid ${theme.colors.primary}`,
  },
  danger: {
    backgroundColor: theme.colors.danger,
    color: theme.colors.textInverse,
    border: 'none',
  },
  ghost: {
    backgroundColor: 'transparent',
    color: theme.colors.text,
    border: 'none',
  },
}

const sizeStyles: Record<ButtonSize, React.CSSProperties> = {
  sm: {
    height: '32px',
    padding: '6px 12px',
    fontSize: theme.typography.sizes.bodySmall,
  },
  md: {
    height: '36px',
    padding: '8px 16px',
    fontSize: theme.typography.sizes.body,
  },
  lg: {
    height: '40px',
    padding: '10px 20px',
    fontSize: theme.typography.sizes.body,
  },
}

export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  fullWidth = false,
  disabled,
  testId,
  children,
  style,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || loading

  return (
    <button
      data-testid={testId}
      disabled={isDisabled}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: theme.spacing[2],
        fontWeight: theme.typography.weights.semibold,
        borderRadius: theme.borderRadius.md,
        cursor: isDisabled ? 'not-allowed' : 'pointer',
        opacity: isDisabled ? 0.5 : 1,
        transition: 'background-color 150ms, opacity 150ms',
        fontFamily: theme.typography.fontFamily,
        width: fullWidth ? '100%' : undefined,
        ...variantStyles[variant],
        ...sizeStyles[size],
        ...style,
      }}
      {...rest}
    >
      {loading ? (
        <Loader2 size={size === 'sm' ? 14 : 16} style={{ animation: 'spin 1s linear infinite' }} />
      ) : (
        icon && <span style={{ display: 'inline-flex', flexShrink: 0 }}>{icon}</span>
      )}
      {children && <span>{children}</span>}
    </button>
  )
}
