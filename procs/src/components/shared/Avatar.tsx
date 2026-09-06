import { theme } from '../../styles/theme'

interface AvatarProps {
  src?: string
  alt?: string
  name?: string
  size?: number
  testId?: string
}

const AVATAR_COLORS = [
  '#7BC4BE', '#F6B233', '#3B82F6', '#10B981',
  '#EF4444', '#8B5CF6', '#EC4899', '#F97316',
]

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

function getColorFromName(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
}

export default function Avatar({ src, alt, name = '', size = 32, testId }: AvatarProps) {
  const initials = getInitials(name)
  const bgColor = getColorFromName(name)

  return (
    <div
      data-testid={testId}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',
        overflow: 'hidden',
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: bgColor,
        color: '#FFFFFF',
        fontSize: `${Math.round(size * 0.375)}px`,
        fontWeight: theme.typography.weights.semibold,
        fontFamily: theme.typography.fontFamily,
        lineHeight: 1,
      }}
    >
      {src ? (
        <img
          src={src}
          alt={alt || name}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      ) : (
        initials
      )}
    </div>
  )
}
