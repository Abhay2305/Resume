import { useState, useEffect, useCallback } from 'react'
import { getResumes } from '../../../services/api/resume.service'
import type { ResumeListItem, ResumeListFilters } from '../../Resumes/types'

interface UseUserResumesResult {
  resumes: ResumeListItem[]
  total: number
  page: number
  loading: boolean
  error: string | null
  setPage: (page: number) => void
  refresh: () => void
}

const PAGE_SIZE = 10

export function useUserResumes(userId: string): UseUserResumesResult {
  const [resumes, setResumes] = useState<ResumeListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchResumes = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const filters: ResumeListFilters = {
        search: '',
        status: null,
        template: null,
        user_id: userId,
        sort_by: 'updated_at',
        sort_order: 'desc',
        page,
        limit: PAGE_SIZE,
      }
      const response = await getResumes(filters) as {
        items?: ResumeListItem[]
        total?: number
      }
      setResumes(response.items || [])
      setTotal(response.total || 0)
    } catch {
      setError('Failed to load resumes. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [userId, page])

  useEffect(() => {
    fetchResumes()
  }, [fetchResumes])

  useEffect(() => {
    setPage(1)
  }, [userId])

  return { resumes, total, page, loading, error, setPage, refresh: fetchResumes }
}
