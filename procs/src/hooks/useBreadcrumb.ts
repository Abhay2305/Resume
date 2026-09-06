import { useLocation } from 'react-router-dom'
import { getBreadcrumbItems, type BreadcrumbConfig } from '../config/navigation'

export function useBreadcrumb(): BreadcrumbConfig[] {
  const location = useLocation()
  return getBreadcrumbItems(location.pathname)
}
