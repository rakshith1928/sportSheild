'use server'

import { uploadAsset } from '@/utils/api'

export async function submitAssetUpload(formData: FormData) {
  try {
    const result = await uploadAsset(formData)
    return { success: true, data: result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
}
