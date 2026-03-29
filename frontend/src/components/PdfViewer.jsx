import { useState, useRef, useCallback, useEffect } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`

export default function PdfViewer({ bookId, pageIdx, highlight, onClose }) {
  const [numPages, setNumPages] = useState(null)
  const [currentPage, setCurrentPage] = useState(pageIdx || 1)
  const [scale, setScale] = useState(1.0)
  const [pdfError, setPdfError] = useState(null)
  const [pageInputValue, setPageInputValue] = useState('')
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 })
  const containerRef = useRef(null)
  const wrapperRef = useRef(null)

  const pdfUrl = bookId ? `/pdf/${bookId}` : null

  // Navigate to highlighted page when source changes
  useEffect(() => {
    if (pageIdx != null) {
      setCurrentPage(pageIdx)
      setPageInputValue('')
    }
  }, [pageIdx, bookId])

  // Auto-fit to container width
  useEffect(() => {
    if (containerRef.current) {
      const width = containerRef.current.clientWidth
      const fitScale = Math.min((width - 32) / 595, 2.0)
      setScale(Math.max(fitScale, 0.5))
    }
  }, [containerRef.current?.clientWidth])

  // Detect canvas size after page render
  const onPageRenderSuccess = useCallback(() => {
    if (wrapperRef.current) {
      const canvas = wrapperRef.current.querySelector('canvas')
      if (canvas) {
        setCanvasSize({ width: canvas.clientWidth, height: canvas.clientHeight })
      }
    }
  }, [])

  const onDocumentLoadSuccess = useCallback(({ numPages }) => {
    setNumPages(numPages)
    setPdfError(null)
  }, [])

  const onDocumentLoadError = useCallback((err) => {
    setPdfError(`Failed to load PDF: ${err.message}`)
  }, [])

  const goToPage = (p) => {
    const pg = Math.max(1, Math.min(p, numPages || 1))
    setCurrentPage(pg)
  }

  const handlePageInput = (e) => {
    if (e.key === 'Enter') {
      const p = parseInt(pageInputValue)
      if (!isNaN(p)) goToPage(p)
      setPageInputValue('')
    }
  }

  // Compute highlight overlay position using actual canvas dimensions
  const renderHighlight = () => {
    if (!highlight || currentPage !== pageIdx) return null
    const { x, y, width, height, page_width, page_height } = highlight
    if (!page_width || !page_height || !canvasSize.width) return null

    // Scale from PDF points to actual canvas pixels
    const scaleX = canvasSize.width / page_width
    const scaleY = canvasSize.height / page_height

    return (
      <div
        className="pdf-highlight"
        style={{
          left: `${x * scaleX}px`,
          top: `${y * scaleY}px`,
          width: `${width * scaleX}px`,
          height: `${height * scaleY}px`,
        }}
      />
    )
  }

  if (!bookId) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-neutral-500 px-8 text-center">
        <svg className="w-16 h-16 mb-4 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
        <p className="text-sm font-medium mb-1">No PDF Selected</p>
        <p className="text-xs opacity-60">Click "View PDF" on a source to open the book here</p>
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
            className="p-1.5 rounded-md hover:bg-white/[0.06] text-neutral-400 hover:text-neutral-200 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}
        {/* Book info */}
        <div className="flex-1 min-w-0">
          <span className="text-xs font-medium text-neutral-300 truncate block">
            {bookId.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </span>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => goToPage(currentPage - 1)}
            disabled={currentPage <= 1}
            className="p-1.5 rounded hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div className="flex items-center gap-1 text-xs text-neutral-300">
            <input
              type="text"
              value={pageInputValue || currentPage}
              onChange={e => setPageInputValue(e.target.value)}
              onKeyDown={handlePageInput}
              onFocus={() => setPageInputValue(String(currentPage))}
              onBlur={() => setPageInputValue('')}
              className="w-10 text-center bg-white/5 border border-white/10 rounded px-1 py-0.5 text-xs
                         focus:outline-none focus:border-accent-500/50"
            />
            <span className="text-neutral-500">/ {numPages || '—'}</span>
          </div>

          <button
            onClick={() => goToPage(currentPage + 1)}
            disabled={currentPage >= (numPages || 1)}
            className="p-1.5 rounded hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Zoom */}
        <div className="flex items-center gap-1 ml-2">
          <button
            onClick={() => setScale(s => Math.max(0.3, s - 0.15))}
            className="p-1 rounded hover:bg-white/10 transition-colors text-xs"
          >−</button>
          <span className="text-[10px] text-neutral-400 w-8 text-center">{Math.round(scale * 100)}%</span>
          <button
            onClick={() => setScale(s => Math.min(3, s + 0.15))}
            className="p-1 rounded hover:bg-white/10 transition-colors text-xs"
          >+</button>
        </div>

        {/* Go to highlighted page */}
        {highlight && currentPage !== pageIdx && (
          <button
            onClick={() => goToPage(pageIdx)}
            className="px-2 py-1 rounded bg-yellow-500/15 text-yellow-300/80 text-[10px] font-medium
                       hover:bg-yellow-500/25 transition-colors"
          >
            p.{pageIdx}
          </button>
        )}
      </div>

      {/* PDF Container */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto flex justify-center"
        style={{ background: '#0c0c0c' }}
      >
        {pdfError ? (
          <div className="flex items-center justify-center h-full text-red-400 text-sm px-4">{pdfError}</div>
        ) : (
          <Document
            file={pdfUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading={
              <div className="flex items-center justify-center h-64">
                <div className="spinner" />
                <span className="ml-3 text-sm text-neutral-400">Loading PDF...</span>
              </div>
            }
          >
            <div ref={wrapperRef} className="relative inline-block my-4">
              <Page
                pageNumber={currentPage}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
                onRenderSuccess={onPageRenderSuccess}
                loading={
                  <div className="flex items-center justify-center h-64">
                    <div className="spinner" />
                  </div>
                }
              />
              {renderHighlight()}
            </div>
          </Document>
        )}
      </div>
    </div>
  )
}
