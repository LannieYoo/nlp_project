import { useState, useCallback, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import SearchPanel from './components/SearchPanel'
import LibraryPanel from './components/LibraryPanel'
import PdfViewer from './components/PdfViewer'
import { useSearch } from './hooks/useSearch'

const DEFAULT_SETTINGS = {
  model: 'qwen2.5:0.5b',
  topK: 10,
  methods: ['fts', 'vector', 'tree', 'metadata'],
  bookFilter: '',
}

export default function App() {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => typeof window !== 'undefined' ? window.innerWidth < 1024 : false)
  const [pdfState, setPdfState] = useState({ bookId: null, pageIdx: null, highlight: null })
  const [activeSource, setActiveSource] = useState(null)
  const [showPdfMobile, setShowPdfMobile] = useState(false)
  const [activeView, setActiveView] = useState('search')  // 'search' | 'library'
  const [searchKey, setSearchKey] = useState(0)
  const [pdfWidth, setPdfWidth] = useState(50) // percentage
  const [isDragging, setIsDragging] = useState(false)

  useEffect(() => {
    let wasMobile = window.innerWidth < 1024;
    const handleResize = () => {
      const isMobile = window.innerWidth < 1024;
      if (isMobile && !wasMobile) {
        setSidebarCollapsed(true);
      } else if (!isMobile && wasMobile) {
        setSidebarCollapsed(false);
      }
      wasMobile = isMobile;
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!isDragging) return
    const handleMouseMove = (e) => {
      const availWidth = window.innerWidth
      let newWidth = ((availWidth - e.clientX) / availWidth) * 100
      newWidth = Math.max(30, Math.min(newWidth, 70))
      setPdfWidth(newWidth)
    }
    const handleMouseUp = () => setIsDragging(false)
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  const { search: rawSearch, result, loading, error, resetSearch } = useSearch()

  // Wrap search to close PDF before starting a new query
  const search = useCallback((params) => {
    handleClosePdf()
    rawSearch(params)
  }, [rawSearch])

  const handleViewPdf = useCallback((source) => {
    setPdfState({
      bookId: source.book_id,
      pageIdx: source.page_idx,
      highlight: source.highlight,
    })
    setActiveSource(source)
    setShowPdfMobile(true)
  }, [])

  const handleClosePdf = useCallback(() => {
    setPdfState({ bookId: null, pageIdx: null, highlight: null })
    setActiveSource(null)
    setShowPdfMobile(false)
  }, [])

  const handleOpenBook = useCallback((bookId) => {
    setPdfState({ bookId, pageIdx: 0, highlight: null })
    setActiveSource(null)
    setShowPdfMobile(true)
  }, [])

  const handleViewChange = useCallback((view) => {
    setActiveView(view)
    handleClosePdf()
  }, [handleClosePdf])

  const handleGoHome = useCallback(() => {
    setActiveView('search')
    handleClosePdf()
    resetSearch()
    setSearchKey(k => k + 1)
  }, [handleClosePdf, resetSearch])

  const sidebarWidth = sidebarCollapsed ? 'pl-0 lg:pl-14' : 'pl-60'

  return (
    <div className="h-screen flex flex-col" style={{ background: '#f8f8f8' }}>
      {/* Top accent line */}
      <div className="h-[2px] flex-shrink-0" style={{
        background: 'linear-gradient(90deg, #5273e8 0%, #a5beff 50%, transparent 100%)'
      }} />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          settings={settings}
          onSettingsChange={setSettings}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(c => !c)}
          activeView={activeView}
          onViewChange={handleViewChange}
          onOpenBook={handleOpenBook}
          onGoHome={handleGoHome}
          activeBookId={pdfState.bookId}
        />

        {/* Main content area */}
        <div className={`flex-1 flex transition-all duration-300 ${sidebarWidth}`}>
          {/* Mobile sidebar toggle */}
          <button
            onClick={() => setSidebarCollapsed(c => !c)}
            className="lg:hidden fixed top-3 left-3 z-40 p-2.5 rounded-xl bg-white border border-neutral-200 shadow-soft text-neutral-500 hover:text-neutral-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Main Panel — Search or Library */}
          <div 
            className="flex-1 min-w-0 border-r border-neutral-100"
            style={{ width: pdfState.bookId ? `${100 - pdfWidth}%` : '100%', flex: 'none' }}
          >
            {activeView === 'search' ? (
              <SearchPanel
                key={`search-${searchKey}`}
                result={result}
                loading={loading}
                error={error}
                onSearch={search}
                settings={settings}
                onViewPdf={handleViewPdf}
                activeSource={activeSource}
              />
            ) : (
              <LibraryPanel onOpenBook={handleOpenBook} activeBookId={pdfState.bookId} />
            )}
          </div>

          {/* PDF Viewer — right panel */}
          {pdfState.bookId && (
            <>
              {/* Drag Handle */}
              <div 
                className="hidden lg:block w-1.5 cursor-col-resize hover:bg-accent-400 active:bg-accent-500 z-10 transition-colors bg-neutral-200"
                onMouseDown={(e) => { e.preventDefault(); setIsDragging(true); }}
              />

              <div 
                className="hidden lg:block bg-neutral-100 flex-none"
                style={{ width: `calc(${pdfWidth}% - 6px)` }}
              >
                <PdfViewer
                  bookId={pdfState.bookId}
                  pageIdx={pdfState.pageIdx}
                  highlight={pdfState.highlight}
                  onClose={handleClosePdf}
                />
              </div>

              {/* Mobile: full-screen overlay */}
              {showPdfMobile && (
                <div className="lg:hidden fixed inset-0 z-50 w-full h-full" style={{ background: '#f0f0f0' }}>
                  <PdfViewer
                    bookId={pdfState.bookId}
                    pageIdx={pdfState.pageIdx}
                    highlight={pdfState.highlight}
                    onClose={handleClosePdf}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
