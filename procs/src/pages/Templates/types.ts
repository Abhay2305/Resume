export interface TemplateCmsItem {
  id: string
  name: string
  slug: string | null
  description: string | null
  category: string
  thumbnail_url: string | null
  preview_images: string[] | null
  color_scheme: Record<string, string>
  layout_schema: Record<string, unknown>
  template_definition: Record<string, unknown> | null
  theme: string | null
  fonts: Record<string, string> | null
  colors: Record<string, string> | null
  status: 'draft' | 'published' | 'archived' | 'deprecated'
  version: number
  author: string | null
  is_default: boolean
  sort_order: number
  tags: string[] | null
  usage_count: number
  metadata_json: Record<string, unknown> | null
  created_at: string
  updated_at: string | null
  published_at: string | null
}

export interface TemplateCmsListResponse {
  success: boolean
  items: TemplateCmsItem[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface TemplateCmsDetailResponse {
  success: boolean
  data: TemplateCmsItem
}

export interface TemplateVersion {
  id: string
  template_id: string
  version: number
  snapshot: Record<string, unknown>
  created_at: string
}

export interface TemplateVersionListResponse {
  success: boolean
  items: TemplateVersion[]
  total: number
}

export interface TemplateCmsFilters {
  search: string
  category: string | null
  status: string | null
  page: number
  limit: number
}

export interface TemplateFormData {
  name: string
  slug: string
  description: string
  category: string
  status: 'draft' | 'published' | 'archived'
  layout: 'single-column' | 'two-column-left' | 'two-column-right'
  headerStyle: 'left' | 'center' | 'banner'
  fontFamily: string
  primaryColor: string
  secondaryColor: string
  accentColor: string
  backgroundColor: string
  textColor: string
  margins: string
  sectionOrder: string[]
  sidebarSections: string[]
}
