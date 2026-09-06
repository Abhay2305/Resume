import { Clock } from 'lucide-react'
import EmptyState from '../../../components/shared/EmptyState'
import { theme } from '../../../styles/theme'
import type { ResumeVersion } from '../types'

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

interface ResumeVersionsTabProps {
  versions: ResumeVersion[]
}

export default function ResumeVersionsTab({ versions }: ResumeVersionsTabProps) {
  if (!versions || versions.length === 0) {
    return <EmptyState title="No versions" description="This resume has no version history." />
  }

  const sortedVersions = [...versions].sort((a, b) => b.version_number - a.version_number)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[3] }}>
      {sortedVersions.map((version) => (
        <div
          key={version.id}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[3],
            padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
            backgroundColor: theme.colors.surface,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.md,
          }}
        >
          <Clock size={16} color={theme.colors.textTertiary} />
          <div style={{ flex: 1 }}>
            <span
              style={{
                fontWeight: theme.typography.weights.medium,
                color: theme.colors.text,
                fontFamily: theme.typography.fontFamily,
                fontSize: theme.typography.sizes.body,
              }}
            >
              Version {version.version_number}
            </span>
          </div>
          <span
            style={{
              fontSize: theme.typography.sizes.caption,
              color: theme.colors.textSecondary,
              fontFamily: theme.typography.fontFamily,
            }}
          >
            {formatDate(version.created_at)}
          </span>
        </div>
      ))}
    </div>
  )
}
