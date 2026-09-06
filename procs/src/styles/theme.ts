export const theme = {
  colors: {
    primary: '#7BC4BE',
    primaryHover: '#6AB5AF',
    primaryActive: '#5AA69F',
    primaryLight: '#A8D8D3',
    primaryDark: '#4A9E98',

    background: '#F8FAFC',
    surface: '#FFFFFF',
    surfaceHover: '#F1F5F9',
    surfaceActive: '#E2E8F0',
    border: '#E2E8F0',
    borderStrong: '#CBD5E1',
    divider: '#F1F5F9',

    text: '#0F172A',
    textSecondary: '#475569',
    textTertiary: '#94A3B8',
    textInverse: '#FFFFFF',

    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    info: '#3B82F6',

    successBg: '#ECFDF5',
    warningBg: '#FFFBEB',
    dangerBg: '#FEF2F2',
    infoBg: '#EFF6FF',
    neutralBg: '#F8FAFC',
  },

  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    sizes: {
      display: '30px',
      h1: '24px',
      h2: '20px',
      h3: '16px',
      body: '14px',
      bodySmall: '13px',
      caption: '12px',
      tiny: '11px',
    },
    weights: {
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeights: {
      heading: 1.2,
      body: 1.5,
    },
  },

  spacing: {
    0: '0px',
    1: '4px',
    2: '8px',
    3: '12px',
    4: '16px',
    5: '20px',
    6: '24px',
    8: '32px',
    10: '40px',
    12: '48px',
  },

  layout: {
    sidebarWidth: '240px',
    sidebarCollapsed: '64px',
    headerHeight: '64px',
    pagePadding: '24px',
    cardPadding: '16px',
    sectionGap: '24px',
    tableRowHeight: '48px',
  },

  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
    lg: '0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06)',
  },

  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    full: '9999px',
  },

  chart: {
    series1: '#7BC4BE',
    series2: '#F6B233',
    series3: '#3B82F6',
    series4: '#10B981',
    series5: '#EF4444',
    series6: '#6B7280',
  },

  transitions: {
    fast: '150ms ease',
    normal: '200ms ease',
    slow: '300ms ease',
  },

  borderWidth: {
    thin: '1px',
    medium: '2px',
    thick: '3px',
  },

  statusColors: {
    success: { text: '#065F46', bg: '#ECFDF5', border: '#A7F3D0' },
    warning: { text: '#92400E', bg: '#FFFBEB', border: '#FDE68A' },
    danger: { text: '#991B1B', bg: '#FEF2F2', border: '#FECACA' },
    info: { text: '#1E40AF', bg: '#EFF6FF', border: '#BFDBFE' },
    neutral: { text: '#475569', bg: '#F8FAFC', border: '#E2E8F0' },
  },

  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    popover: 1040,
    tooltip: 1050,
    toast: 1060,
    modal: 1100,
  },
} as const

export type Theme = typeof theme
