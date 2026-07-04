// Shared Asset type for the reports module
export interface Asset {
  asset_id: string
  filename: string
  original_filename?: string
  file_url: string
  content_type?: string
  sport?: string
  team?: string
  description?: string
}
