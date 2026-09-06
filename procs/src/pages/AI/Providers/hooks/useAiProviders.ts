import { useState, useEffect, useCallback } from 'react'
import { getAiAdminProviders } from '../../../../services/api/ai.service'
import type { AiProviderStatsResponse } from '../../../../types/ai-monitoring'

interface UseAiProvidersReturn {
  data: AiProviderStatsResponse | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function useAiProviders(): UseAiProvidersReturn {
  const [data, setData] = useState<AiProviderStatsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchProviders = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getAiAdminProviders()
      setData(res)
    } catch {
      setError('Failed to load provider data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProviders()
  }, [fetchProviders])

  return { data, loading, error, refetch: fetchProviders }
}
