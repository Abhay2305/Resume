import { FileText, Layout, Calendar, User } from 'lucide-react'
import KeyValueList from '../../../components/shared/KeyValueList'
import { theme } from '../../../styles/theme'
import type { ResumeDetail } from '../types'

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        backgroundColor: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
          borderBottom: `1px solid ${theme.colors.border}`,
          backgroundColor: theme.colors.surfaceHover,
        }}
      >
        <h3
          style={{
            margin: 0,
            fontSize: theme.typography.sizes.bodySmall,
            fontWeight: theme.typography.weights.semibold,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          {title}
        </h3>
      </div>
      <div style={{ padding: theme.spacing[4] }}>{children}</div>
    </div>
  )
}

interface ResumeOverviewTabProps {
  resume: ResumeDetail
}

export default function ResumeOverviewTab({ resume }: ResumeOverviewTabProps) {
  const resumeItems = [
    { key: 'ID', value: resume.id, icon: <FileText size={14} color={theme.colors.textTertiary} /> },
    { key: 'Status', value: resume.status === 'published' ? 'Published' : 'Draft' },
    { key: 'Template', value: resume.template_name, icon: <Layout size={14} color={theme.colors.textTertiary} /> },
    { key: 'Template Category', value: resume.template_category || '—' },
    { key: 'Sections', value: String(resume.sections?.length || 0) },
    { key: 'Versions', value: String(resume.versions?.length || 0) },
  ]

  const ownerItems = [
    { key: 'Email', value: resume.user_email, icon: <User size={14} color={theme.colors.textTertiary} /> },
    { key: 'Name', value: resume.user_name || '—' },
    { key: 'User ID', value: resume.user_id },
  ]

  const timestampItems = [
    { key: 'Created', value: formatDate(resume.created_at), icon: <Calendar size={14} color={theme.colors.textTertiary} /> },
    { key: 'Updated', value: formatDate(resume.updated_at) },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[4] }}>
      <SectionCard title="Resume Information">
        <KeyValueList items={resumeItems} columns={2} />
      </SectionCard>

      <SectionCard title="Owner Information">
        <KeyValueList items={ownerItems} columns={2} />
      </SectionCard>

      <SectionCard title="Timestamps">
        <KeyValueList items={timestampItems} columns={2} />
      </SectionCard>
    </div>
  )
}
