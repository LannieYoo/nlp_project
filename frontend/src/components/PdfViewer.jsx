import { useState, useRef, useCallback, useEffect } from 'react'
import { getBookTitle } from '../utils/bookMeta'

export default function PdfViewer({ bookId, pageIdx, highlight, onClose }) {
  const [numPages, setNumPages] = useState(null)
  const [currentPage, setCurrentPage] = useState(pageIdx || 0)
  const [scale, setScale] = useState(2.0)
  const [pageInputValue, setPageInputValue] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchResults, setSearchResults] = useState(null)
  const [searchLoading, setSearchLoading] = useState(false)
  const containerRef = useRef(null)
  const imgRef = useRef(null)
  const searchInputRef = useRef(null)

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
      setError(null)
    }
  }, [pageIdx, bookId])

  // Focus search input when opened
  useEffect(() => {
    if (searchOpen && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [searchOpen])

  // Ctrl+F shortcut
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        setSearchOpen(true)
      }
      if (e.key === 'Escape') {
        setSearchOpen(false)
        setSearchResults(null)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Scroll-to-change-page: when user scrolls past top/bottom, change page
  useEffect(() => {
    const container = containerRef.current
    if (!container || !numPages) return

    let scrollTimeout = null
    const handleWheel = (e) => {
      const { scrollTop, scrollHeight, clientHeight } = container
      const atBottom = scrollTop + clientHeight >= scrollHeight - 5
      const atTop = scrollTop <= 5

      if (atBottom && e.deltaY > 0 && currentPage < numPages - 1) {
        e.preventDefault()
        if (!scrollTimeout) {
          scrollTimeout = setTimeout(() => { scrollTimeout = null }, 400)
          setCurrentPage(p => Math.min(p + 1, numPages - 1))
          setError(null)
          setLoading(true)
          container.scrollTop = 0
        }
      } else if (atTop && e.deltaY < 0 && currentPage > 0) {
        e.preventDefault()
        if (!scrollTimeout) {
          scrollTimeout = setTimeout(() => { scrollTimeout = null }, 400)
          setCurrentPage(p => Math.max(p - 1, 0))
          setError(null)
          setLoading(true)
          container.scrollTop = 0
        }
      }
    }

    container.addEventListener('wheel', handleWheel, { passive: false })
    return () => container.removeEventListener('wheel', handleWheel)
  }, [numPages, currentPage])

  // Build image URL
  const buildImageUrl = useCallback((page, withHighlight = true) => {
    let url = `/api/page-image/${bookId}/${page}?scale=${scale}`
    if (withHighlight && highlight && page === pageIdx) {
      url += `&hl_x=${highlight.x}&hl_y=${highlight.y}&hl_w=${highlight.width}&hl_h=${highlight.height}`
    }
    if (searchOpen && searchQuery.trim().length > 0) {
      url += `&sq=${encodeURIComponent(searchQuery.trim())}`
    }
    return url
  }, [bookId, scale, highlight, pageIdx, searchOpen, searchQuery])

  const goToPage = (p) => {
    const pg = Math.max(0, Math.min(p, (numPages || 1) - 1))
    setCurrentPage(pg)
    setError(null)
    setLoading(true)
    if (containerRef.current) containerRef.current.scrollTop = 0
  }

  const handlePageInput = (e) => {
    if (e.key === 'Enter') {
      const p = parseInt(pageInputValue)
      if (!isNaN(p)) goToPage(p - 1)  // User enters 1-based, convert to 0-based
      setPageInputValue('')
    }
  }

  // Text search in book
  const handleSearch = async (query) => {
    const q = query ?? searchQuery
    if (!q.trim() || !bookId) return
    setSearchLoading(true)
    try {
      const res = await fetch(`/api/search-in-book/${bookId}?q=${encodeURIComponent(q.trim())}`)
      if (res.ok) {
        const data = await res.json()
        setSearchResults(data)
      }
    } catch { /* ignore */ }
    setSearchLoading(false)
  }

  // Debounced auto-search as user types (autocomplete effect)
  useEffect(() => {
    if (!searchOpen || !bookId || searchQuery.trim().length < 3) {
      return
    }
    const timer = setTimeout(() => {
      handleSearch(searchQuery)
    }, 500)
    return () => clearTimeout(timer)
  }, [searchQuery, bookId, searchOpen])

  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch()
    if (e.key === 'Escape') {
      setSearchOpen(false)
      setSearchResults(null)
    }
  }

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

  // Highlight matched terms in the search snippet
  const highlightMatch = (text, q) => {
    if (!q || !q.trim()) return text
    const idx = text.toLowerCase().indexOf(q.toLowerCase())
    if (idx === -1) return text
    const before = text.slice(0, idx)
    const match = text.slice(idx, idx + q.length)
    const after = text.slice(idx + q.length)
    return (
      <>
        {before}
        <strong className="text-accent-700 bg-accent-100 rounded px-0.5 border-b-[2px] border-accent-400">{match}</strong>
        {after}
      </>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-3 py-2 toolbar-bg flex-shrink-0">
        {onClose && (
          <button onClick={onClose}
            className="p-1.5 mr-1 rounded-lg hover:bg-neutral-200 bg-neutral-100 text-neutral-500 hover:text-neutral-700 transition-colors"
            title="Close PDF Viewer">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}

        <div className="flex-1 min-w-0">
          <span className="text-xs font-semibold text-neutral-600 truncate block">
            {getBookTitle(bookId)}
          </span>
        </div>

        <button
          onClick={() => setSearchOpen(!searchOpen)}
          className={`p-1.5 rounded-lg transition-colors ${searchOpen ? 'bg-accent-100 text-accent-600' : 'hover:bg-neutral-100 text-neutral-400'}`}
          title="Search in book (Ctrl+F)">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>

        <div className="flex items-center gap-1">
          <button onClick={() => goToPage(currentPage - 1)} disabled={currentPage <= 0}
            className="p-1.5 rounded-lg hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-neutral-500">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div className="flex items-center gap-1 text-xs text-neutral-500">
            <input type="text"
              value={pageInputValue || (currentPage + 1)}
              onChange={e => setPageInputValue(e.target.value)}
              onKeyDown={handlePageInput}
              onFocus={() => setPageInputValue(String(currentPage + 1))}
              onBlur={() => setPageInputValue('')}
              className="w-10 text-center bg-neutral-100 border border-neutral-200 rounded-lg px-1 py-0.5 text-xs text-neutral-700
                         focus:outline-none focus:border-accent-400 focus:ring-1 focus:ring-accent-100" />
            <span className="text-neutral-400">/ {numPages || '—'}</span>
          </div>

          <button onClick={() => goToPage(currentPage + 1)} disabled={currentPage >= (numPages || 1) - 1}
            className="p-1.5 rounded-lg hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-neutral-500">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div className="flex items-center gap-0.5 ml-2 bg-neutral-100 rounded-lg p-0.5">
          <button onClick={() => setScale(s => Math.max(0.5, +(s - 0.25).toFixed(2)))}
            className="p-1 rounded-md hover:bg-white transition-colors text-xs text-neutral-500 hover:text-neutral-700 font-bold leading-none">−</button>
          <span className="text-[10px] text-neutral-500 w-9 text-center font-medium">{scale.toFixed(1)}x</span>
          <button onClick={() => setScale(s => Math.min(4, +(s + 0.25).toFixed(2)))}
            className="p-1 rounded-md hover:bg-white transition-colors text-xs text-neutral-500 hover:text-neutral-700 font-bold leading-none">+</button>
        </div>

        {highlight && currentPage !== pageIdx && (
          <button onClick={() => goToPage(pageIdx)}
            className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-600 border border-amber-200 text-[10px] font-semibold hover:bg-amber-100 transition-colors">
            ↗ p.{pageIdx + 1}
          </button>
        )}
      </div>

      {/* Search bar */}
      {searchOpen && (
        <div className="px-3 py-2.5 border-b-2 border-accent-200 animate-fade-in"
          style={{ background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)' }}>
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-accent-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input ref={searchInputRef} type="text" value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)} onKeyDown={handleSearchKeyDown}
                placeholder="Search text in this book…"
                className="w-full pl-8 pr-3 py-1.5 bg-white rounded-lg border-2 border-accent-200 text-xs text-neutral-700
                           placeholder:text-neutral-300 focus:outline-none focus:border-accent-400 focus:ring-2 focus:ring-accent-100 transition-all" />
            </div>
            <button onClick={handleSearch} disabled={searchLoading || !searchQuery.trim()}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold btn-primary disabled:opacity-50">
              {searchLoading ? '…' : 'Find'}
            </button>
            <button onClick={() => { setSearchOpen(false); setSearchResults(null) }}
              className="p-1.5 rounded-lg hover:bg-white/60 text-neutral-400 hover:text-neutral-600 transition-colors">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {searchResults && (
            <div className="mt-2.5">
              {searchResults.results?.length > 0 ? (
                <>
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="text-[10px] font-bold text-accent-600 uppercase tracking-wider">
                      {searchResults.total} result{searchResults.total > 1 ? 's' : ''} found
                    </span>
                    <span className="text-[10px] text-neutral-400">for "{searchResults.query}"</span>
                  </div>
                  <div className="max-h-36 overflow-y-auto rounded-lg bg-white border border-accent-100 shadow-sm divide-y divide-neutral-50">
                    {searchResults.results.map((r, i) => (
                      <button key={i} onClick={() => goToPage(r.page_idx)}
                        className={`w-full flex items-start gap-2.5 px-3 py-2 text-left text-[11px] transition-all
                          ${currentPage === r.page_idx
                            ? 'bg-accent-50 text-accent-800 border-l-[3px] border-l-accent-500'
                            : 'hover:bg-blue-50/50 text-neutral-600 border-l-[3px] border-l-transparent hover:border-l-accent-200'}`}>
                        <span className="font-bold text-accent-500 w-8 flex-shrink-0 mt-0.5">p.{r.page_idx + 1}</span>
                        <span className="leading-relaxed">{highlightMatch(r.snippet, searchResults.query)}</span>
                      </button>
                    ))}
                  </div>
                </>
              ) : (
                <div className="flex items-center gap-2.5 py-3 px-4 rounded-lg bg-white border border-orange-200 shadow-sm">
                  <svg className="w-5 h-5 text-orange-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <div>
                    <p className="text-xs font-semibold text-neutral-700">No results found for "{searchResults.query}"</p>
                    <p className="text-[10px] text-neutral-400 mt-0.5">The keyword was not found in any page of this book. Try a different term.</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Loading progress bar */}
      {loading && (
        <div className="h-1 flex-shrink-0 bg-neutral-200 overflow-hidden">
          <div className="h-full bg-accent-500 rounded-r-full animate-loading-bar" />
        </div>
      )}

      {/* Scroll hint */}
      <div className="text-center py-0.5 bg-neutral-100/80 text-[9px] text-neutral-400 flex-shrink-0 select-none">
        Page {currentPage + 1}{numPages ? ` of ${numPages}` : ''} · Scroll down to go to next page
      </div>

      {/* PDF Image Container — single page, scroll to change */}
      <div ref={containerRef} className="flex-1 overflow-auto flex justify-center" style={{ background: '#ebebeb' }}>
        {error ? (
          <div className="flex flex-col items-center justify-center h-full px-4 gap-3">
            <p className="text-red-500 text-sm">{error}</p>
            <button
              onClick={() => { setError(null); setLoading(true) }}
              className="px-4 py-1.5 rounded-lg bg-accent-50 text-accent-600 border border-accent-200 text-xs font-semibold hover:bg-accent-100 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : (
          <div key={`${bookId}-${currentPage}-${scale}-${searchOpen ? searchQuery : ''}`} className="my-4 relative inline-block">
            <img
              ref={imgRef}
              src={buildImageUrl(currentPage)}
              alt={`Page ${currentPage + 1}`}
              onLoad={() => setLoading(false)}
              onError={() => { setLoading(false); setError(`Failed to load page ${currentPage + 1}`) }}
              className={`block max-w-full rounded shadow-lg transition-opacity duration-300 ${loading ? 'opacity-40' : 'opacity-100'}`}
              style={{ minHeight: '200px' }}
            />
            {loading && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/70 rounded backdrop-blur-sm">
                <div className="w-10 h-10 rounded-full border-3 border-neutral-200 border-t-accent-500 animate-spin mb-2" />
                <span className="text-sm font-medium text-neutral-500">Loading page {currentPage + 1}…</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
