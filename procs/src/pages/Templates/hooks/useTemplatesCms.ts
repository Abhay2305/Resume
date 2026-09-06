import { useState, useEffect, useCallback, useRef } from 'react'
import { getTemplatesCms } from '../../../services/api/templateCms.service'
import type { TemplateCmsItem, TemplateCmsFilters } from '../types'

interface UseTemplatesCmsResult {
  templates: TemplateCmsItem[]
  total: number
  loading: boolean
  error: string | null
  filters: TemplateCmsFilters
  searchInput: string
  setSearchInput: (value: string) => void
  setFilters: (updates: Partial<TemplateCmsFilters>) => void
  refresh: () => Promise<void>
}

const DEFAULT_FILTERS: TemplateCmsFilters = {
  search: '',
  category: null,
  status: null,
  page: 1,
  limit: 20,
}

export function useTemplatesCms(): UseTemplatesCmsResult {
  const [templates, setTemplates] = useState<TemplateCmsItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<TemplateCmsFilters>(DEFAULT_FILTERS)
  const [searchInput, setSearchInput] = useState(DEFAULT_FILTERS.search)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const fetchTemplates = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: Record<string, string | number | boolean | undefined> = {
        page: filters.page,
        limit: filters.limit,
      }
      if (filters.search) params.search = filters.search
      if (filters.category) params.category = filters.category
      if (filters.status) params.status = filters.status

      const response = await getTemplatesCms(params) as {
        items?: TemplateCmsItem[]
        total?: number
        page?: number
      }
      setTemplates(response.items || [])
      setTotal(response.total || 0)
    } catch {
      setError('Failed to load templates. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchTemplates()
  }, [fetchTemplates])

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

  const setFilters = useCallback((updates: Partial<TemplateCmsFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...updates,
      page: updates.page ?? (updates.search !== undefined || updates.category !== undefined || updates.status !== undefined ? 1 : prev.page),
    }))
  }, [])

  return { templates, total, loading, error, filters, searchInput, setSearchInput, setFilters, refresh: fetchTemplates }
}
