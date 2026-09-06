import { theme } from '../../styles/theme'

interface SwitchProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  size?: 'sm' | 'md'
  testId?: string
}

const sizeMap = {
  sm: { track: '32px', knob: '16px', translate: '16px' },
  md: { track: '40px', knob: '20px', translate: '20px' },
}

export default function Switch({
  checked,
  onChange,
  disabled = false,
  size = 'md',
  testId,
}: SwitchProps) {
  const s = sizeMap[size]

  return (
    <button
      data-testid={testId}
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      style={{
        position: 'relative',
        width: s.track,
        height: s.knob,
        borderRadius: theme.borderRadius.full,
        border: 'none',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        backgroundColor: checked ? theme.colors.primary : theme.colors.borderStrong,
        transition: `background-color ${theme.transitions.fast}`,
        padding: 0,
        flexShrink: 0,
      }}
    >
      <span
        style={{
          position: 'absolute',
          top: '2px',
          left: checked ? `calc(100% - ${s.knob})` : '2px',
          width: `calc(${s.knob} - 4px)`,
          height: `calc(${s.knob} - 4px)`,
          borderRadius: '50%',
          backgroundColor: theme.colors.surface,
          boxShadow: theme.shadows.sm,
          transition: `left ${theme.transitions.fast}`,
          pointerEvents: 'none',
        }}
      />
    </button>
  )
}
