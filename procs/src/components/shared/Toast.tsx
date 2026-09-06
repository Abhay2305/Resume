import { useState, useEffect, useCallback, createContext, useContext, type ReactNode } from 'react'
import { X, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react'
import { theme } from '../../styles/theme'

export type ToastVariant = 'success' | 'error' | 'warning' | 'info'

export interface ToastMessage {
  id: string
  variant: ToastVariant
  title: string
  description?: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

interface ToastContextType {
  toast: (message: Omit<ToastMessage, 'id'>) => void
  dismiss: (id: string) => void
  dismissAll: () => void
}

const ToastContext = createContext<ToastContextType | null>(null)

const variantConfig: Record<ToastVariant, { icon: typeof CheckCircle; color: string; bg: string; border: string }> = {
  success: { icon: CheckCircle, color: theme.colors.success, bg: theme.colors.successBg, border: '#10B98130' },
  error: { icon: XCircle, color: theme.colors.danger, bg: theme.colors.dangerBg, border: '#EF444430' },
  warning: { icon: AlertTriangle, color: theme.colors.warning, bg: theme.colors.warningBg, border: '#F59E0B30' },
  info: { icon: Info, color: theme.colors.info, bg: theme.colors.infoBg, border: '#3B82F630' },
}

const defaultDurations: Record<ToastVariant, number> = {
  success: 3000,
  info: 3000,
  warning: 5000,
  error: 5000,
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const dismissAll = useCallback(() => {
    setToasts([])
  }, [])

  const toast = useCallback(
    (message: Omit<ToastMessage, 'id'>) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
      const newToast: ToastMessage = { ...message, id }
      setToasts((prev) => [...prev.slice(-2), newToast])

      const duration = message.duration ?? defaultDurations[message.variant]
      setTimeout(() => dismiss(id), duration)
    },
    [dismiss],
  )

  return (
    <ToastContext.Provider value={{ toast, dismiss, dismissAll }}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  )
}

export function useToast(): ToastContextType {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

function ToastContainer({
  toasts,
  onDismiss,
}: {
  toasts: ToastMessage[]
  onDismiss: (id: string) => void
}) {
  return (
    <div
      aria-live="polite"
      aria-label="Notifications"
      style={{
        position: 'fixed',
        bottom: theme.spacing[6],
        right: theme.spacing[6],
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing[2],
        zIndex: 9999,
        maxWidth: '400px',
        width: '100%',
        pointerEvents: 'none',
      }}
    >
      {toasts.map((t) => (
        <ToastItem key={t.id} message={t} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

function ToastItem({
  message,
  onDismiss,
}: {
  message: ToastMessage
  onDismiss: (id: string) => void
}) {
  const config = variantConfig[message.variant]
  const Icon = config.icon

  const [visible, setVisible] = useState(false)
  useEffect(() => {
    requestAnimationFrame(() => setVisible(true))
  }, [])

  return (
    <div
      role="status"
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: theme.spacing[3],
        padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
        backgroundColor: config.bg,
        border: `1px solid ${config.border}`,
        borderRadius: theme.borderRadius.md,
        boxShadow: theme.shadows.lg,
        pointerEvents: 'auto',
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateX(0)' : 'translateX(20px)',
        transition: 'opacity 200ms ease, transform 200ms ease',
      }}
    >
      <Icon size={18} color={config.color} style={{ flexShrink: 0, marginTop: '1px' }} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontWeight: theme.typography.weights.medium,
            fontSize: theme.typography.sizes.body,
            color: theme.colors.text,
          }}
        >
          {message.title}
        </div>
        {message.description && (
          <div
            style={{
              fontSize: theme.typography.sizes.bodySmall,
              color: theme.colors.textSecondary,
              marginTop: '2px',
            }}
          >
            {message.description}
          </div>
        )}
        {message.action && (
          <button
            onClick={message.action.onClick}
            style={{
              marginTop: theme.spacing[2],
              padding: 0,
              fontSize: theme.typography.sizes.bodySmall,
              fontWeight: theme.typography.weights.medium,
              color: config.color,
              backgroundColor: 'transparent',
              border: 'none',
              cursor: 'pointer',
              fontFamily: theme.typography.fontFamily,
            }}
          >
            {message.action.label}
          </button>
        )}
      </div>
      <button
        onClick={() => onDismiss(message.id)}
        aria-label="Dismiss"
        style={{
          padding: theme.spacing[1],
          color: theme.colors.textTertiary,
          backgroundColor: 'transparent',
          border: 'none',
          cursor: 'pointer',
          display: 'inline-flex',
          flexShrink: 0,
        }}
      >
        <X size={14} />
      </button>
    </div>
  )
}
