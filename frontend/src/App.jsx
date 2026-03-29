import { useState, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import SearchPanel from './components/SearchPanel'
import PdfViewer from './components/PdfViewer'
import { useSearch } from './hooks/useSearch'

const DEFAULT_SETTINGS = {
  model: 'qwen2.5:0.5b',
  topK: 5,
  methods: ['fts', 'vector', 'tree', 'metadata'],
  bookFilter: '',
}

export default function App() {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [pdfState, setPdfState] = useState({ bookId: null, pageIdx: null, highlight: null })
  const [activeSource, setActiveSource] = useState(null)
  const [showPdfMobile, setShowPdfMobile] = useState(false)

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

  const sidebarWidth = sidebarCollapsed ? 'lg:pl-14' : 'pl-0 lg:pl-60'

  return (
    <div className="h-screen flex flex-col" style={{ background: '#0c0c0c' }}>
      {/* Top steel accent line */}
      <div className="h-px bg-gradient-to-r from-mint-500/50 via-mint-400/20 to-transparent flex-shrink-0" />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          settings={settings}
          onSettingsChange={setSettings}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(c => !c)}
        />

        {/* Main content area */}
        <div className={`flex-1 flex transition-all duration-300 ${sidebarWidth}`}>
          {/* Mobile sidebar toggle */}
          <button
            onClick={() => setSidebarCollapsed(c => !c)}
            className="lg:hidden fixed top-2.5 left-2.5 z-40 p-2 rounded-md glass text-neutral-400 hover:text-neutral-200 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Q&A panel */}
          <div className={`
            flex-1 min-w-0 border-r border-white/[0.04]
            ${pdfState.bookId ? 'lg:w-1/2 lg:flex-none' : 'w-full'}
          `}>
            <SearchPanel
              result={result}
              loading={loading}
              error={error}
              onSearch={search}
              settings={settings}
              onViewPdf={handleViewPdf}
              activeSource={activeSource}
            />
          </div>

          {/* PDF Viewer — right half on desktop */}
          {pdfState.bookId && (
            <>
              <div className="hidden lg:block lg:w-1/2 lg:flex-none">
                <PdfViewer
                  bookId={pdfState.bookId}
                  pageIdx={pdfState.pageIdx}
                  highlight={pdfState.highlight}
                />
              </div>

              {/* Mobile: full-screen overlay with proper width */}
              {showPdfMobile && (
                <div className="lg:hidden fixed inset-0 z-50 w-full h-full" style={{ background: '#0c0c0c' }}>
                  <PdfViewer
                    bookId={pdfState.bookId}
                    pageIdx={pdfState.pageIdx}
                    highlight={pdfState.highlight}
                    onClose={() => setShowPdfMobile(false)}
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
