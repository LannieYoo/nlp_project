import { useState, useRef, useCallback, useEffect } from 'react'

export default function PdfViewer({ bookId, pageIdx, highlight, onClose }) {
  const [numPages, setNumPages] = useState(null)
  const [currentPage, setCurrentPage] = useState(pageIdx || 0)
  const [scale, setScale] = useState(2.0)
  const [pageInputValue, setPageInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const containerRef = useRef(null)
  const imgRef = useRef(null)

  // Fetch page count on book change
  useEffect(() => {
    if (!bookId) return
    fetch(`/api/page-count/${bookId}`)
      .then(r => r.json())
      .then(data => setNumPages(data.page_count))
      .catch(() => setNumPages(null))
  }, [bookId])

  // Navigate to highlighted page when source changes
  useEffect(() => {
    if (pageIdx != null) {
      setCurrentPage(pageIdx)
      setPageInputValue('')
    }
  }, [pageIdx, bookId])

  // Build image URL
  const buildImageUrl = useCallback((page, withHighlight = true) => {
    let url = `/api/page-image/${bookId}/${page}?scale=${scale}`
    if (withHighlight && highlight && page === pageIdx) {
      url += `&hl_x=${highlight.x}&hl_y=${highlight.y}&hl_w=${highlight.width}&hl_h=${highlight.height}`
    }
    return url
  }, [bookId, scale, highlight, pageIdx])

  const goToPage = (p) => {
    const pg = Math.max(0, Math.min(p, (numPages || 1) - 1))
    setCurrentPage(pg)
  }

  const handlePageInput = (e) => {
    if (e.key === 'Enter') {
      const p = parseInt(pageInputValue)
      if (!isNaN(p)) goToPage(p)
      setPageInputValue('')
    }
  }

  // Display page number (0-based internally, 1-based for display is optional, 
  // but user sees actual PDF page indices)
  const displayPage = currentPage

  if (!bookId) {
    return (
      <div className="h-full flex flex-col items-center justify-center px-8 text-center" style={{ background: '#f0f0f0' }}>
        <div className="w-16 h-16 rounded-2xl bg-white shadow-soft flex items-center justify-center mb-4">
          <svg className="w-7 h-7 text-neutral-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
        </div>
        <p className="text-sm font-semibold text-neutral-500 mb-1">No PDF Selected</p>
        <p className="text-xs text-neutral-400">Click "View PDF" on a source to open the book here</p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-3 py-2 toolbar-bg flex-shrink-0">
        {/* Close on mobile */}
        {onClose && (
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-neutral-100 text-neutral-400 hover:text-neutral-600 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}

        {/* Book info */}
        <div className="flex-1 min-w-0">
          <span className="text-xs font-semibold text-neutral-600 truncate block">
            {bookId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </span>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage <= 0}
            className="p-1.5 rounded-lg hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-neutral-500"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div className="flex items-center gap-1 text-xs text-neutral-500">
            <input
              type="text"
              value={pageInputValue || displayPage}
              onChange={e => setPageInputValue(e.target.value)}
              onKeyDown={handlePageInput}
              onFocus={() => setPageInputValue(String(displayPage))}
              onBlur={() => setPageInputValue('')}
              className="w-10 text-center bg-neutral-100 border border-neutral-200 rounded-lg px-1 py-0.5 text-xs text-neutral-700
                         focus:outline-none focus:border-accent-400 focus:ring-1 focus:ring-accent-100"
            />
            <span className="text-neutral-400">/ {numPages ? numPages - 1 : '—'}</span>
          </div>

          <button
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage >= (numPages || 1) - 1}
            className="p-1.5 rounded-lg hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-neutral-500"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Zoom */}
        <div className="flex items-center gap-0.5 ml-2 bg-neutral-100 rounded-lg p-0.5">
          <button
            onClick={() => setScale(s => Math.max(0.5, +(s - 0.25).toFixed(2)))}
            className="p-1 rounded-md hover:bg-white transition-colors text-xs text-neutral-500 hover:text-neutral-700 font-bold leading-none"
          >−</button>
          <span className="text-[10px] text-neutral-500 w-9 text-center font-medium">
            {scale.toFixed(1)}x
          </span>
          <button
            onClick={() => setScale(s => Math.min(4, +(s + 0.25).toFixed(2)))}
            className="p-1 rounded-md hover:bg-white transition-colors text-xs text-neutral-500 hover:text-neutral-700 font-bold leading-none"
          >+</button>
        </div>

        {/* Go to highlighted page */}
        {highlight && currentPage !== pageIdx && (
          <button
            onClick={() => goToPage(pageIdx)}
            className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-600 border border-amber-200 text-[10px] font-semibold
                       hover:bg-amber-100 transition-colors"
          >
            ↗ p.{pageIdx}
          </button>
        )}
      </div>

      {/* PDF Image Container */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto flex justify-center"
        style={{ background: '#ebebeb' }}
      >
        {error ? (
          <div className="flex items-center justify-center h-full text-red-500 text-sm px-4">{error}</div>
        ) : (
          <div className="my-4 relative inline-block">
            <img
              ref={imgRef}
              src={buildImageUrl(currentPage)}
              alt={`Page ${displayPage}`}
              onLoad={() => setLoading(false)}
              onError={() => { setLoading(false); setError(`Failed to load page ${displayPage}`) }}
              className="block max-w-full rounded shadow-lg"
              style={{ minHeight: '200px' }}
            />
            {loading && (
              <div className="absolute inset-0 flex items-center justify-center bg-white/60">
                <div className="spinner" />
                <span className="ml-2 text-sm text-neutral-400">Loading…</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
