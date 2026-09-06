import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import EmptyState from '../../../components/shared/EmptyState'
import { theme } from '../../../styles/theme'
import type { ResumeSection } from '../types'

function SectionItem({ section }: { section: ResumeSection }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      style={{
        backgroundColor: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md,
        overflow: 'hidden',
      }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
          backgroundColor: 'transparent',
          border: 'none',
          cursor: 'pointer',
          textAlign: 'left',
          gap: theme.spacing[2],
        }}
        aria-expanded={expanded}
        aria-label={`Toggle ${section.section_type} section`}
      >
        {expanded ? (
          <ChevronDown size={16} color={theme.colors.textTertiary} />
        ) : (
          <ChevronRight size={16} color={theme.colors.textTertiary} />
        )}
        <span
          style={{
            fontWeight: theme.typography.weights.medium,
            color: theme.colors.text,
            fontFamily: theme.typography.fontFamily,
            fontSize: theme.typography.sizes.body,
            flex: 1,
          }}
        >
          {section.section_type}
        </span>
        <span
          style={{
            fontSize: theme.typography.sizes.caption,
            color: theme.colors.textTertiary,
            fontFamily: theme.typography.fontFamily,
          }}
        >
          Position: {section.position}
        </span>
      </button>
      
      {expanded && (
        <div
          style={{
            padding: theme.spacing[4],
            borderTop: `1px solid ${theme.colors.border}`,
            backgroundColor: theme.colors.surfaceHover,
          }}
        >
          <pre
            style={{
              margin: 0,
              fontSize: theme.typography.sizes.caption,
              fontFamily: 'monospace',
              color: theme.colors.text,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              maxHeight: '400px',
              overflow: 'auto',
            }}
          >
            {JSON.stringify(section.content, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

interface ResumeSectionsTabProps {
  sections: ResumeSection[]
}

export default function ResumeSectionsTab({ sections }: ResumeSectionsTabProps) {
  if (!sections || sections.length === 0) {
    return <EmptyState title="No sections" description="This resume has no sections." />
  }

  const sortedSections = [...sections].sort((a, b) => a.position - b.position)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[3] }}>
      {sortedSections.map((section) => (
        <SectionItem key={section.id} section={section} />
      ))}
    </div>
  )
}
