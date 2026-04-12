import { useState, useEffect } from 'react'
import { getBookTitle, getBookAuthor } from '../utils/bookMeta'

const QualityIcon = ({ score, className = "w-3.5 h-3.5" }) => {
  if (score >= 0.7) return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
    </svg>
  )
  if (score >= 0.4) return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M12 2a10 10 0 100 20 10 10 0 000-20z" />
    </svg>
  )
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
}

export default function SourceCard({ group, index, onViewPdf, activeChunkId }) {
  const [expanded, setExpanded] = useState(index === 0)
  const [imgError, setImgError] = useState(false)
  
  // Reset imgError if the book changes, or to clear stale state from HMR
  useEffect(() => {
    setImgError(false)
  }, [group.book_id])
  
  const bookName = getBookTitle(group.book_id)
  const authorName = getBookAuthor(group.book_id)
  
  // Calculate best score and check if any item is active
  const bestScore = Math.max(...group.items.map(s => s.score || 0))
  const bestQuality = Math.max(...group.items.map(s => s.quality_score || 0))
  const isAnyActive = group.items.some(s => s.chunk_id === activeChunkId)

  return (
    <div className={`source-card ${isAnyActive ? 'active' : ''} rounded-xl overflow-hidden`}>
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-neutral-50 transition-colors"
      >
        {/* Actual Book Cover Thumbnail */}
        <div className="relative w-8 h-11 rounded-sm shadow-md flex-shrink-0 bg-neutral-200 overflow-hidden border border-neutral-300 flex items-center justify-center">
          {!imgError ? (
            <img 
              src={`/api/page-image/${group.book_id}/0?scale=0.5&_t=1`} 
              alt="Cover" 
              className="w-full h-full object-cover"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center">
              <span className="text-white text-[9px] font-bold">{index + 1}</span>
            </div>
          )}
        </div>
        
        <div className="flex-1 min-w-0 py-0.5">
          <div className="text-[13px] font-bold text-neutral-800 truncate" title={bookName}>{bookName}</div>
          <div className="text-[10px] text-neutral-400 truncate mt-0.5 flex items-center gap-1.5">
            <span className="font-medium text-neutral-600">{authorName}</span>
            <span className="w-0.5 h-0.5 rounded-full bg-neutral-300"></span>
            <span>{group.items.length} match{group.items.length > 1 ? 'es' : ''}</span>
            <span className="w-0.5 h-0.5 rounded-full bg-neutral-300"></span>
            <span className="font-bold text-neutral-600">Rank: {bestScore.toFixed(4)}</span>
            <>
              <span className="w-0.5 h-0.5 rounded-full bg-neutral-300"></span>
              <span className={`font-semibold flex items-center gap-0.5 ${
                bestQuality >= 0.7 ? 'text-emerald-500' : bestQuality >= 0.4 ? 'text-amber-500' : 'text-neutral-400'
              }`}>
                <QualityIcon score={bestQuality} className="w-2.5 h-2.5" />
                Quality: {bestQuality.toFixed(4)}
              </span>
            </>
          </div>
        </div>
        <svg
          className={`w-3.5 h-3.5 text-neutral-400 transition-transform flex-shrink-0 ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded */}
      {expanded && (
        <div className="px-4 pb-4 animate-fade-in space-y-4">
          {group.items.map((source, idx) => {
            const isActive = source.chunk_id === activeChunkId;
            return (
              <div key={source.chunk_id || idx} className="pl-2 border-l-2 border-neutral-100 mt-2 block">
                <div className="flex items-center gap-2 text-[10px] text-neutral-400 mb-1.5">
                  <span className="font-semibold text-neutral-500 whitespace-nowrap">Page {source.page_idx + 1}</span>
                  {source.chapter && <span className="truncate max-w-[150px]">· {source.chapter}</span>}
                  <span className="ml-auto flex items-center gap-1.5 flex-shrink-0">
                    <span className="px-1.5 py-0.5 rounded text-[8px] font-semibold bg-neutral-100 text-neutral-400">
                      {source.method === 'rrf_fusion' ? 'fusion' : source.method?.split('_')[0] || '—'}
                    </span>
                    <span className="font-bold text-neutral-600">Rank: {source.score?.toFixed(4)}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold flex items-center gap-0.5 ${
                      source.quality_score >= 0.7
                        ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                        : source.quality_score >= 0.4
                          ? 'bg-amber-50 text-amber-600 border border-amber-200'
                          : 'bg-neutral-50 text-neutral-400 border border-neutral-200'
                    }`}>
                      <QualityIcon score={source.quality_score || 0} className="w-2 h-2" />
                      Q: {(source.quality_score || 0)?.toFixed(2)}
                    </span>
                  </span>
                </div>

                {source.text_preview && (
                  <div className="bg-neutral-50 rounded-md p-2.5 mb-2 border border-neutral-100">
                    <p className="text-[11px] text-neutral-500 leading-relaxed line-clamp-3">
                      {source.text_preview}
                    </p>
                  </div>
                )}

                {source.book_id && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onViewPdf(source) }}
                    className={`
                      flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[11px] font-semibold transition-all w-fit
                      ${isActive
                        ? 'btn-primary'
                        : 'bg-accent-50 text-accent-600 hover:bg-accent-100 border border-accent-200'
                      }
                    `}
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                      <path strokeLinecap="round" strokeLinejoin="round"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    View PDF (p.{source.page_idx + 1})
                  </button>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
