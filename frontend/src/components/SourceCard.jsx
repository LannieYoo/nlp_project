import { useState } from 'react'

export default function SourceCard({ source, index, onViewPdf, isActive }) {
  const [expanded, setExpanded] = useState(index === 0)
  const bookName = source.book_id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

  return (
    <div className={`source-card ${isActive ? 'active' : ''} rounded-xl overflow-hidden`}>
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2.5 px-4 py-3 text-left hover:bg-neutral-50 transition-colors"
      >
        <span className="flex items-center justify-center w-5 h-5 rounded-md bg-neutral-100 text-neutral-500 text-[10px] font-bold flex-shrink-0">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-semibold text-neutral-700 truncate">{bookName}</div>
          <div className="text-[10px] text-neutral-400 truncate mt-0.5">
            p.{source.page_idx}{source.chapter ? ` · ${source.chapter.slice(0, 45)}` : ''}
          </div>
        </div>
        <span className="px-2 py-0.5 rounded-full text-[9px] font-semibold bg-neutral-100 text-neutral-400 flex-shrink-0">
          {source.method === 'rrf_fusion' ? 'fusion' : source.method?.split('_')[0] || '—'}
        </span>
        <svg
          className={`w-3.5 h-3.5 text-neutral-400 transition-transform flex-shrink-0 ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded */}
      {expanded && (
        <div className="px-4 pb-4 animate-fade-in">
          <div className="flex flex-wrap gap-3 text-[10px] text-neutral-400 mb-2.5">
            <span className="flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              Page {source.page_idx}
            </span>
            <span>Score: {source.score?.toFixed(4)}</span>
          </div>

          {source.text_preview && (
            <div className="bg-neutral-50 rounded-lg p-3 mb-3 border border-neutral-100">
              <p className="text-[11px] text-neutral-500 leading-relaxed line-clamp-4">
                {source.text_preview}
              </p>
            </div>
          )}

          {source.book_id && (
            <button
              onClick={(e) => { e.stopPropagation(); onViewPdf(source) }}
              className={`
                flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all
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
              View PDF (p.{source.page_idx})
            </button>
          )}
        </div>
      )}
    </div>
  )
}
