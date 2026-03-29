import { useState, useCallback } from 'react'
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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [pdfState, setPdfState] = useState({ bookId: null, pageIdx: null, highlight: null })
  const [activeSource, setActiveSource] = useState(null)
  const [showPdfMobile, setShowPdfMobile] = useState(false)
  const [activeView, setActiveView] = useState('search')  // 'search' | 'library'

  const { search, result, loading, error } = useSearch()

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

  const sidebarWidth = sidebarCollapsed ? 'lg:pl-14' : 'pl-0 lg:pl-60'

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
          onViewChange={setActiveView}
        />

        {/* Main content area */}
        <div className={`flex-1 flex transition-all duration-300 ${sidebarWidth}`}>
          {/* Mobile sidebar toggle */}
          <button
            onClick={() => setSidebarCollapsed(c => !c)}
            className="lg:hidden fixed top-3 left-3 z-40 p-2 rounded-xl bg-white border border-neutral-200 shadow-soft text-neutral-500 hover:text-neutral-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Main Panel — Search or Library */}
          <div className={`
            flex-1 min-w-0 border-r border-neutral-100
            ${pdfState.bookId ? 'lg:w-1/2 lg:flex-none' : 'w-full'}
          `}>
            {activeView === 'search' ? (
              <SearchPanel
                result={result}
                loading={loading}
                error={error}
                onSearch={search}
                settings={settings}
                onViewPdf={handleViewPdf}
                activeSource={activeSource}
              />
            ) : (
              <LibraryPanel onOpenBook={handleOpenBook} />
            )}
          </div>

          {/* PDF Viewer — right half on desktop */}
          {pdfState.bookId && (
            <>
              <div className="hidden lg:block lg:w-1/2 lg:flex-none bg-neutral-100">
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
