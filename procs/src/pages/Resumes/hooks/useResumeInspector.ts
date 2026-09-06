import { useState, useEffect, useCallback } from 'react'
import { getResumeDetail, updateResume, deleteResume } from '../../../services/api/resume.service'
import type { ResumeDetail, ResumeUpdateData } from '../types'

interface UseResumeInspectorReturn {
  resume: ResumeDetail | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  updateResume: (data: ResumeUpdateData) => Promise<void>
  deleteResume: () => Promise<void>
}

export function useResumeInspector(resumeId: string): UseResumeInspectorReturn {
  const [resume, setResume] = useState<ResumeDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchResume = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await getResumeDetail(resumeId) as { data?: ResumeDetail }
      setResume(response.data || null)
    } catch {
      setError('Failed to load resume details. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [resumeId])

  useEffect(() => {
    fetchResume()
  }, [fetchResume])

  const handleUpdateResume = useCallback(async (data: ResumeUpdateData) => {
    const response = await updateResume(resumeId, data) as { data?: ResumeDetail }
    if (response.data) {
      setResume(response.data)
    }
  }, [resumeId])

  const handleDeleteResume = useCallback(async () => {
    await deleteResume(resumeId)
    setResume(null)
  }, [resumeId])

  return {
    resume,
    loading,
    error,
    refresh: fetchResume,
    updateResume: handleUpdateResume,
    deleteResume: handleDeleteResume,
  }
}
