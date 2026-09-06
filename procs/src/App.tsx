import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppShell from './components/layout/AppShell'
import { useSidebar } from './hooks/useSidebar'

import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import UserList from './pages/Users/UserList'
import UserInspector from './pages/Users/UserInspector'
import ResumeList from './pages/Resumes/ResumeList'
import ResumeInspector from './pages/Resumes/ResumeInspector'
import TemplateList from './pages/Templates/TemplateList'
import CostCenter from './pages/AI/CostCenter'
import TokenAnalytics from './pages/AI/TokenAnalytics'
import Observability from './pages/AI/Observability'
import Providers from './pages/AI/Providers'
import SystemLogs from './pages/Monitoring/SystemLogs'
import Errors from './pages/Monitoring/Errors'
import ApiMonitor from './pages/Monitoring/ApiMonitor'
import BackgroundJobs from './pages/Monitoring/BackgroundJobs'
import Infrastructure from './pages/Monitoring/Infrastructure'
import Revenue from './pages/Analytics/Revenue'
import FeatureUsage from './pages/Analytics/FeatureUsage'
import Funnels from './pages/Analytics/Funnels'
import FeatureFlags from './pages/Configuration/FeatureFlags'
import Notifications from './pages/Configuration/Notifications'
import AuditTrail from './pages/Configuration/AuditTrail'
import Settings from './pages/Configuration/Settings'
import NotFound from './pages/NotFound'

function AuthenticatedRoutes() {
  const { isCollapsed, toggle } = useSidebar()

  return (
    <AppShell isCollapsed={isCollapsed} toggleSidebar={toggle}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/users" element={<UserList />} />
        <Route path="/users/:id" element={<UserInspector />} />
        <Route path="/resumes" element={<ResumeList />} />
        <Route path="/resumes/:id" element={<ResumeInspector />} />
        <Route path="/templates" element={<TemplateList />} />
        <Route path="/ai/costs" element={<CostCenter />} />
        <Route path="/ai/tokens" element={<TokenAnalytics />} />
        <Route path="/ai/executions" element={<Observability />} />
        <Route path="/ai/providers" element={<Providers />} />
        <Route path="/logs" element={<SystemLogs />} />
        <Route path="/errors" element={<Errors />} />
        <Route path="/api-monitor" element={<ApiMonitor />} />
        <Route path="/jobs" element={<BackgroundJobs />} />
        <Route path="/health" element={<Infrastructure />} />
        <Route path="/analytics/revenue" element={<Revenue />} />
        <Route path="/analytics/features" element={<FeatureUsage />} />
        <Route path="/analytics/funnels" element={<Funnels />} />
        <Route path="/flags" element={<FeatureFlags />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/audit" element={<AuditTrail />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </AppShell>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AuthenticatedRoutes />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
