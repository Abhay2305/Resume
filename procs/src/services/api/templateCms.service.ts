import { apiGet, apiPost, apiPut, apiDelete } from './apiService'
import { API_ENDPOINTS } from './endpoints'

export async function getTemplatesCms(params?: Record<string, string | number | boolean | undefined>) {
  return apiGet(API_ENDPOINTS.PROCS_TEMPLATES, { params })
}

export async function getTemplateDetail(id: string) {
  return apiGet(API_ENDPOINTS.PROCS_TEMPLATE_BY_ID(id))
}

export async function createTemplate(data: Record<string, unknown>) {
  return apiPost(API_ENDPOINTS.PROCS_TEMPLATES, data)
}

export async function updateTemplate(id: string, data: Record<string, unknown>) {
  return apiPut(API_ENDPOINTS.PROCS_TEMPLATE_BY_ID(id), data)
}

export async function deleteTemplate(id: string) {
  return apiDelete(API_ENDPOINTS.PROCS_TEMPLATE_BY_ID(id))
}

export async function publishTemplate(id: string) {
  return apiPost(API_ENDPOINTS.PROCS_TEMPLATE_PUBLISH(id))
}

export async function archiveTemplate(id: string) {
  return apiPost(API_ENDPOINTS.PROCS_TEMPLATE_ARCHIVE(id))
}

export async function deprecateTemplate(id: string) {
  return apiPost(API_ENDPOINTS.PROCS_TEMPLATE_DEPRECATE(id))
}

export async function duplicateTemplate(id: string, data: { new_id: string; new_name?: string }) {
  return apiPost(API_ENDPOINTS.PROCS_TEMPLATE_DUPLICATE(id), data)
}

export async function getTemplateVersions(id: string) {
  return apiGet(API_ENDPOINTS.PROCS_TEMPLATE_VERSIONS(id))
}

export async function restoreTemplateVersion(id: string, versionId: string) {
  return apiPost(API_ENDPOINTS.PROCS_TEMPLATE_RESTORE(id, versionId))
}

export async function reorderTemplates(templateIds: string[]) {
  return apiPost(API_ENDPOINTS.PROCS_TEMPLATE_REORDER, { template_ids: templateIds })
}

export async function uploadTemplateFile(id: string, type: 'thumbnail' | 'preview' | 'definition', file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const endpoint = type === 'thumbnail'
    ? API_ENDPOINTS.PROCS_TEMPLATE_UPLOAD_THUMBNAIL(id)
    : type === 'preview'
    ? API_ENDPOINTS.PROCS_TEMPLATE_UPLOAD_PREVIEW(id)
    : API_ENDPOINTS.PROCS_TEMPLATE_UPLOAD_DEFINITION(id)
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('procs_token') || ''}`,
    },
    body: formData,
  })
  return response.json()
}

export async function getPublishedTemplates() {
  return apiGet(API_ENDPOINTS.PROCS_TEMPLATES_PUBLISHED)
}
