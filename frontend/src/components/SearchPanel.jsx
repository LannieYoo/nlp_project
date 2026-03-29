import { useState, useRef, useEffect } from 'react'
import SourceCard from './SourceCard'

const SUGGESTIONS = [
  'What is SVM (Support Vector Machine)?',
  'Explain gradient descent optimization',
  'How does backpropagation work?',
  'What is the transformer attention mechanism?',
  'Explain convolutional neural networks (CNN)',
  'What is reinforcement learning?',
  'How does batch normalization work?',
  'Explain the bias-variance tradeoff',
  'What is the EM algorithm?',
  'How does dropout regularization work?',
  'Explain recurrent neural networks (RNN)',
  'What is the Bayesian approach to machine learning?',
  'How does principal component analysis (PCA) work?',
  'What is cross-validation?',
  'Explain the kernel trick in SVM',
  'What is natural language processing (NLP)?',
  'How does word2vec work?',
  'What are generative adversarial networks (GAN)?',
  'Explain maximum likelihood estimation',
  'What is the softmax function?',
  'How does LSTM work?',
  'What is transfer learning?',
  'Explain decision tree algorithms',
  'What is logistic regression?',
  'How does random forest work?',
]

export default function SearchPanel({ result, loading, error, onSearch, settings, onViewPdf, activeSource }) {
  const [query, setQuery] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputRef = useRef(null)
  const suggestionsRef = useRef(null)

  const filteredSuggestions = query.trim().length >= 2
    ? SUGGESTIONS.filter(s => s.toLowerCase().includes(query.toLowerCase())).slice(0, 6)
    : []

  // Close suggestions on click outside
  useEffect(() => {
    const handler = (e) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target) && !inputRef.current.contains(e.target)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleSearch = () => {
    if (!query.trim()) return
    setShowSuggestions(false)
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

  const selectSuggestion = (s) => {
    setQuery(s)
    setShowSuggestions(false)
    inputRef.current?.focus()
  }

  // Highlight matching text in suggestion
  const highlightMatch = (text, q) => {
    if (!q.trim()) return text
    const idx = text.toLowerCase().indexOf(q.toLowerCase())
    if (idx === -1) return text
    const before = text.slice(0, idx)
    const match = text.slice(idx, idx + q.length)
    const after = text.slice(idx + q.length)
    return (
      <>
        {before}
        <span className="font-bold text-accent-600">{match}</span>
        {after}
      </>
    )
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
              onChange={e => { setQuery(e.target.value); setShowSuggestions(true) }}
              onFocus={() => setShowSuggestions(true)}
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

            {/* Autocomplete dropdown */}
            {showSuggestions && filteredSuggestions.length > 0 && (
              <div ref={suggestionsRef}
                className="absolute left-0 right-0 top-full mt-1 bg-white rounded-xl border border-neutral-200 shadow-lg z-20 overflow-hidden animate-fade-in">
                {filteredSuggestions.map((s, i) => (
                  <button key={i} onClick={() => selectSuggestion(s)}
                    className="w-full px-4 py-2 text-left text-sm text-neutral-600 hover:bg-accent-50 hover:text-accent-700 transition-colors flex items-center gap-2">
                    <svg className="w-3.5 h-3.5 text-neutral-300 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <span>{highlightMatch(s, query)}</span>
                  </button>
                ))}
              </div>
            )}
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
        {result?.sources?.length > 0 && (() => {
          // Group sources by book_id
          const groupedSources = []
          const map = new Map()
          result.sources.forEach(src => {
            if (!map.has(src.book_id)) {
              map.set(src.book_id, { book_id: src.book_id, items: [] })
              groupedSources.push(map.get(src.book_id)) // preserve ranking order
            }
            map.get(src.book_id).items.push(src)
          })
          
          // Sort items within each book by score descending
          groupedSources.forEach(group => {
            group.items.sort((a, b) => (b.score || 0) - (a.score || 0))
          })

          return (
            <div className="animate-slide-up" style={{ animationDelay: '80ms' }}>
              <h3 className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-2">
                Source Books ({groupedSources.length})
              </h3>
              <div className="space-y-2">
                {groupedSources.map((group, i) => (
                  <SourceCard
                    key={group.book_id}
                    group={group}
                    index={i}
                    onViewPdf={onViewPdf}
                    activeChunkId={activeSource?.chunk_id}
                  />
                ))}
              </div>
            </div>
          )
        })()}

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
