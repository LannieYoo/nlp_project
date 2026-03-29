import { useState, useEffect } from 'react'
import { fetchStats, fetchBooks } from '../hooks/useSearch'
import { getBookTitle } from '../utils/bookMeta'

const METHODS = [
  { key: 'fts',      label: 'BM25 Keyword',    icon: 'search' },
  { key: 'vector',   label: 'Semantic Vector',  icon: 'vector' },
  { key: 'tree',     label: 'TOC Tree',         icon: 'tree'   },
  { key: 'metadata', label: 'Metadata Filter',  icon: 'filter' },
]

const MethodIcon = ({ type, className = "w-3.5 h-3.5" }) => {
  const icons = {
    search: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    vector: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
      </svg>
    ),
    tree: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h8m-8 6h16" />
      </svg>
    ),
    filter: (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
      </svg>
    ),
  }
  return icons[type] || null
}

export default function Sidebar({ settings, onSettingsChange, collapsed, onToggle, activeView, onViewChange }) {
  const [stats, setStats] = useState(null)
  const [books, setBooks] = useState([])
  const [showBookFilter, setShowBookFilter] = useState(false)
  const [selectedBooks, setSelectedBooks] = useState([])  // empty = all books
  const [bookSearchTerm, setBookSearchTerm] = useState('')

  useEffect(() => {
    fetchStats().then(s => s && setStats(s))
    fetchBooks().then(b => b && setBooks(b))
  }, [])

  const update = (key, val) => onSettingsChange({ ...settings, [key]: val })

  const toggleMethod = (key) => {
    const m = settings.methods.includes(key)
      ? settings.methods.filter(k => k !== key)
      : [...settings.methods, key]
    update('methods', m)
  }

  const toggleBookSelection = (bookId) => {
    setSelectedBooks(prev => {
      const next = prev.includes(bookId)
        ? prev.filter(b => b !== bookId)
        : [...prev, bookId]
      // Update settings.bookFilter as comma-separated
      const filterVal = next.length > 0 ? next.join(',') : ''
      update('bookFilter', filterVal)
      return next
    })
  }

  const clearBookSelection = () => {
    setSelectedBooks([])
    update('bookFilter', '')
  }

  const filteredBooks = books.filter(b => {
    if (!bookSearchTerm.trim()) return true
    const q = bookSearchTerm.toLowerCase()
    return b.book_id.toLowerCase().includes(q) || getBookTitle(b.book_id).toLowerCase().includes(q)
  })

  return (
    <aside className={`
      fixed left-0 top-0 h-full z-30 sidebar-bg
      transition-all duration-300 ease-in-out flex flex-col
      ${collapsed ? 'w-0 -translate-x-full lg:w-14 lg:translate-x-0' : 'w-60'}
    `}>
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-neutral-150">
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <h1 className="text-sm font-semibold text-neutral-800 truncate tracking-tight">AI Textbook Q&A</h1>
            <p className="text-[10px] text-neutral-400 mt-0.5">RAG Source Tracing</p>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1.5 rounded-md hover:bg-neutral-100 text-neutral-400 hover:text-neutral-600 transition-colors flex-shrink-0"
        >
          <svg className={`w-3.5 h-3.5 transition-transform ${collapsed ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {/* Navigation Tabs */}
      {!collapsed && (
        <div className="flex border-b border-neutral-100">
          <button
            onClick={() => onViewChange('search')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-semibold transition-all border-b-2
              ${activeView === 'search'
                ? 'text-accent-600 border-accent-500 bg-accent-50/50'
                : 'text-neutral-400 border-transparent hover:text-neutral-600 hover:bg-neutral-50'}`}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Search
          </button>
          <button
            onClick={() => onViewChange('library')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-semibold transition-all border-b-2
              ${activeView === 'library'
                ? 'text-accent-600 border-accent-500 bg-accent-50/50'
                : 'text-neutral-400 border-transparent hover:text-neutral-600 hover:bg-neutral-50'}`}
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            Library
          </button>
        </div>
      )}

      {!collapsed && (
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-4">
          {/* Model */}
          <div>
            <label className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider">Model</label>
            <input
              type="text"
              value={settings.model}
              onChange={e => update('model', e.target.value)}
              className="mt-1 w-full px-2.5 py-1.5 bg-neutral-50 rounded-lg border border-neutral-200 text-xs text-neutral-700
                         focus:outline-none focus:border-accent-400 focus:ring-2 focus:ring-accent-100 transition-all"
            />
          </div>

          {/* Top K */}
          <div>
            <label className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider">
              Sources: <span className="text-accent-600 font-bold">{settings.topK}</span>
            </label>
            <input
              type="range" min={1} max={20} value={settings.topK}
              onChange={e => update('topK', Number(e.target.value))}
              className="mt-1.5 w-full accent-accent-600 h-1"
            />
          </div>

          {/* Methods */}
          <div>
            <label className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider mb-1.5 block">Retrieval</label>
            <div className="space-y-1">
              {METHODS.map(m => {
                const active = settings.methods.includes(m.key)
                return (
                  <button
                    key={m.key}
                    onClick={() => toggleMethod(m.key)}
                    className={`
                      w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs transition-all border
                      ${active
                        ? 'method-btn-active'
                        : 'text-neutral-500 border-transparent hover:bg-neutral-100 hover:text-neutral-700'
                      }
                    `}
                  >
                    <MethodIcon
                      type={m.icon}
                      className={`w-3.5 h-3.5 flex-shrink-0 method-icon ${active ? 'text-accent-500' : 'text-neutral-400'}`}
                    />
                    <span className="truncate font-medium">{m.label}</span>
                    {active && (
                      <svg className="w-3 h-3 ml-auto text-accent-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Book Filter — Toggle Section */}
          <div>
            <button
              onClick={() => setShowBookFilter(!showBookFilter)}
              className="w-full flex items-center gap-1.5 text-[10px] font-semibold text-neutral-400 uppercase tracking-wider hover:text-neutral-600 transition-colors"
            >
              <svg className={`w-3 h-3 transition-transform ${showBookFilter ? 'rotate-90' : ''}`}
                fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
              Book Filter
              {selectedBooks.length > 0 && (
                <span className="ml-auto px-1.5 py-0.5 rounded-full bg-accent-100 text-accent-600 text-[9px] font-bold normal-case">
                  {selectedBooks.length}
                </span>
              )}
            </button>

            {showBookFilter && (
              <div className="mt-2 space-y-1.5 animate-fade-in">
                {/* Quick search */}
                <input
                  type="text"
                  value={bookSearchTerm}
                  onChange={e => setBookSearchTerm(e.target.value)}
                  placeholder="Filter books…"
                  className="w-full px-2 py-1 bg-neutral-50 rounded-md border border-neutral-200 text-[11px] text-neutral-700
                             placeholder:text-neutral-300 focus:outline-none focus:border-accent-400 transition-all"
                />

                {/* Select All / Clear */}
                <div className="flex justify-between px-0.5">
                  <button
                    onClick={clearBookSelection}
                    className="text-[9px] text-accent-500 hover:text-accent-700 font-semibold transition-colors"
                  >
                    All Books (default)
                  </button>
                  {selectedBooks.length > 0 && (
                    <button
                      onClick={clearBookSelection}
                      className="text-[9px] text-red-400 hover:text-red-600 font-semibold transition-colors"
                    >
                      Clear
                    </button>
                  )}
                </div>

                {/* Book list */}
                <div className="max-h-40 overflow-y-auto space-y-0.5 pr-0.5 scrollbar-thin">
                  {filteredBooks.map(book => {
                    const checked = selectedBooks.includes(book.book_id)
                    return (
                      <label
                        key={book.book_id}
                        className={`flex items-center gap-2 px-2 py-1 rounded-md cursor-pointer text-[11px] transition-all
                          ${checked ? 'bg-accent-50 text-accent-700' : 'text-neutral-500 hover:bg-neutral-50'}`}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => toggleBookSelection(book.book_id)}
                          className="w-3 h-3 rounded border-neutral-300 text-accent-600 focus:ring-accent-400 focus:ring-1 flex-shrink-0"
                        />
                        <span className="truncate">{getBookTitle(book.book_id)}</span>
                      </label>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Stats footer */}
      {!collapsed && stats && (
        <div className="px-3 py-3 border-t border-neutral-100">
          <div className="flex gap-3">
            <div className="flex-1 text-center bg-neutral-50 rounded-lg py-2">
              <div className="text-base font-bold text-neutral-700">{stats.total_books}</div>
              <div className="text-[9px] text-neutral-400 uppercase tracking-wider mt-0.5">Books</div>
            </div>
            <div className="flex-1 text-center bg-neutral-50 rounded-lg py-2">
              <div className="text-base font-bold text-neutral-700">{stats.total_chunks?.toLocaleString()}</div>
              <div className="text-[9px] text-neutral-400 uppercase tracking-wider mt-0.5">Chunks</div>
            </div>
          </div>
        </div>
      )}

      {/* Collapsed icon strip */}
      {collapsed && (
        <div className="hidden lg:flex flex-col items-center gap-3 mt-4 px-2">
          <button
            onClick={() => { onToggle(); onViewChange('search') }}
            className={`w-7 h-7 rounded-lg flex items-center justify-center transition-colors
              ${activeView === 'search' ? 'bg-accent-50' : 'hover:bg-neutral-100'}`}
            title="Search"
          >
            <svg className={`w-3.5 h-3.5 ${activeView === 'search' ? 'text-accent-500' : 'text-neutral-400'}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
          <button
            onClick={() => { onToggle(); onViewChange('library') }}
            className={`w-7 h-7 rounded-lg flex items-center justify-center transition-colors
              ${activeView === 'library' ? 'bg-accent-50' : 'hover:bg-neutral-100'}`}
            title="Library"
          >
            <svg className={`w-3.5 h-3.5 ${activeView === 'library' ? 'text-accent-500' : 'text-neutral-400'}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </button>
        </div>
      )}
    </aside>
  )
}
