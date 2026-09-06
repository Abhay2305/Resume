import {
  LayoutDashboard,
  Users,
  FileText,
  Layout,
  DollarSign,
  BarChart3,
  Eye,
  Server,
  ScrollText,
  AlertTriangle,
  Activity,
  Clock,
  HardDrive,
  TrendingUp,
  PieChart,
  Filter,
  ToggleLeft,
  Bell,
  Shield,
  Settings,
  type LucideIcon,
} from 'lucide-react'

export interface NavItemConfig {
  id: string
  label: string
  route: string
  icon: LucideIcon
}

export interface NavGroupConfig {
  id: string
  label: string
  items: NavItemConfig[]
}

export const navigationConfig: NavGroupConfig[] = [
  {
    id: 'overview',
    label: 'OVERVIEW',
    items: [
      { id: 'dashboard', label: 'Dashboard', route: '/', icon: LayoutDashboard },
    ],
  },
  {
    id: 'operations',
    label: 'OPERATIONS',
    items: [
      { id: 'users', label: 'Users', route: '/users', icon: Users },
      { id: 'resumes', label: 'Resumes', route: '/resumes', icon: FileText },
      { id: 'templates', label: 'Templates', route: '/templates', icon: Layout },
    ],
  },
  {
    id: 'intelligence',
    label: 'INTELLIGENCE',
    items: [
      { id: 'ai-costs', label: 'AI Cost Center', route: '/ai/costs', icon: DollarSign },
      { id: 'ai-tokens', label: 'Token Analytics', route: '/ai/tokens', icon: BarChart3 },
      { id: 'ai-executions', label: 'AI Observability', route: '/ai/executions', icon: Eye },
      { id: 'ai-providers', label: 'Providers', route: '/ai/providers', icon: Server },
    ],
  },
  {
    id: 'monitoring',
    label: 'MONITORING',
    items: [
      { id: 'logs', label: 'System Logs', route: '/logs', icon: ScrollText },
      { id: 'errors', label: 'Errors', route: '/errors', icon: AlertTriangle },
      { id: 'api-monitor', label: 'API Monitor', route: '/api-monitor', icon: Activity },
      { id: 'jobs', label: 'Background Jobs', route: '/jobs', icon: Clock },
      { id: 'health', label: 'Infrastructure', route: '/health', icon: HardDrive },
    ],
  },
  {
    id: 'analytics',
    label: 'ANALYTICS',
    items: [
      { id: 'revenue', label: 'Revenue', route: '/analytics/revenue', icon: TrendingUp },
      { id: 'features', label: 'Feature Usage', route: '/analytics/features', icon: PieChart },
      { id: 'funnels', label: 'Funnels', route: '/analytics/funnels', icon: Filter },
    ],
  },
  {
    id: 'configuration',
    label: 'CONFIGURATION',
    items: [
      { id: 'flags', label: 'Feature Flags', route: '/flags', icon: ToggleLeft },
      { id: 'notifications', label: 'Notifications', route: '/notifications', icon: Bell },
      { id: 'audit', label: 'Audit Trail', route: '/audit', icon: Shield },
      { id: 'settings', label: 'Settings', route: '/settings', icon: Settings },
    ],
  },
]

export interface BreadcrumbConfig {
  label: string
  route: string
}

const routeToBreadcrumb: Record<string, BreadcrumbConfig[]> = {
  '/': [{ label: 'Dashboard', route: '/' }],
  '/users': [
    { label: 'Operations', route: '/users' },
    { label: 'Users', route: '/users' },
  ],
  '/resumes': [
    { label: 'Operations', route: '/resumes' },
    { label: 'Resumes', route: '/resumes' },
  ],
  '/templates': [
    { label: 'Operations', route: '/templates' },
    { label: 'Templates', route: '/templates' },
  ],
  '/ai/costs': [
    { label: 'Intelligence', route: '/ai/costs' },
    { label: 'AI Cost Center', route: '/ai/costs' },
  ],
  '/ai/tokens': [
    { label: 'Intelligence', route: '/ai/tokens' },
    { label: 'Token Analytics', route: '/ai/tokens' },
  ],
  '/ai/executions': [
    { label: 'Intelligence', route: '/ai/executions' },
    { label: 'AI Observability', route: '/ai/executions' },
  ],
  '/ai/providers': [
    { label: 'Intelligence', route: '/ai/providers' },
    { label: 'Providers', route: '/ai/providers' },
  ],
  '/logs': [
    { label: 'Monitoring', route: '/logs' },
    { label: 'System Logs', route: '/logs' },
  ],
  '/errors': [
    { label: 'Monitoring', route: '/errors' },
    { label: 'Errors', route: '/errors' },
  ],
  '/api-monitor': [
    { label: 'Monitoring', route: '/api-monitor' },
    { label: 'API Monitor', route: '/api-monitor' },
  ],
  '/jobs': [
    { label: 'Monitoring', route: '/jobs' },
    { label: 'Background Jobs', route: '/jobs' },
  ],
  '/health': [
    { label: 'Monitoring', route: '/health' },
    { label: 'Infrastructure', route: '/health' },
  ],
  '/analytics/revenue': [
    { label: 'Analytics', route: '/analytics/revenue' },
    { label: 'Revenue', route: '/analytics/revenue' },
  ],
  '/analytics/features': [
    { label: 'Analytics', route: '/analytics/features' },
    { label: 'Feature Usage', route: '/analytics/features' },
  ],
  '/analytics/funnels': [
    { label: 'Analytics', route: '/analytics/funnels' },
    { label: 'Funnels', route: '/analytics/funnels' },
  ],
  '/flags': [
    { label: 'Configuration', route: '/flags' },
    { label: 'Feature Flags', route: '/flags' },
  ],
  '/notifications': [
    { label: 'Configuration', route: '/notifications' },
    { label: 'Notifications', route: '/notifications' },
  ],
  '/audit': [
    { label: 'Configuration', route: '/audit' },
    { label: 'Audit Trail', route: '/audit' },
  ],
  '/settings': [
    { label: 'Configuration', route: '/settings' },
    { label: 'Settings', route: '/settings' },
  ],
}

export function getBreadcrumbItems(pathname: string): BreadcrumbConfig[] {
  if (routeToBreadcrumb[pathname]) {
    return routeToBreadcrumb[pathname]
  }

  const segments = pathname.split('/').filter(Boolean)
  if (segments.length === 0) {
    return [{ label: 'Dashboard', route: '/' }]
  }

  if (segments[0] === 'users' && segments.length > 1) {
    return [
      { label: 'Operations', route: '/users' },
      { label: 'Users', route: '/users' },
      { label: 'Detail', route: pathname },
    ]
  }

  if (segments[0] === 'resumes' && segments.length > 1) {
    return [
      { label: 'Operations', route: '/resumes' },
      { label: 'Resumes', route: '/resumes' },
      { label: 'Detail', route: pathname },
    ]
  }

  const fallback = segments.map((seg, i) => ({
    label: seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, ' '),
    route: '/' + segments.slice(0, i + 1).join('/'),
  }))

  return fallback.length > 0 ? fallback : [{ label: 'Dashboard', route: '/' }]
}
