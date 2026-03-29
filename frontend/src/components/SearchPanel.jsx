import { useState, useRef } from 'react'
import SourceCard from './SourceCard'

export default function SearchPanel({ result, loading, error, onSearch, settings, onViewPdf, activeSource }) {
  const [query, setQuery] = useState('')
  const inputRef = useRef(null)

  const handleSearch = () => {
    if (!query.trim()) return
    onSearch({
      query: query.trim(),
      topK: settings.topK,
      model: settings.model,
      bookFilter: settings.bookFilter,
      methods: settings.methods,
    })
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch()
  }

  return (
    <div className="h-full flex flex-col overflow-hidden bg-surface-100">
      {/* Search Header */}
      <div className="px-6 pt-6 pb-5 bg-white border-b border-neutral-100 shadow-soft">
        <h2 className="text-xl font-bold text-neutral-800 mb-0.5">Ask a Question</h2>
        <p className="text-xs text-neutral-400 mb-4">Search across 46 AI/ML textbooks with source tracing</p>

        <div className="flex gap-2.5">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. What is the transformer attention mechanism?"
              className="w-full px-4 py-2.5 bg-neutral-50 rounded-xl border border-neutral-200 text-sm text-neutral-700
                         placeholder:text-neutral-300
                         focus:outline-none focus:border-accent-400 focus:ring-2 focus:ring-accent-100 focus:bg-white
                         transition-all"
            />
            <svg
              className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-300 pointer-events-none"
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="btn-primary px-6 py-2.5 rounded-xl text-sm font-semibold active:scale-[0.98]"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="spinner" />
                <span>Searching…</span>
              </div>
            ) : 'Search'}
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {/* Error */}
        {error && (
          <div className="p-3.5 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm animate-fade-in">
            {error}
          </div>
        )}

        {/* Answer */}
        {result?.answer && (
          <div className="animate-slide-up">
            <h3 className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-2">Answer</h3>
            <div className="answer-box px-5 py-4 rounded-r-xl bg-white shadow-soft">
              <div className="text-sm text-neutral-700 leading-relaxed whitespace-pre-wrap">
                {result.answer}
              </div>
            </div>
          </div>
        )}

        {/* Sources */}
        {result?.sources?.length > 0 && (
          <div className="animate-slide-up" style={{ animationDelay: '80ms' }}>
            <h3 className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-2">
              Source Documents ({result.sources.length})
            </h3>
            <div className="space-y-2">
              {result.sources.map((src, i) => (
                <SourceCard
                  key={src.chunk_id || i}
                  source={src}
                  index={i}
                  onViewPdf={onViewPdf}
                  isActive={activeSource?.chunk_id === src.chunk_id}
                />
              ))}
            </div>
          </div>
        )}

        {/* Empty state */}
        {!loading && !result && !error && (
          <div className="flex flex-col items-center justify-center h-64 select-none">
            <div className="w-14 h-14 rounded-2xl bg-accent-50 flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            </div>
            <p className="text-sm font-semibold text-neutral-500">Ask anything about AI, ML, or NLP</p>
            <p className="text-xs text-neutral-300 mt-1">Answers are grounded in textbook sources</p>
          </div>
        )}
      </div>
    </div>
  )
}
