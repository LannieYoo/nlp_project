import { useState, useEffect } from 'react'
import { fetchBooks } from '../hooks/useSearch'
import { getBookMeta } from '../utils/bookMeta'

export default function LibraryPanel({ onOpenBook }) {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchBooks().then(data => {
      setBooks(data)
      setLoading(false)
    })
  }, [])

  const filtered = books.filter(b => {
    if (!search.trim()) return true
    const meta = getBookMeta(b.book_id)
    const q = search.toLowerCase()
    return (
      meta.title.toLowerCase().includes(q) ||
      meta.author.toLowerCase().includes(q) ||
      b.book_id.toLowerCase().includes(q)
    )
  })

  return (
    <div className="h-full flex flex-col overflow-hidden bg-surface-100">
      {/* Header */}
      <div className="px-6 pt-6 pb-5 bg-white border-b border-neutral-100 shadow-soft">
        <h2 className="text-xl font-bold text-neutral-800 mb-0.5">Library</h2>
        <p className="text-xs text-neutral-400 mb-4">{books.length} textbooks in collection</p>
        <div className="relative">
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by title, author, or keyword…"
            className="w-full px-4 py-2.5 bg-neutral-50 rounded-xl border border-neutral-200 text-sm text-neutral-700
                       placeholder:text-neutral-300
                       focus:outline-none focus:border-accent-400 focus:ring-2 focus:ring-accent-100 focus:bg-white
                       transition-all"
          />
          <svg className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-300 pointer-events-none"
            fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Book Grid */}
      <div className="flex-1 overflow-y-auto px-6 py-5">
        {loading ? (
          <div className="flex items-center justify-center h-40">
            <div className="spinner" />
            <span className="ml-2 text-sm text-neutral-400">Loading books…</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered.map(book => (
              <BookCard key={book.book_id} book={book} onOpen={onOpenBook} />
            ))}
          </div>
        )}
        {!loading && filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center h-40 text-neutral-400">
            <p className="text-sm font-medium">No books found</p>
            <p className="text-xs mt-1">Try a different keyword</p>
          </div>
        )}
      </div>
    </div>
  )
}

function BookCard({ book, onOpen }) {
  const meta = getBookMeta(book.book_id)
  const [imgError, setImgError] = useState(false)

  return (
    <button
      onClick={() => onOpen(book.book_id)}
      className="group flex gap-3.5 p-3 bg-white rounded-xl border border-neutral-100 shadow-soft
                 hover:shadow-md hover:border-accent-200 hover:bg-accent-50/30
                 transition-all text-left w-full"
    >
      {/* Cover */}
      <div className="relative w-14 h-[76px] rounded-md shadow-md flex-shrink-0 bg-neutral-200 overflow-hidden border border-neutral-200">
        {!imgError ? (
          <img
            src={`/api/page-image/${book.book_id}/0?scale=0.5`}
            alt={meta.title}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center">
            <svg className="w-6 h-6 text-white/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0 py-0.5">
        <h3 className="text-[13px] font-bold text-neutral-800 leading-tight line-clamp-2 group-hover:text-accent-700 transition-colors">
          {meta.title}
        </h3>
        <p className="text-[10px] text-neutral-500 mt-1 truncate">{meta.author}</p>
        <div className="flex items-center gap-2 mt-2 text-[9px] text-neutral-400">
          <span className="px-1.5 py-0.5 rounded bg-neutral-100 font-medium">{meta.year}</span>
          {book.page_count > 0 && (
            <span>{book.page_count} pages</span>
          )}
        </div>
      </div>
    </button>
  )
}
