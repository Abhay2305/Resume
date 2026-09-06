import { Activity, LogIn, LogOut, UserPlus, UserCog, UserMinus, FilePlus, FileEdit, FileMinus, ShieldAlert, Key } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import Skeleton from '../../../components/shared/Skeleton'
import Alert from '../../../components/shared/Alert'
import EmptyState from '../../../components/shared/EmptyState'
import Button from '../../../components/shared/Button'
import { theme } from '../../../styles/theme'
import { useUserTimeline } from '../hooks/useUserTimeline'
import type { UserTimelineEvent } from '../types'

const ICON_MAP: Record<string, LucideIcon> = {
  Activity,
  LogIn,
  LogOut,
  UserPlus,
  UserCog,
  UserMinus,
  FilePlus,
  FileEdit,
  FileMinus,
  ShieldAlert,
  Key,
}

const SEVERITY_COLORS: Record<string, string> = {
  info: theme.colors.info,
  warning: theme.colors.warning,
  danger: theme.colors.danger,
}

function TimelineItem({ event }: { event: UserTimelineEvent }) {
  const Icon = ICON_MAP[event.icon] || Activity
  const color = SEVERITY_COLORS[event.severity] || theme.colors.textTertiary

  return (
    <div
      style={{
        display: 'flex',
        gap: theme.spacing[3],
        padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
        borderBottom: `1px solid ${theme.colors.border}`,
      }}
    >
      <div
        style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          backgroundColor: theme.colors.surfaceHover,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <Icon size={16} color={color} />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[2],
            marginBottom: theme.spacing[1],
          }}
        >
          <span
            style={{
              fontSize: theme.typography.sizes.body,
              fontWeight: theme.typography.weights.medium,
              color: theme.colors.text,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            {event.title}
          </span>
          <span
            style={{
              fontSize: theme.typography.sizes.caption,
              color: theme.colors.textTertiary,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            {formatTimestamp(event.timestamp)}
          </span>
        </div>
        {event.description && (
          <p
            style={{
              margin: 0,
              fontSize: theme.typography.sizes.bodySmall,
              color: theme.colors.textSecondary,
              fontFamily: theme.typography.fontFamily,
              lineHeight: theme.typography.lineHeights.body,
            }}
          >
            {event.description}
          </p>
        )}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[2],
            marginTop: theme.spacing[1],
          }}
        >
          <span
            style={{
              fontSize: theme.typography.sizes.caption,
              color: theme.colors.textTertiary,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            by {event.actor}
          </span>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: `2px ${theme.spacing[2]}`,
              fontSize: theme.typography.sizes.caption,
              fontWeight: theme.typography.weights.medium,
              color,
              backgroundColor: `${color}15`,
              borderRadius: theme.borderRadius.sm,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            {event.severity}
          </span>
        </div>
      </div>
    </div>
  )
}

function formatTimestamp(timestamp: string): string {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function LoadingSkeleton() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            gap: theme.spacing[3],
            padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
            borderBottom: `1px solid ${theme.colors.border}`,
          }}
        >
          <Skeleton variant="avatar" width={32} height={32} />
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: theme.spacing[2] }}>
            <Skeleton variant="text" width="60%" height="16px" />
            <Skeleton variant="text" width="40%" height="12px" />
          </div>
        </div>
      ))}
    </div>
  )
}

interface TimelineTabProps {
  userId: string
}

export default function TimelineTab({ userId }: TimelineTabProps) {
  const { events, total, hasMore, loading, error, loadMore, refresh } = useUserTimeline(userId)

  if (error) {
    return (
      <Alert variant="error" title="Error loading timeline" action={{ label: 'Retry', onClick: refresh }}>
        {error}
      </Alert>
    )
  }

  if (loading && events.length === 0) {
    return <LoadingSkeleton />
  }

  if (events.length === 0) {
    return (
      <EmptyState
        title="No activity yet"
        description="Timeline events will appear here as the user interacts with the system."
      />
    )
  }

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
          borderBottom: `1px solid ${theme.colors.border}`,
          backgroundColor: theme.colors.surfaceHover,
        }}
      >
        <span
          style={{
            fontSize: theme.typography.sizes.bodySmall,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          {total} event{total !== 1 ? 's' : ''}
        </span>
      </div>
      <div>
        {events.map((event) => (
          <TimelineItem key={event.id} event={event} />
        ))}
      </div>
      {hasMore && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            padding: theme.spacing[4],
          }}
        >
          <Button
            variant="secondary"
            size="sm"
            onClick={loadMore}
            loading={loading}
          >
            Load More
          </Button>
        </div>
      )}
    </div>
  )
}
