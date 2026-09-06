import { useState, useEffect, useCallback } from 'react'
import { getAiAdminTokens } from '../../../../services/api/ai.service'
import type { AiTokenResponse } from '../../../../types/ai-monitoring'

interface UseAiTokensReturn {
  data: AiTokenResponse | null
  period: string
  setPeriod: (p: string) => void
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function useAiTokens(): UseAiTokensReturn {
  const [data, setData] = useState<AiTokenResponse | null>(null)
  const [period, setPeriod] = useState('24h')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTokens = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getAiAdminTokens({ period })
      setData(res)
    } catch {
      setError('Failed to load token data')
    } finally {
      setLoading(false)
    }
  }, [period])

  useEffect(() => {
    fetchTokens()
  }, [fetchTokens])

  return { data, period, setPeriod, loading, error, refetch: fetchTokens }
}
