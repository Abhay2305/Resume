import { useState, useRef, useEffect, useCallback } from 'react'
import { MoreVertical } from 'lucide-react'
import { theme } from '../../styles/theme'

export interface ActionMenuItem {
  key: string
  label: string
  icon?: React.ReactNode
  onClick: () => void
  variant?: 'default' | 'danger'
  divider?: boolean
  disabled?: boolean
}

interface ActionMenuProps {
  items: ActionMenuItem[]
  trigger?: React.ReactNode
  align?: 'left' | 'right'
  minWidth?: number
}

export default function ActionMenu({ items, trigger, align = 'right', minWidth = 180 }: ActionMenuProps) {
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const containerRef = useRef<HTMLDivElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const itemRefs = useRef<(HTMLButtonElement | null)[]>([])

  const focusItem = useCallback((index: number) => {
    const clamped = Math.max(0, Math.min(index, items.length - 1))
    setActiveIndex(clamped)
    itemRefs.current[clamped]?.focus()
  }, [items.length])

  useEffect(() => {
    if (!open) return

    const handleClickOutside = (e: MouseEvent) => {
      if (
        (containerRef.current && !containerRef.current.contains(e.target as Node)) ||
        (menuRef.current && !menuRef.current.contains(e.target as Node))
      ) {
        setOpen(false)
      }
    }

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setOpen(false)
        triggerRef.current?.focus()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [open])

  useEffect(() => {
    if (open) {
      setActiveIndex(-1)
    }
  }, [open])

  const handleTriggerClick = () => {
    setOpen((prev) => !prev)
  }

  const handleItemAction = (item: ActionMenuItem) => {
    if (item.disabled) return
    item.onClick()
    setOpen(false)
  }

  const handleMenuKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        focusItem(activeIndex + 1)
        break
      case 'ArrowUp':
        e.preventDefault()
        focusItem(activeIndex - 1)
        break
      case 'Home':
        e.preventDefault()
        focusItem(0)
        break
      case 'End':
        e.preventDefault()
        focusItem(items.length - 1)
        break
      case 'Enter':
      case ' ':
        e.preventDefault()
        if (activeIndex >= 0 && activeIndex < items.length) {
          handleItemAction(items[activeIndex])
        }
        break
      case 'Tab':
        setOpen(false)
        break
    }
  }

  const defaultTrigger = (
    <button
      ref={triggerRef}
      type="button"
      onClick={handleTriggerClick}
      aria-label="Actions"
      aria-haspopup="true"
      aria-expanded={open}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '32px',
        height: '32px',
        padding: 0,
        border: 'none',
        borderRadius: theme.borderRadius.sm,
        backgroundColor: 'transparent',
        color: theme.colors.textTertiary,
        cursor: 'pointer',
        transition: `all ${theme.transitions.fast}`,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = theme.colors.surfaceHover
        e.currentTarget.style.color = theme.colors.text
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent'
        e.currentTarget.style.color = theme.colors.textTertiary
      }}
    >
      <MoreVertical size={16} />
    </button>
  )

  return (
    <div ref={containerRef} style={{ position: 'relative', display: 'inline-flex' }}>
      {trigger
        ? <div onClick={handleTriggerClick}>{trigger}</div>
        : defaultTrigger
      }

      {open && (
        <div
          ref={menuRef}
          role="menu"
          onKeyDown={handleMenuKeyDown}
          style={{
            position: 'absolute',
            [align]: 0,
            top: '100%',
            marginTop: '4px',
            minWidth: `${minWidth}px`,
            backgroundColor: theme.colors.surface,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            boxShadow: theme.shadows.lg,
            zIndex: theme.zIndex.dropdown,
            overflow: 'hidden',
            padding: '4px',
          }}
        >
          {items.map((item, index) => (
            <div key={item.key}>
              {item.divider && index > 0 && (
                <div
                  style={{
                    height: '1px',
                    backgroundColor: theme.colors.divider,
                    margin: '4px 0',
                  }}
                />
              )}
              <button
                ref={(el) => { itemRefs.current[index] = el }}
                type="button"
                role="menuitem"
                tabIndex={activeIndex === index ? 0 : -1}
                aria-disabled={item.disabled}
                onClick={() => handleItemAction(item)}
                onMouseEnter={() => setActiveIndex(index)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: theme.spacing[2],
                  width: '100%',
                  padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
                  border: 'none',
                  borderRadius: theme.borderRadius.sm,
                  backgroundColor: activeIndex === index
                    ? (item.variant === 'danger' ? theme.colors.dangerBg : theme.colors.surfaceHover)
                    : 'transparent',
                  color: item.variant === 'danger' ? theme.colors.danger : theme.colors.text,
                  fontSize: theme.typography.sizes.bodySmall,
                  fontWeight: theme.typography.weights.medium,
                  fontFamily: theme.typography.fontFamily,
                  cursor: item.disabled ? 'not-allowed' : 'pointer',
                  textAlign: 'left',
                  transition: `background-color ${theme.transitions.fast}`,
                  whiteSpace: 'nowrap',
                  opacity: item.disabled ? 0.5 : 1,
                }}
              >
                {item.icon && (
                  <span style={{ display: 'inline-flex', flexShrink: 0, color: item.variant === 'danger' ? theme.colors.danger : theme.colors.textTertiary }}>
                    {item.icon}
                  </span>
                )}
                {item.label}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
