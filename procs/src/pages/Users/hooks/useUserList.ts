import { useState, useEffect, useCallback, useRef } from 'react'
import { getUsers } from '../../../services/api/user.service'
import type { UserListItem, UserListFilters } from '../types'

const DEFAULT_FILTERS: UserListFilters = {
  search: '',
  is_active: null,
  is_verified: null,
  sort_by: 'created_at',
  sort_order: 'desc',
  page: 1,
  limit: 20,
}

interface UseUserListReturn {
  users: UserListItem[]
  total: number
  totalPages: number
  loading: boolean
  error: string | null
  filters: UserListFilters
  searchInput: string
  setSearchInput: (value: string) => void
  setFilters: (updates: Partial<UserListFilters>) => void
  refresh: () => Promise<void>
}

export function useUserList(): UseUserListReturn {
  const [users, setUsers] = useState<UserListItem[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFiltersState] = useState<UserListFilters>(DEFAULT_FILTERS)
  const [searchInput, setSearchInput] = useState(DEFAULT_FILTERS.search)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const fetchUsers = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await getUsers(filters) as {
        items?: UserListItem[]
        total?: number
        totalPages?: number
      }
      setUsers(response.items || [])
      setTotal(response.total || 0)
      setTotalPages(response.totalPages || 0)
    } catch {
      setError('Failed to load users. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

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

  const setFilters = useCallback((updates: Partial<UserListFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...updates,
      page: updates.page ?? (updates.search !== undefined || updates.is_active !== undefined || updates.is_verified !== undefined ? 1 : prev.page),
    }))
  }, [])

  return {
    users,
    total,
    totalPages,
    loading,
    error,
    filters,
    searchInput,
    setSearchInput,
    setFilters,
    refresh: fetchUsers,
  }
}
