import { FileText, Clock, CheckCircle, Layout } from 'lucide-react'
import MetricCard from '../../../components/shared/MetricCard'
import { theme } from '../../../styles/theme'
import type { ResumeStats } from '../types'

interface ResumeStatsCardsProps {
  stats: ResumeStats | null
  loading: boolean
}

export default function ResumeStatsCards({ stats, loading }: ResumeStatsCardsProps) {
  const cards = [
    {
      title: 'Total Resumes',
      value: stats?.total_resumes ?? 0,
      icon: <FileText size={20} color={theme.colors.primary} />,
      loading,
    },
    {
      title: 'Draft',
      value: stats?.draft_count ?? 0,
      icon: <Clock size={20} color={theme.colors.warning} />,
      loading,
    },
    {
      title: 'Published',
      value: stats?.published_count ?? 0,
      icon: <CheckCircle size={20} color={theme.colors.success} />,
      loading,
    },
    {
      title: 'Templates',
      value: stats?.templates?.length ?? 0,
      icon: <Layout size={20} color={theme.colors.info} />,
      loading,
    },
  ]

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing[4],
        marginBottom: theme.spacing[6],
      }}
    >
      {cards.map((card) => (
        <MetricCard
          key={card.title}
          title={card.title}
          value={card.value}
          loading={card.loading}
        />
      ))}
    </div>
  )
}
