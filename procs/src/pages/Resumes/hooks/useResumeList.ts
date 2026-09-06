import { useState, useEffect, useCallback, useRef } from 'react'
import { getResumes } from '../../../services/api/resume.service'
import type { ResumeListItem, ResumeListFilters } from '../types'

const DEFAULT_FILTERS: ResumeListFilters = {
  search: '',
  status: null,
  template: null,
  sort_by: 'created_at',
  sort_order: 'desc',
  page: 1,
  limit: 20,
}

interface UseResumeListReturn {
  resumes: ResumeListItem[]
  total: number
  loading: boolean
  error: string | null
  filters: ResumeListFilters
  searchInput: string
  setSearchInput: (value: string) => void
  setFilters: (updates: Partial<ResumeListFilters>) => void
  refresh: () => Promise<void>
}

export function useResumeList(): UseResumeListReturn {
  const [resumes, setResumes] = useState<ResumeListItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<ResumeListFilters>(DEFAULT_FILTERS)
  const [searchInput, setSearchInput] = useState(DEFAULT_FILTERS.search)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const fetchResumes = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
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
  }, [filters])

  useEffect(() => {
    fetchResumes()
  }, [fetchResumes])

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setFiltersState((prev) => {
        if (prev.search === searchInput) return prev
        return { ...prev, search: searchInput, page: 1 }
      })
    }, 300)
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [searchInput])

  const setFilters = useCallback((updates: Partial<ResumeListFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...updates,
      page: updates.page ?? (updates.search !== undefined || updates.status !== undefined || updates.template !== undefined ? 1 : prev.page),
    }))
  }, [])

  return {
    resumes,
    total,
    loading,
    error,
    filters,
    searchInput,
    setSearchInput,
    setFilters,
    refresh: fetchResumes,
  }
}
