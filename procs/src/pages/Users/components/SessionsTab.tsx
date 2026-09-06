import { useState, useEffect, useCallback } from 'react'
import Skeleton from '../../../components/shared/Skeleton'
import Alert from '../../../components/shared/Alert'
import EmptyState from '../../../components/shared/EmptyState'
import { theme } from '../../../styles/theme'
import { getUserSessions } from '../../../services/api/user.service'
import type { UserSession } from '../types'

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function parseUserAgent(ua: string | null): { browser: string; device: string } {
  if (!ua) return { browser: 'Unknown', device: 'Unknown' }

  let browser = 'Unknown'
  if (ua.includes('Chrome')) browser = 'Chrome'
  else if (ua.includes('Firefox')) browser = 'Firefox'
  else if (ua.includes('Safari')) browser = 'Safari'
  else if (ua.includes('Edge')) browser = 'Edge'

  let device = 'Desktop'
  if (ua.includes('Mobile') || ua.includes('Android')) device = 'Mobile'
  else if (ua.includes('iPad') || ua.includes('Tablet')) device = 'Tablet'

  return { browser, device }
}

function formatDuration(created: string, expires: string | null): string {
  if (!expires) return '—'
  const start = new Date(created).getTime()
  const end = new Date(expires).getTime()
  const diffMs = end - start
  if (diffMs <= 0) return 'Expired'
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins}m`
}

interface SessionsTabProps {
  userId: string
}

export default function SessionsTab({ userId }: SessionsTabProps) {
  const [sessions, setSessions] = useState<UserSession[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSessions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await getUserSessions(userId) as {
        items?: UserSession[]
        total?: number
      }
      setSessions(response.items || [])
      setTotal(response.total || 0)
    } catch {
      setError('Failed to load sessions. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    fetchSessions()
  }, [fetchSessions])

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {Array.from({ length: 3 }).map((_, i) => (
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

  if (error) {
    return (
      <Alert variant="error" title="Error loading sessions" action={{ label: 'Retry', onClick: fetchSessions }}>
        {error}
      </Alert>
    )
  }

  if (sessions.length === 0) {
    return (
      <EmptyState
        title="No sessions found"
        description="Session history is not yet available. Sessions will appear here once the session tracking backend is implemented."
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
          {total} session{total !== 1 ? 's' : ''}
        </span>
      </div>
      <div style={{ border: `1px solid ${theme.colors.border}`, borderRadius: theme.borderRadius.md, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: theme.typography.fontFamily }}>
          <thead>
            <tr style={{ borderBottom: `1px solid ${theme.colors.border}`, backgroundColor: theme.colors.neutralBg }}>
              <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'left', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>Login Time</th>
              <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'left', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>Duration</th>
              <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'left', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>IP Address</th>
              <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'left', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>Browser</th>
              <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'left', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>Device</th>
              <th style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, textAlign: 'left', fontSize: theme.typography.sizes.caption, fontWeight: theme.typography.weights.semibold, color: theme.colors.textSecondary }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session) => {
              const { browser, device } = parseUserAgent(session.user_agent)
              const isActive = session.expires_at ? new Date(session.expires_at) > new Date() : false
              return (
                <tr key={session.id} style={{ borderBottom: `1px solid ${theme.colors.divider}` }}>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, fontSize: theme.typography.sizes.body, color: theme.colors.text }}>
                    {formatDate(session.created_at)}
                  </td>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, fontSize: theme.typography.sizes.body, color: theme.colors.textSecondary }}>
                    {formatDuration(session.created_at, session.expires_at)}
                  </td>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, fontSize: theme.typography.sizes.body, color: theme.colors.textSecondary, fontFamily: 'monospace' }}>
                    {session.ip_address || '—'}
                  </td>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, fontSize: theme.typography.sizes.body, color: theme.colors.text }}>
                    {browser}
                  </td>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}`, fontSize: theme.typography.sizes.body, color: theme.colors.text }}>
                    {session.device_type || device}
                  </td>
                  <td style={{ padding: `${theme.spacing[3]} ${theme.spacing[4]}` }}>
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '2px 8px',
                        fontSize: theme.typography.sizes.tiny,
                        fontWeight: theme.typography.weights.medium,
                        color: isActive ? theme.colors.success : theme.colors.textSecondary,
                        backgroundColor: isActive ? theme.colors.successBg : theme.colors.neutralBg,
                        borderRadius: theme.borderRadius.full,
                      }}
                    >
                      <span
                        style={{
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          backgroundColor: isActive ? theme.colors.success : theme.colors.textTertiary,
                        }}
                      />
                      {isActive ? 'Active' : 'Expired'}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
