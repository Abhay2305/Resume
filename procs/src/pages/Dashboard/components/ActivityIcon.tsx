import { Plus, Pencil, Trash2, LogIn, LogOut, AlertTriangle, Download, Info } from 'lucide-react'
import { theme } from '../../../styles/theme'

interface ActivityIconProps {
  iconType: string
}

const iconConfig: Record<string, { icon: typeof Plus; bg: string; color: string }> = {
  create: { icon: Plus, bg: '#10B98120', color: theme.chart.series4 },
  update: { icon: Pencil, bg: '#3B82F620', color: theme.chart.series3 },
  delete: { icon: Trash2, bg: '#EF444420', color: theme.chart.series5 },
  login: { icon: LogIn, bg: '#7BC4BE20', color: theme.chart.series1 },
  logout: { icon: LogOut, bg: '#6B728020', color: theme.chart.series6 },
  error: { icon: AlertTriangle, bg: '#F6B23320', color: theme.chart.series2 },
  export: { icon: Download, bg: '#8B5CF620', color: '#8B5CF6' },
  info: { icon: Info, bg: '#6B728020', color: theme.chart.series6 },
}

export default function ActivityIcon({ iconType }: ActivityIconProps) {
  const config = iconConfig[iconType] || iconConfig.info
  const IconComponent = config.icon

  return (
    <div
      style={{
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        backgroundColor: config.bg,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}
      aria-label={`${iconType} activity`}
    >
      <IconComponent size={16} color={config.color} />
    </div>
  )
}
