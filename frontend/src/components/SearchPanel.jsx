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
    <div className="h-full flex flex-col overflow-hidden">
      {/* Search Header */}
      <div className="px-5 pt-5 pb-4 border-b border-white/[0.04]">
        <h2 className="text-lg font-semibold gradient-text mb-0.5">Ask a Question</h2>
        <p className="text-[11px] text-neutral-600 mb-3">Search across 46 AI/ML textbooks with source tracing</p>

        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. What is the transformer attention mechanism?"
              className="w-full px-3.5 py-2.5 bg-white/[0.03] rounded-lg border border-white/[0.06] text-sm text-neutral-200
                         placeholder:text-neutral-700
                         focus:outline-none focus:border-mint-500/30 focus:ring-1 focus:ring-mint-500/10
                         transition-all"
            />
            <svg
              className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600"
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="btn-primary px-5 py-2.5 rounded-lg text-sm font-medium text-white active:scale-[0.98]"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="spinner" />
                <span>Searching...</span>
              </div>
            ) : 'Search'}
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {/* Error */}
        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/15 text-red-300 text-sm animate-fade-in">
            {error}
          </div>
        )}

        {/* Answer */}
        {result?.answer && (
          <div className="animate-slide-up">
            <h3 className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider mb-2">Answer</h3>
            <div className="answer-box px-4 py-3 rounded-r-lg">
              <div className="text-sm text-neutral-300 leading-relaxed whitespace-pre-wrap">
                {result.answer}
              </div>
            </div>
          </div>
        )}

        {/* Sources */}
        {result?.sources?.length > 0 && (
          <div className="animate-slide-up" style={{ animationDelay: '100ms' }}>
            <h3 className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider mb-2">
              Source Documents ({result.sources.length})
            </h3>
            <div className="space-y-1.5">
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
          <div className="flex flex-col items-center justify-center h-64 text-neutral-600">
            <svg className="w-10 h-10 mb-3 opacity-25" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-sm font-medium text-neutral-500">Ask anything about AI, ML, or NLP</p>
            <p className="text-xs text-neutral-700 mt-1">Answers are grounded in textbook sources</p>
          </div>
        )}
      </div>
    </div>
  )
}
