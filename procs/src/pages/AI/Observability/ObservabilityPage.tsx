import { useState } from 'react'
import { theme } from '../../../styles/theme'
import { MetricCard, Alert } from '../../../components/shared'
import { useAiExecutions } from './hooks/useAiExecutions'
import ExecutionTable from './components/ExecutionTable'
import ExecutionDetailModal from './components/ExecutionDetailModal'
import type { AiExecutionLog } from '../../../types/ai-monitoring'

const PROVIDERS = ['', 'gemini', 'openai', 'anthropic']
const STATUSES = ['', 'completed', 'failed', 'pending']

export default function ObservabilityPage() {
  const { executions, total, stats, loading, error, filters, setFilters, refresh } = useAiExecutions()
  const [selectedExecution, setSelectedExecution] = useState<AiExecutionLog | null>(null)

  return (
    <div style={{ padding: theme.spacing[6] }}>
      <div style={{ marginBottom: theme.spacing[5] }}>
        <h1 style={{
          margin: 0,
          fontSize: theme.typography.sizes.h1,
          fontWeight: theme.typography.weights.bold,
          color: theme.colors.text,
          fontFamily: theme.typography.fontFamily,
        }}>
          AI Observability
        </h1>
        <p style={{
          margin: 0,
          marginTop: theme.spacing[1],
          fontSize: theme.typography.sizes.body,
          color: theme.colors.textSecondary,
          fontFamily: theme.typography.fontFamily,
        }}>
          Monitor AI execution performance and failures
        </p>
      </div>

      {error && (
        <div style={{ marginBottom: theme.spacing[4] }}>
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[5],
      }}>
        <MetricCard
          title="Total Executions"
          value={stats?.total_executions ?? 0}
          loading={loading}
          testId="metric-total-executions"
        />
        <MetricCard
          title="Success Rate"
          value={`${stats?.success_rate ?? 0}%`}
          loading={loading}
          testId="metric-success-rate"
        />
        <MetricCard
          title="Failure Rate"
          value={`${stats?.failure_rate ?? 0}%`}
          loading={loading}
          testId="metric-failure-rate"
        />
        <MetricCard
          title="Avg Latency"
          value={stats?.avg_latency_ms ? `${Math.round(stats.avg_latency_ms)}ms` : '0ms'}
          loading={loading}
          testId="metric-avg-latency"
        />
      </div>

      <div style={{
        display: 'flex',
        gap: theme.spacing[3],
        marginBottom: theme.spacing[4],
        flexWrap: 'wrap',
      }}>
        <select
          value={filters.provider || ''}
          onChange={(e) => setFilters({ provider: e.target.value || undefined, page: 1 })}
          style={{
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            outline: 'none',
            minWidth: '130px',
          }}
        >
          {PROVIDERS.map((p) => (
            <option key={p} value={p}>{p || 'All Providers'}</option>
          ))}
        </select>
        <select
          value={filters.status || ''}
          onChange={(e) => setFilters({ status: e.target.value || undefined, page: 1 })}
          style={{
            padding: `${theme.spacing[2]} ${theme.spacing[3]}`,
            fontSize: theme.typography.sizes.body,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            outline: 'none',
            minWidth: '130px',
          }}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s || 'All Statuses'}</option>
          ))}
        </select>
      </div>

      <ExecutionTable
        executions={executions}
        loading={loading}
        error={error}
        onRefresh={refresh}
        onRowClick={setSelectedExecution}
        page={filters.page}
        perPage={filters.size}
        total={total}
        onPageChange={(p) => setFilters({ page: p })}
      />

      <ExecutionDetailModal
        execution={selectedExecution}
        open={!!selectedExecution}
        onClose={() => setSelectedExecution(null)}
      />
    </div>
  )
}
