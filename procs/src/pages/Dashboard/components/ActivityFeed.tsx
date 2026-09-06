import Skeleton from '../../../components/shared/Skeleton'
import EmptyState from '../../../components/shared/EmptyState'
import { theme } from '../../../styles/theme'
import type { DashboardActivity } from '../types'
import ActivityIcon from './ActivityIcon'

interface ActivityFeedProps {
  activity: DashboardActivity[]
  loading: boolean
  hasMore: boolean
  onLoadMore: () => void
  loadingMore: boolean
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)

  if (diffMin < 1) return 'Just now'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffH = Math.floor(diffMin / 60)
  if (diffH < 24) return `${diffH}h ago`
  const diffD = Math.floor(diffH / 24)
  return `${diffD}d ago`
}

export default function ActivityFeed({ activity, loading, hasMore, onLoadMore, loadingMore }: ActivityFeedProps) {
  return (
    <div
      style={{
        backgroundColor: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
          borderBottom: `1px solid ${theme.colors.border}`,
          fontSize: theme.typography.sizes.bodySmall,
          fontWeight: theme.typography.weights.medium,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}
      >
        Recent Activity
      </div>

      <div style={{ padding: theme.spacing[2] }}>
        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[2] }}>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[3], padding: `${theme.spacing[2]} ${theme.spacing[3]}` }}>
                <Skeleton variant="avatar" width={32} height={32} />
                <div style={{ flex: 1 }}>
                  <Skeleton variant="text" width="70%" height="14px" />
                  <Skeleton variant="text" width="40%" height="12px" />
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && activity.length === 0 && (
          <EmptyState
            title="No recent activity"
            description="Activity will appear here as events occur."
          />
        )}

        {!loading && activity.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {activity.map((item) => (
              <div
                key={item.id}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: theme.spacing[3],
                  padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
                  borderBottom: `1px solid ${theme.colors.divider}`,
                }}
              >
                <ActivityIcon iconType={item.icon_type || 'info'} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: theme.typography.sizes.body,
                      color: theme.colors.text,
                      fontFamily: theme.typography.fontFamily,
                    }}
                  >
                    <span style={{ fontWeight: theme.typography.weights.medium }}>
                      {item.action}
                    </span>
                    {' '}
                    {item.entity_label || item.subject}
                  </div>
                  <div
                    style={{
                      fontSize: theme.typography.sizes.caption,
                      color: theme.colors.textTertiary,
                      fontFamily: theme.typography.fontFamily,
                      marginTop: '2px',
                    }}
                  >
                    {item.admin_email && (
                      <span>{item.admin_email} · </span>
                    )}
                    {formatTimestamp(item.timestamp)}
                  </div>
                </div>
              </div>
            ))}

            {hasMore && (
              <div
                style={{
                  padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
                  display: 'flex',
                  justifyContent: 'center',
                }}
              >
                <button
                  onClick={onLoadMore}
                  disabled={loadingMore}
                  style={{
                    backgroundColor: 'transparent',
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.sm,
                    padding: `${theme.spacing[2]} ${theme.spacing[4]}`,
                    fontSize: theme.typography.sizes.bodySmall,
                    color: theme.colors.textSecondary,
                    fontFamily: theme.typography.fontFamily,
                    cursor: loadingMore ? 'not-allowed' : 'pointer',
                    opacity: loadingMore ? 0.6 : 1,
                  }}
                >
                  {loadingMore ? 'Loading...' : 'Show More'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
