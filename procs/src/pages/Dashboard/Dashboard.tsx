import { useDashboard } from './hooks/useDashboard'
import DashboardHeader from './components/DashboardHeader'
import HealthSection from './components/HealthSection'
import MetricsSection from './components/MetricsSection'
import ChartsGrid from './components/ChartsGrid'
import ActivityFeed from './components/ActivityFeed'
import { theme } from '../../styles/theme'

export default function Dashboard() {
  const {
    metrics,
    activity,
    activityHasMore,
    activityLoadingMore,
    health,
    chartRequests,
    chartErrors,
    chartAiCost,
    period,
    loading,
    chartsLoading,
    error,
    setPeriod,
    refresh,
    loadMoreActivity,
  } = useDashboard()

  return (
    <div style={{ padding: theme.layout.pagePadding }}>
      <DashboardHeader period={period} onPeriodChange={setPeriod} />

      <HealthSection
        health={health}
        loading={loading}
        error={error}
        onRetry={refresh}
      />

      <MetricsSection
        metrics={metrics}
        loading={loading}
        error={error}
      />

      <ChartsGrid
        chartRequests={chartRequests}
        chartErrors={chartErrors}
        chartAiCost={chartAiCost}
        loading={chartsLoading}
      />

      <ActivityFeed
        activity={activity}
        loading={loading}
        hasMore={activityHasMore}
        onLoadMore={loadMoreActivity}
        loadingMore={activityLoadingMore}
      />

      <style>{`
        @media (max-width: 1279px) {
          .dashboard-metrics-grid { grid-template-columns: repeat(2, 1fr) !important; }
          .dashboard-charts-grid { grid-template-columns: 1fr !important; }
        }
        @media (max-width: 767px) {
          .dashboard-metrics-grid { grid-template-columns: 1fr !important; }
          .dashboard-charts-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}
