import { getAssets } from '@/utils/api'
import { UploadDropzone } from '@/components/upload/UploadDropzone'

export default async function AssetsPage() {
  const data = await getAssets()
  const assets = data?.assets || []

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Asset Vault</h1>
        <p className="text-slate-400 text-sm mt-1">
          Upload and manage your protected media assets. Every file is AI-fingerprinted upon upload.
        </p>
      </div>

      {/* Upload Form */}
      <UploadDropzone />

      {/* Library Grid */}
      <div className="pt-6">
        <h3 className="text-lg font-semibold text-white mb-4">Protected Assets ({assets.length})</h3>
        
        {assets.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {assets.map((asset: any) => (
              <div key={asset.asset_id} className="bg-[#111415] border border-white/5 rounded-xl overflow-hidden group hover:border-[#FF6B6B]/30 transition-colors">
                <div className="h-40 bg-slate-900 relative">
                  {/* Thumbnail Preview */}
                  {asset.content_type?.startsWith('image/') ? (
                    <img 
                      src={asset.file_url} 
                      alt={asset.filename} 
                      className="w-full h-full object-cover" 
                    />
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center text-slate-600 bg-black">
                       <span className="material-symbols-outlined text-4xl mb-2">movie</span>
                       <span className="text-xs font-semibold">VIDEO</span>
                    </div>
                  )}
                  {/* Status Badge */}
                  <div className="absolute top-2 right-2 px-2 py-1 bg-emerald-500/90 backdrop-blur text-white text-[10px] font-bold uppercase tracking-wider rounded border border-emerald-400/20 shadow-lg">
                    Protected
                  </div>
                </div>
                
                <div className="p-4 space-y-3">
                  <h4 className="text-white font-medium text-sm truncate" title={asset.original_filename || asset.filename}>
                    {asset.original_filename || asset.filename}
                  </h4>
                  
                  <div className="flex flex-wrap gap-2">
                    {asset.sport && (
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] uppercase font-semibold">
                        {asset.sport}
                      </span>
                    )}
                    {asset.team && (
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-[#FF6B6B] text-[10px] uppercase font-semibold">
                        {asset.team}
                      </span>
                    )}
                  </div>
                  
                  <p className="text-xs text-slate-500 truncate" title={asset.description}>
                    {asset.description || 'No description provided'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 rounded-xl border border-dashed border-slate-800 bg-[#111415]/50">
            <span className="material-symbols-outlined text-5xl text-slate-700 mb-3">folder_open</span>
            <p className="text-white font-medium">Your vault is currently empty.</p>
            <p className="text-slate-500 text-sm mt-1">Upload an asset above to securely fingerprint it.</p>
          </div>
        )}
      </div>
    </div>
  )
}
