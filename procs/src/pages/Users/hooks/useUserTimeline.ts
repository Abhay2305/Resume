import { useState, useEffect, useCallback } from 'react'
import { getUserTimeline } from '../../../services/api/user.service'
import type { UserTimelineEvent } from '../types'

const PAGE_SIZE = 50

interface UseUserTimelineReturn {
  events: UserTimelineEvent[]
  total: number
  hasMore: boolean
  loading: boolean
  error: string | null
  loadMore: () => Promise<void>
  refresh: () => Promise<void>
}

export function useUserTimeline(userId: string): UseUserTimelineReturn {
  const [events, setEvents] = useState<UserTimelineEvent[]>([])
  const [total, setTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTimeline = useCallback(async (reset = false) => {
    setLoading(true)
    setError(null)

    try {
      const offset = reset ? 0 : events.length
      const response = await getUserTimeline(userId, {
        limit: PAGE_SIZE,
        offset,
      }) as { events?: UserTimelineEvent[]; total?: number; has_more?: boolean }

      const newEvents = response.events || []
      setEvents(prev => reset ? newEvents : [...prev, ...newEvents])
      setTotal(response.total || 0)
      setHasMore(response.has_more || false)
    } catch {
      setError('Failed to load timeline. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [userId, events.length])

  useEffect(() => {
    fetchTimeline(true)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId])

  const loadMore = useCallback(async () => {
    if (!loading && hasMore) {
      await fetchTimeline(false)
    }
  }, [fetchTimeline, loading, hasMore])

  const refresh = useCallback(async () => {
    await fetchTimeline(true)
  }, [fetchTimeline])

  return {
    events,
    total,
    hasMore,
    loading,
    error,
    loadMore,
    refresh,
  }
}
