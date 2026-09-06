export const API_ENDPOINTS = {
  AUTH_LOGIN: '/auth/admin/login',
  AUTH_LOGOUT: '/auth/admin/logout',
  AUTH_ME: '/auth/admin/me',

  USERS: '/users',
  USER_BY_ID: (id: string) => `/users/${id}`,

  RESUMES: '/resumes',
  RESUME_BY_ID: (id: string) => `/resumes/${id}`,

  AI_COSTS: '/ai/costs',
  AI_TOKENS: '/ai/tokens',
  AI_EXECUTIONS: '/ai/executions',
  AI_PROVIDERS: '/ai/providers',

  AI_ADMIN_EXECUTIONS: '/ai/admin/executions',
  AI_ADMIN_EXECUTION_STATS: '/ai/admin/executions/stats',
  AI_ADMIN_TOKENS: '/ai/admin/tokens',
  AI_ADMIN_PROVIDERS: '/ai/admin/providers',

  ERRORS: '/errors',
  ERROR_STATS: '/errors/stats',
  ERROR_BY_ID: (id: string) => `/errors/${id}`,
  ERROR_ACKNOWLEDGE: (id: string) => `/errors/${id}/acknowledge`,
  ERROR_RESOLVE: (id: string) => `/errors/${id}/resolve`,

  AUDIT: '/audit',
  AUDIT_BY_ID: (entityType: string, entityId: string) => `/audit/${entityType}/${entityId}`,

  METRICS: '/metrics',
  METRICS_SUMMARY: '/metrics/summary',

  HEALTH: '/health',
  PROCS_HEALTH: '/procs/dashboard/health',

  PROCS_CHART_REQUESTS: '/procs/dashboard/charts/requests',
  PROCS_CHART_ERRORS: '/procs/dashboard/charts/errors',
  PROCS_CHART_AI_COST: '/procs/dashboard/charts/ai-cost',

  ANALYTICS_REVENUE: '/analytics/revenue',
  ANALYTICS_FEATURES: '/analytics/features',
  ANALYTICS_FUNNELS: '/analytics/funnels',

  CONFIG: '/config',
  CONFIG_BY_KEY: (key: string) => `/config/${key}`,
  CONFIG_FLAGS: '/config/flags',
  CONFIG_FLAG_BY_NAME: (name: string) => `/config/flags/${name}`,

  NOTIFICATIONS: '/notifications',
  AUDIT_TRAIL: '/audit',

  DASHBOARD_STATS: '/procs/dashboard/stats',
  DASHBOARD_ACTIVITY: '/procs/dashboard/activity',
  DASHBOARD_HEALTH: '/procs/dashboard/health',
  DASHBOARD_RECENT: '/procs/dashboard/recent',
  DASHBOARD_METRICS: '/procs/dashboard/metrics',
  DASHBOARD_CHART_REQUESTS: '/procs/dashboard/charts/requests',
  DASHBOARD_CHART_ERRORS: '/procs/dashboard/charts/errors',
  DASHBOARD_CHART_AI_COST: '/procs/dashboard/charts/ai-cost',

  PROCS_USERS: '/procs/users',
  PROCS_USER_BY_ID: (id: string) => `/procs/users/${id}`,
  PROCS_USER_TIMELINE: (id: string) => `/procs/users/${id}/timeline`,
  PROCS_USER_SESSIONS: (id: string) => `/procs/users/${id}/sessions`,

  PROCS_RESUMES: '/procs/resumes',
  PROCS_RESUME_BY_ID: (id: string) => `/procs/resumes/${id}`,
  PROCS_RESUME_STATS: '/procs/resumes/stats',
  PROCS_RESUME_TEMPLATES: '/procs/resumes/templates',
  PROCS_RESUME_TEMPLATE_STATS: '/procs/resumes/templates/stats',

  // Template CMS
  PROCS_TEMPLATES: '/procs/templates',
  PROCS_TEMPLATE_BY_ID: (id: string) => `/procs/templates/${id}`,
  PROCS_TEMPLATE_PUBLISH: (id: string) => `/procs/templates/${id}/publish`,
  PROCS_TEMPLATE_ARCHIVE: (id: string) => `/procs/templates/${id}/archive`,
  PROCS_TEMPLATE_DEPRECATE: (id: string) => `/procs/templates/${id}/deprecate`,
  PROCS_TEMPLATE_DUPLICATE: (id: string) => `/procs/templates/${id}/duplicate`,
  PROCS_TEMPLATE_VERSIONS: (id: string) => `/procs/templates/${id}/versions`,
  PROCS_TEMPLATE_RESTORE: (id: string, vid: string) => `/procs/templates/${id}/versions/${vid}/restore`,
  PROCS_TEMPLATE_REORDER: '/procs/templates/reorder',
  PROCS_TEMPLATE_UPLOAD_THUMBNAIL: (id: string) => `/procs/templates/${id}/upload/thumbnail`,
  PROCS_TEMPLATE_UPLOAD_PREVIEW: (id: string) => `/procs/templates/${id}/upload/preview`,
  PROCS_TEMPLATE_UPLOAD_DEFINITION: (id: string) => `/procs/templates/${id}/upload/definition`,
  PROCS_TEMPLATE_USAGE: (id: string) => `/procs/templates/${id}/usage`,
  PROCS_TEMPLATES_PUBLISHED: '/procs/templates/published',
} as const
