import { apiGet, apiPut, apiDelete } from './apiService'
import { API_ENDPOINTS } from './endpoints'
import type { ResumeListFilters, ResumeUpdateData } from '../../pages/Resumes/types'

export async function getResumes(filters: ResumeListFilters) {
  const params: Record<string, string | number> = {
    page: filters.page,
    limit: filters.limit,
    sort_by: filters.sort_by,
    sort_order: filters.sort_order,
  }

  if (filters.search) params.search = filters.search
  if (filters.status) params.status = filters.status
  if (filters.template) params.template = filters.template
  if ('user_id' in filters && filters.user_id) params.user_id = filters.user_id

  return apiGet(API_ENDPOINTS.PROCS_RESUMES, { params })
}

export async function getResumeStats() {
  return apiGet(API_ENDPOINTS.PROCS_RESUME_STATS)
}

export async function getResumeDetail(resumeId: string) {
  return apiGet(API_ENDPOINTS.PROCS_RESUME_BY_ID(resumeId))
}

export async function updateResume(resumeId: string, data: ResumeUpdateData) {
  return apiPut(API_ENDPOINTS.PROCS_RESUME_BY_ID(resumeId), data)
}

export async function deleteResume(resumeId: string) {
  return apiDelete(API_ENDPOINTS.PROCS_RESUME_BY_ID(resumeId))
}

export async function getTemplates() {
  return apiGet(API_ENDPOINTS.PROCS_RESUME_TEMPLATES)
}

export async function getTemplateStats() {
  return apiGet(API_ENDPOINTS.PROCS_RESUME_TEMPLATE_STATS)
}
