import { theme } from '../../../styles/theme'
import { Button, Alert } from '../../../components/shared'
import { useAiProviders } from './hooks/useAiProviders'
import ProviderCard from './components/ProviderCard'
import { RefreshCw } from 'lucide-react'

export default function ProvidersPage() {
  const { data, loading, error, refetch } = useAiProviders()

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: theme.spacing[5],
      }}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: theme.typography.sizes.h1,
            fontWeight: theme.typography.weights.bold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
          }}>
            AI Providers
          </h1>
          <p style={{
            margin: 0,
            marginTop: theme.spacing[1],
            fontSize: theme.typography.sizes.body,
            color: theme.colors.textSecondary,
            fontFamily: theme.typography.fontFamily,
          }}>
            Provider health status and usage statistics
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          icon={<RefreshCw size={14} />}
          onClick={refetch}
          loading={loading}
        >
          Refresh
        </Button>
      </div>

      {error && (
        <div style={{ marginBottom: theme.spacing[4] }}>
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
        gap: theme.spacing[4],
      }}>
        {(data?.providers || []).map((provider) => (
          <ProviderCard key={provider.name} provider={provider} loading={loading} />
        ))}
      </div>
    </div>
  )
}
