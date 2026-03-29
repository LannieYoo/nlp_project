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

  const isSearchActive = !!result || loading || !!error;

  return (
    <div className="h-full flex flex-col bg-surface-100 relative overflow-hidden">
      
      {/* Background that turns white when active */}
      <div className={`absolute top-0 left-0 right-0 h-[124px] bg-white border-b border-neutral-100 shadow-soft transition-all duration-700 ease-[cubic-bezier(0.25,1,0.5,1)] z-0
        ${isSearchActive ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-full'}`} />

      {/* The Search Header (animates from center to top) */}
      <div className={`
        relative z-10 w-full transition-all duration-700 ease-[cubic-bezier(0.25,1,0.5,1)] px-6
        ${isSearchActive 
          ? 'pt-6 pb-5' 
          : 'pt-[28vh]'}
      `}>
        <div className={`mx-auto transition-all duration-700 w-full flex flex-col ${isSearchActive ? 'max-w-full items-start' : 'max-w-3xl items-center text-center'}`}>
          
          <h2 className={`font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-accent-600 to-accent-400 transition-all duration-700 pb-1 ${isSearchActive ? 'text-xl mb-0.5' : 'text-[2.75rem] leading-tight mb-3 tracking-tight'}`}>
            {isSearchActive ? 'Ask a Question' : 'AI Textbook Q&A'}
          </h2>
          <p className={`text-neutral-400 transition-all duration-700 ${isSearchActive ? 'text-xs mb-4' : 'text-[15px] mb-10 tracking-wide'}`}>
            Search across 46 AI/ML textbooks with source tracing
          </p>

          <div className={`flex gap-3 w-full transition-all duration-700 ${isSearchActive ? 'scale-100' : 'scale-[1.02]'}`}>
            <div className={`flex-1 relative transition-all duration-700 ${isSearchActive ? 'shadow-none' : 'shadow-lg hover:shadow-xl rounded-full'}`}>
              
              {/* Left Search Icon */}
              <svg
                className={`absolute left-5 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none transition-all duration-700 ${isSearchActive ? 'w-4 h-4 left-3.5' : 'w-5 h-5 left-5 text-accent-400/70'}`}
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>

              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={e => { setQuery(e.target.value); setShowSuggestions(true) }}
                onFocus={() => setShowSuggestions(true)}
                onKeyDown={handleKeyDown}
                placeholder="e.g. What is the transformer attention mechanism?"
                className={`w-full bg-white border-2 text-neutral-700 placeholder:text-neutral-400 focus:outline-none focus:border-accent-500 focus:ring-4 focus:ring-accent-500/15 transition-all duration-700
                  ${isSearchActive 
                    ? 'pl-10 pr-4 py-2.5 rounded-xl border-neutral-200 text-sm' 
                    : 'pl-14 pr-6 py-4 rounded-full border-transparent focus:border-accent-500 hover:border-neutral-200 text-base'
                  }`}
              />

              {/* Autocomplete dropdown */}
              {showSuggestions && filteredSuggestions.length > 0 && (
                <div ref={suggestionsRef}
                  className={`absolute left-0 right-0 mt-2 bg-white border border-neutral-200 shadow-xl z-20 overflow-hidden animate-fade-in ${isSearchActive ? 'rounded-xl top-full' : 'rounded-2xl top-full'}`}>
                  {filteredSuggestions.map((s, i) => (
                    <button key={i} onClick={() => selectSuggestion(s)}
                      className="w-full px-5 py-3 text-left text-[15px] text-neutral-600 hover:bg-neutral-50 hover:text-accent-600 transition-colors flex items-center gap-3">
                      <svg className="w-4 h-4 text-neutral-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
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
              className={`btn-primary font-bold active:scale-[0.98] transition-all duration-700 shadow-sm flex items-center justify-center
                ${isSearchActive ? 'px-6 py-2.5 text-sm rounded-xl' : 'px-8 py-3 text-base shadow-md hover:shadow-lg rounded-full'}`}
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
      </div>

      {/* Results */}
      <div className={`flex-1 relative z-0 overflow-y-auto px-6 py-4 space-y-4 transition-all duration-700 ease-[cubic-bezier(0.25,1,0.5,1)] scrollbar-thin
        ${isSearchActive ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12 pointer-events-none absolute left-0 right-0'}`}>
        
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
      </div>
    </div>
  )
}
