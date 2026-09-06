import { useState, useEffect, useCallback } from 'react'
import { getUserDetail, updateUser, deleteUser } from '../../../services/api/user.service'
import type { UserDetail } from '../types'

interface UseUserInspectorReturn {
  user: UserDetail | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  updateUser: (data: Record<string, unknown>) => Promise<void>
  deleteUser: () => Promise<void>
}

export function useUserInspector(userId: string): UseUserInspectorReturn {
  const [user, setUser] = useState<UserDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchUser = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await getUserDetail(userId) as { data?: UserDetail }
      setUser(response.data || null)
    } catch {
      setError('Failed to load user details. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const handleUpdateUser = useCallback(async (data: Record<string, unknown>) => {
    const response = await updateUser(userId, data) as { data?: UserDetail }
    if (response.data) {
      setUser(response.data)
    }
  }, [userId])

  const handleDeleteUser = useCallback(async () => {
    await deleteUser(userId)
    setUser(null)
  }, [userId])

  return {
    user,
    loading,
    error,
    refresh: fetchUser,
    updateUser: handleUpdateUser,
    deleteUser: handleDeleteUser,
  }
}
