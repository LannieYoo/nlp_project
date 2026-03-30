import { useState, useRef, useCallback, useEffect } from 'react'
import { getBookTitle } from '../utils/bookMeta'

export default function BookSpreadViewer({ bookId, initialPage, numPages, onClose }) {
  const [currentPage, setCurrentPage] = useState(() => {
    // Snap to even page (left side of spread)
    const p = initialPage || 0
    return p % 2 !== 0 ? Math.max(0, p - 1) : p
  })
  const [zoom, setZoom] = useState(1.0)
  const [singlePage, setSinglePage] = useState(false)
  const [loadingLeft, setLoadingLeft] = useState(true)
  const [loadingRight, setLoadingRight] = useState(true)
  const [errorLeft, setErrorLeft] = useState(false)
  const [errorRight, setErrorRight] = useState(false)
  const [pageInputValue, setPageInputValue] = useState('')
  const [retryKey, setRetryKey] = useState(0)
  const containerRef = useRef(null)

  const totalPages = numPages || 1
  const API_SCALE = 4.0  // High-quality render scale for zoom support

  const pageStep = singlePage ? 1 : 2

  // Keyboard nav: arrows + escape
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault()
        goToPage(currentPage + pageStep)
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault()
        goToPage(currentPage - pageStep)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentPage, pageStep])

  // Scroll to turn pages
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    let scrollTimeout = null
    const handleWheel = (e) => {
      // Don't intercept scroll when zoomed in (let user scroll the content)
      if (zoom > 1.0) return

      const { scrollTop, scrollHeight, clientHeight } = container
      const atBottom = scrollTop + clientHeight >= scrollHeight - 5
      const atTop = scrollTop <= 5

      if (atBottom && e.deltaY > 0 && currentPage + 2 < totalPages) {
        e.preventDefault()
        if (!scrollTimeout) {
          scrollTimeout = setTimeout(() => { scrollTimeout = null }, 400)
          goToPage(currentPage + pageStep)
        }
      } else if (atTop && e.deltaY < 0 && currentPage > 0) {
        e.preventDefault()
        if (!scrollTimeout) {
          scrollTimeout = setTimeout(() => { scrollTimeout = null }, 400)
          goToPage(currentPage - pageStep)
        }
      }
    }

    container.addEventListener('wheel', handleWheel, { passive: false })
    return () => container.removeEventListener('wheel', handleWheel)
  }, [currentPage, totalPages, zoom, pageStep])

  // Prevent body scroll when overlay is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = '' }
  }, [])

  const buildImageUrl = useCallback((page) => {
    return `/api/page-image/${bookId}/${page}?scale=${API_SCALE}`
  }, [bookId])

  const goToPage = (p) => {
    let pg = Math.max(0, Math.min(p, totalPages - 1))
    // Snap to even page in 2-page mode
    if (!singlePage && pg % 2 !== 0) pg = Math.max(0, pg - 1)
    setCurrentPage(pg)
    setLoadingLeft(true)
    setLoadingRight(true)
    setErrorLeft(false)
    setErrorRight(false)
    if (containerRef.current) containerRef.current.scrollTop = 0
  }

  const retryImages = () => {
    setErrorLeft(false)
    setErrorRight(false)
    setLoadingLeft(true)
    setLoadingRight(true)
    setRetryKey(k => k + 1)
  }

  const handlePageInput = (e) => {
    if (e.key === 'Enter') {
      const p = parseInt(pageInputValue)
      if (!isNaN(p)) goToPage(p - 1)
      setPageInputValue('')
    }
  }

  const hasRightPage = !singlePage && currentPage + 1 < totalPages
  const isLoading = loadingLeft || (hasRightPage && loadingRight)
  const bookTitle = getBookTitle(bookId)

  return (
    <div className="book-spread-overlay" onClick={onClose}>
      <div className="book-spread-inner" onClick={e => e.stopPropagation()}>
        {/* Top toolbar */}
        <div className="book-spread-toolbar">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <button onClick={onClose}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white/80 hover:text-white transition-colors"
              title="Close (Esc)">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <div className="flex items-center gap-2 min-w-0">
              <svg className="w-4 h-4 text-white/50 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
              <span className="text-sm font-semibold text-white/90 truncate">{bookTitle}</span>
              <span className="text-xs text-white/40 flex-shrink-0">— Book View</span>
            </div>
          </div>

          {/* View mode toggle + page navigation */}
          <div className="flex items-center gap-2">
            {/* 1-page / 2-page toggle */}
            <div className="flex items-center gap-0.5 bg-white/10 rounded-lg p-0.5 mr-1">
              <button onClick={() => setSinglePage(false)}
                className={`p-1.5 rounded-md transition-colors text-[10px] font-bold leading-none ${
                  !singlePage ? 'bg-white/20 text-white' : 'text-white/40 hover:bg-white/10 hover:text-white/70'}`}
                title="Two-page spread">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <rect x="2" y="3" width="8" height="18" rx="1" />
                  <rect x="14" y="3" width="8" height="18" rx="1" />
                </svg>
              </button>
              <button onClick={() => setSinglePage(true)}
                className={`p-1.5 rounded-md transition-colors text-[10px] font-bold leading-none ${
                  singlePage ? 'bg-white/20 text-white' : 'text-white/40 hover:bg-white/10 hover:text-white/70'}`}
                title="Single page">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <rect x="5" y="3" width="14" height="18" rx="1" />
                </svg>
              </button>
            </div>

            <button onClick={() => goToPage(currentPage - pageStep)} disabled={currentPage <= 0}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-20 disabled:cursor-not-allowed text-white/80 hover:text-white transition-colors">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <div className="flex items-center gap-1.5 text-sm text-white/70">
              <input type="text"
                value={pageInputValue || (singlePage ? `${currentPage + 1}` : `${currentPage + 1}–${Math.min(currentPage + 2, totalPages)}`)}
                onChange={e => setPageInputValue(e.target.value)}
                onKeyDown={handlePageInput}
                onFocus={() => setPageInputValue(String(currentPage + 1))}
                onBlur={() => setPageInputValue('')}
                className="w-16 text-center bg-white/10 border border-white/20 rounded-lg px-2 py-1 text-sm text-white
                           focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/20 placeholder:text-white/30" />
              <span className="text-white/40">/ {totalPages}</span>
            </div>

            <button onClick={() => goToPage(currentPage + pageStep)} disabled={currentPage + pageStep >= totalPages}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-20 disabled:cursor-not-allowed text-white/80 hover:text-white transition-colors">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          {/* Right: zoom controls */}
          <div className="flex items-center gap-1 flex-1 justify-end">
            <div className="flex items-center gap-0.5 bg-white/10 rounded-lg p-0.5">
              <button onClick={() => setZoom(s => Math.max(0.5, +(s - 0.25).toFixed(2)))}
                className="p-1.5 rounded-md hover:bg-white/15 transition-colors text-sm text-white/70 hover:text-white font-bold leading-none">−</button>
              <span className="text-xs text-white/60 w-10 text-center font-medium">{zoom.toFixed(1)}x</span>
              <button onClick={() => setZoom(s => Math.min(3, +(s + 0.25).toFixed(2)))}
                className="p-1.5 rounded-md hover:bg-white/15 transition-colors text-sm text-white/70 hover:text-white font-bold leading-none">+</button>
            </div>

            <button onClick={() => setZoom(1.0)}
              className={`px-2 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-[10px] text-white/60 hover:text-white transition-colors font-medium ${zoom === 1.0 ? 'invisible' : ''}`}>
              Fit
            </button>
          </div>
        </div>

        {/* Loading bar */}
        {isLoading && (
          <div className="h-0.5 bg-white/10 overflow-hidden flex-shrink-0">
            <div className="h-full bg-accent-400 rounded-r-full animate-loading-bar" />
          </div>
        )}

        {/* Book spread content area */}
        <div ref={containerRef} className="book-spread-content">
          <div className="book-spread-pages">
            {/* Current page (always shown) */}
            <div className={singlePage ? 'book-page-single' : 'book-page-left'}>
              <div className="relative">
                {errorLeft ? (
                  <div className="book-page-img flex flex-col items-center justify-center bg-neutral-800" style={{minWidth:'280px',minHeight:'400px', borderRadius: singlePage ? '4px' : '4px 0 0 4px'}}>
                    <svg className="w-10 h-10 text-white/20 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="text-xs text-white/40 mb-2">Page {currentPage + 1} unavailable</span>
                    <button onClick={retryImages} className="px-3 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-white/60 text-[10px] transition-colors">Retry</button>
                  </div>
                ) : (
                  <img
                    key={`left-${currentPage}-${retryKey}`}
                    src={buildImageUrl(currentPage)}
                    alt={`Page ${currentPage + 1}`}
                    onLoad={() => setLoadingLeft(false)}
                    onError={() => { setLoadingLeft(false); setErrorLeft(true) }}
                    className={`book-page-img transition-opacity duration-300 ${loadingLeft ? 'opacity-30' : 'opacity-100'}`}
                    style={{
                      maxHeight: `${82 * zoom}vh`,
                      ...(singlePage ? { borderRadius: '4px', boxShadow: '0 6px 24px rgba(0,0,0,0.3)' } : {}),
                    }}
                  />
                )}
                {loadingLeft && !errorLeft && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="w-8 h-8 rounded-full border-2 border-white/20 border-t-white/70 animate-spin mb-2" />
                    <span className="text-xs text-white/50">Loading p.{currentPage + 1}</span>
                  </div>
                )}
                {!errorLeft && (
                  <div className="absolute bottom-3 left-3 bg-black/60 text-white text-[10px] px-2 py-0.5 rounded-full font-medium backdrop-blur-sm">
                    {currentPage + 1}
                  </div>
                )}
              </div>
            </div>

            {/* Spine + Right page: only in two-page mode */}
            {!singlePage && (
              <>
                <div className="book-spine" />
                <div className="book-page-right">
                  {hasRightPage ? (
                    <div className="relative">
                      {errorRight ? (
                        <div className="book-page-img flex flex-col items-center justify-center bg-neutral-800 rounded-r" style={{minWidth:'280px',minHeight:'400px'}}>
                          <svg className="w-10 h-10 text-white/20 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <span className="text-xs text-white/40 mb-2">Page {currentPage + 2} unavailable</span>
                          <button onClick={retryImages} className="px-3 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-white/60 text-[10px] transition-colors">Retry</button>
                        </div>
                      ) : (
                        <img
                          key={`right-${currentPage + 1}-${retryKey}`}
                          src={buildImageUrl(currentPage + 1)}
                          alt={`Page ${currentPage + 2}`}
                          onLoad={() => setLoadingRight(false)}
                          onError={() => { setLoadingRight(false); setErrorRight(true) }}
                          className={`book-page-img transition-opacity duration-300 ${loadingRight ? 'opacity-30' : 'opacity-100'}`}
                          style={{ maxHeight: `${82 * zoom}vh` }}
                        />
                      )}
                      {loadingRight && !errorRight && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <div className="w-8 h-8 rounded-full border-2 border-white/20 border-t-white/70 animate-spin mb-2" />
                          <span className="text-xs text-white/50">Loading p.{currentPage + 2}</span>
                        </div>
                      )}
                      {!errorRight && (
                        <div className="absolute bottom-3 right-3 bg-black/60 text-white text-[10px] px-2 py-0.5 rounded-full font-medium backdrop-blur-sm">
                          {currentPage + 2}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="book-page-end">
                      <svg className="w-8 h-8 text-white/20 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                        <path strokeLinecap="round" strokeLinejoin="round"
                          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                        />
                      </svg>
                      <span className="text-xs text-white/30 font-medium">End of Book</span>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
