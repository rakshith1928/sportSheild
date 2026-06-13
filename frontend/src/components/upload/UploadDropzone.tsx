'use client'

import { useState, useRef } from 'react'
import { submitAssetUpload } from '@/actions/upload'
import { useRouter } from 'next/navigation'

export function UploadDropzone() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isDragActive, setIsDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true)
    } else if (e.type === 'dragleave') {
      setIsDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!file) return

    setIsUploading(true)
    setError(null)

    const formData = new FormData(e.currentTarget)
    formData.set('file', file) // Force the captured file (drag-and-drop or click)

    // Using Server Action
    const res = await submitAssetUpload(formData)
    
    if (res.success) {
      setFile(null)
      router.push('/dashboard/assets') // Go to Assets Library
    } else {
      setError(res.error || 'Upload failed')
      setIsUploading(false)
    }
  }

  return (
    <div className="bg-[#111415] border border-white/5 rounded-xl p-6">
      <h2 className="text-xl font-bold text-white mb-6">Upload & Protect Asset</h2>
      
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* Dropzone Area */}
        <div 
          className={`relative w-full h-64 border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-all cursor-pointer overflow-hidden
            ${isDragActive ? 'border-[#FF6B6B] bg-[#FF6B6B]/5' : 'border-slate-800 hover:border-slate-700'}
            ${file ? 'bg-slate-900/50' : ''}
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            name="file"
            className="hidden"
            onChange={handleFileSelect}
            accept="image/*,video/*"
          />

          {file ? (
            <div className="text-center z-10 w-full px-4">
              <div className="w-16 h-16 mx-auto mb-4 bg-emerald-500/10 text-emerald-500 rounded-full flex items-center justify-center">
                <span className="material-symbols-outlined text-3xl">check_circle</span>
              </div>
              <p className="text-white font-medium truncate max-w-sm mx-auto">{file.name}</p>
              <p className="text-slate-500 text-sm mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
              <button 
                type="button" 
                onClick={(e) => { e.stopPropagation(); setFile(null); fileInputRef.current!.value = ''; }}
                className="mt-4 text-sm text-[#FF6B6B] hover:text-[#e85d5d] transition-colors"
                disabled={isUploading}
              >
                Remove file
              </button>
            </div>
          ) : (
            <div className="text-center z-10 pointer-events-none">
              <div className="w-16 h-16 mx-auto mb-4 bg-slate-800 text-slate-400 rounded-full flex items-center justify-center transition-colors">
                <span className="material-symbols-outlined text-3xl">cloud_upload</span>
              </div>
              <p className="text-white font-medium mb-1">Click or drop a file to upload</p>
              <p className="text-slate-500 text-sm">Supports MP4, JPEG, PNG, WEBP (Max 50MB)</p>
            </div>
          )}

          {/* Animated uploading state overlay */}
          {isUploading && (
            <div className="absolute inset-0 bg-[#111415]/90 backdrop-blur-sm flex flex-col items-center justify-center z-20">
              <div className="w-12 h-12 border-4 border-slate-800 border-t-[#FF6B6B] rounded-full animate-spin mb-4"></div>
              <p className="text-white font-medium animate-pulse">Fingerprinting Asset...</p>
              <p className="text-slate-400 text-sm mt-1">Extracting AI features & uploading to vault</p>
            </div>
          )}
        </div>

        {/* Metadata Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Sport Category <span className="text-[#FF6B6B]">*</span></label>
            <select name="sport" required disabled={isUploading} className="w-full bg-[#1A1D1E] border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#FF6B6B] transition-colors appearance-none">
              <option value="">Select sport...</option>
              <option value="Football">Football</option>
              <option value="Basketball">Basketball</option>
              <option value="Baseball">Baseball</option>
              <option value="Soccer">Soccer</option>
              <option value="Tennis">Tennis</option>
            </select>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Team / Franchise <span className="text-[#FF6B6B]">*</span></label>
            <input type="text" name="team" required disabled={isUploading} placeholder="e.g., Lakers, Real Madrid" className="w-full bg-[#1A1D1E] border border-slate-800 rounded-lg px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-[#FF6B6B] transition-colors" />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Event Name</label>
            <input type="text" name="event" disabled={isUploading} placeholder="e.g., Finals Game 4" className="w-full bg-[#1A1D1E] border border-slate-800 rounded-lg px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-[#FF6B6B] transition-colors" />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Match Date</label>
            <input type="date" name="date" disabled={isUploading} className="w-full bg-[#1A1D1E] border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#FF6B6B] transition-colors [&::-webkit-calendar-picker-indicator]:filter [&::-webkit-calendar-picker-indicator]:invert" />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300">Asset Description</label>
          <textarea name="description" disabled={isUploading} rows={3} placeholder="Describe the clip or image (internal use only)" className="w-full bg-[#1A1D1E] border border-slate-800 rounded-lg px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-[#FF6B6B] transition-colors resize-none"></textarea>
        </div>

        <div className="pt-4 flex justify-end">
          <button 
            type="submit" 
            disabled={!file || isUploading}
            className={`px-8 py-3 rounded-lg font-medium text-white transition-all
              ${!file || isUploading 
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                : 'bg-[#FF6B6B] hover:bg-[#e85d5d] shadow-[0_0_20px_rgba(255,107,107,0.3)]'}
            `}
          >
            {isUploading ? 'Processing...' : 'Upload & Fingerprint'}
          </button>
        </div>
      </form>
    </div>
  )
}
