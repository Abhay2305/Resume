export interface ResumeListItem {
  id: string
  title: string
  user_id: string
  user_email: string
  user_name: string | null
  template_id: string
  template_name: string
  status: 'draft' | 'published'
  section_count: number
  version_count: number
  created_at: string
  updated_at: string
}

export interface ResumeListResponse {
  items: ResumeListItem[]
  total: number
  page: number
  limit: number
}

export interface ResumeListFilters {
  search: string
  status: string | null
  template: string | null
  user_id?: string
  sort_by: string
  sort_order: 'asc' | 'desc'
  page: number
  limit: number
}

export interface ResumeSection {
  id: string
  section_type: string
  content: Record<string, unknown>
  position: number
}

export interface ResumeVersion {
  id: string
  version_number: number
  created_at: string
}

export interface ResumeDetail {
  id: string
  title: string
  user_id: string
  user_email: string
  user_name: string | null
  template_id: string
  template_name: string
  template_category: string
  status: 'draft' | 'published'
  sections: ResumeSection[]
  versions: ResumeVersion[]
  created_at: string
  updated_at: string
}

export interface ResumeStats {
  total_resumes: number
  draft_count: number
  published_count: number
  templates: TemplateUsage[]
}

export interface TemplateUsage {
  template_id: string
  template_name: string
  count: number
}

export interface TemplateListItem {
  id: string
  name: string
  category: string
  preview_image?: string
  created_at?: string
}

export interface TemplateStatsItem {
  template_id: string
  template_name: string
  count: number
}

export interface TemplateStatsResponse {
  items: TemplateStatsItem[]
}

export interface ResumeUpdateData {
  title?: string
  template_id?: string
  status?: 'draft' | 'published'
}
