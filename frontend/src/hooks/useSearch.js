import { useState, useCallback } from 'react'

const API_BASE = ''  // proxy handles it

export function useSearch() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const search = useCallback(async ({ query, topK, model, bookFilter, methods }) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          top_k: topK,
          model,
          book_filter: bookFilter || null,
          methods,
        }),
      })
      if (!res.ok) throw new Error(`Search failed: ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { search, result, loading, error }
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/api/stats`)
  if (!res.ok) return null
  return res.json()
}

export async function fetchBooks() {
  const res = await fetch(`${API_BASE}/api/books`)
  if (!res.ok) return []
  return res.json()
}
