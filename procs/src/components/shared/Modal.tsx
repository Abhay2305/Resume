import { useEffect, useRef, useCallback } from 'react'
import { X } from 'lucide-react'
import { theme } from '../../styles/theme'

interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  description?: string
  size?: 'sm' | 'md' | 'lg'
  closable?: boolean
  children: React.ReactNode
  footer?: React.ReactNode
  testId?: string
}

const sizeMap: Record<string, string> = {
  sm: '480px',
  md: '640px',
  lg: '800px',
}

export default function Modal({
  open,
  onClose,
  title,
  description,
  size = 'md',
  closable = true,
  children,
  footer,
  testId,
}: ModalProps) {
  const contentRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && closable) {
        onClose()
      }
      if (e.key === 'Tab' && contentRef.current) {
        const focusable = contentRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
        )
        if (focusable.length === 0) return
        const first = focusable[0]
        const last = focusable[focusable.length - 1]
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault()
          last.focus()
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      }
    },
    [closable, onClose],
  )

  useEffect(() => {
    if (open) {
      previousFocusRef.current = document.activeElement as HTMLElement
      document.body.style.overflow = 'hidden'
      document.addEventListener('keydown', handleKeyDown)
      requestAnimationFrame(() => {
        contentRef.current?.querySelector<HTMLElement>('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')?.focus()
      })
    }
    return () => {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleKeyDown)
      previousFocusRef.current?.focus()
    }
  }, [open, handleKeyDown])

  if (!open) return null

  return (
    <div
      data-testid={testId}
      role="dialog"
      aria-modal="true"
      aria-label={title}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: theme.spacing[6],
      }}
    >
      <div
        onClick={closable ? onClose : undefined}
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
        }}
      />
      <div
        ref={contentRef}
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: sizeMap[size],
          maxHeight: 'calc(100vh - 48px)',
          backgroundColor: theme.colors.surface,
          borderRadius: theme.borderRadius.lg,
          boxShadow: theme.shadows.lg,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {(title || closable) && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: `${theme.spacing[4]} ${theme.spacing[6]}`,
              borderBottom: `1px solid ${theme.colors.border}`,
              flexShrink: 0,
            }}
          >
            <div>
              {title && (
                <h2
                  style={{
                    margin: 0,
                    fontSize: theme.typography.sizes.h3,
                    fontWeight: theme.typography.weights.semibold,
                    color: theme.colors.text,
                    fontFamily: theme.typography.fontFamily,
                  }}
                >
                  {title}
                </h2>
              )}
              {description && (
                <p
                  style={{
                    margin: 0,
                    marginTop: '2px',
                    fontSize: theme.typography.sizes.bodySmall,
                    color: theme.colors.textSecondary,
                    fontFamily: theme.typography.fontFamily,
                  }}
                >
                  {description}
                </p>
              )}
            </div>
            {closable && (
              <button
                onClick={onClose}
                aria-label="Close"
                style={{
                  padding: theme.spacing[1],
                  color: theme.colors.textTertiary,
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  borderRadius: theme.borderRadius.sm,
                }}
              >
                <X size={18} />
              </button>
            )}
          </div>
        )}
        <div
          style={{
            padding: theme.spacing[6],
            overflowY: 'auto',
            flex: 1,
          }}
        >
          {children}
        </div>
        {footer && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              gap: theme.spacing[3],
              padding: `${theme.spacing[4]} ${theme.spacing[6]}`,
              borderTop: `1px solid ${theme.colors.border}`,
              flexShrink: 0,
            }}
          >
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
