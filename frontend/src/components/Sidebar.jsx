import { useState, useEffect } from 'react'
import { fetchStats } from '../hooks/useSearch'

const METHODS = [
  { key: 'fts', label: 'BM25 Keyword', icon: 'search' },
  { key: 'vector', label: 'Semantic Vector', icon: 'vector' },
  { key: 'tree', label: 'TOC Tree', icon: 'tree' },
  { key: 'metadata', label: 'Metadata Filter', icon: 'filter' },
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

export default function Sidebar({ settings, onSettingsChange, collapsed, onToggle }) {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetchStats().then(s => s && setStats(s))
  }, [])

  const update = (key, val) => onSettingsChange({ ...settings, [key]: val })

  const toggleMethod = (key) => {
    const m = settings.methods.includes(key)
      ? settings.methods.filter(k => k !== key)
      : [...settings.methods, key]
    update('methods', m)
  }

  return (
    <aside
      className={`
        fixed left-0 top-0 h-full z-30
        sidebar-bg border-r border-white/[0.04]
        transition-all duration-300 ease-in-out
        flex flex-col
        ${collapsed ? 'w-0 -translate-x-full lg:w-14 lg:translate-x-0' : 'w-60'}
      `}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-white/[0.04]">
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <h1 className="text-sm font-semibold gradient-text truncate tracking-tight">AI Textbook Q&A</h1>
            <p className="text-[10px] text-neutral-600 mt-0.5">RAG Source Tracing</p>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1.5 rounded-md hover:bg-white/[0.05] text-neutral-500 hover:text-neutral-300 transition-colors flex-shrink-0"
        >
          <svg className={`w-3.5 h-3.5 transition-transform ${collapsed ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {!collapsed && (
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-4">
          {/* Model */}
          <div>
            <label className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider">Model</label>
            <input
              type="text"
              value={settings.model}
              onChange={e => update('model', e.target.value)}
              className="mt-1 w-full px-2.5 py-1.5 bg-white/[0.03] rounded-md border border-white/[0.06] text-xs text-neutral-300
                         focus:outline-none focus:border-mint-500/40 transition-all"
            />
          </div>

          {/* Top K */}
          <div>
            <label className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider">
              Sources: <span className="text-mint-400">{settings.topK}</span>
            </label>
            <input
              type="range" min={1} max={20} value={settings.topK}
              onChange={e => update('topK', Number(e.target.value))}
              className="mt-1 w-full accent-cyan-300 h-1"
            />
          </div>

          {/* Methods */}
          <div>
            <label className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider mb-1.5 block">Retrieval</label>
            <div className="space-y-1">
              {METHODS.map(m => {
                const active = settings.methods.includes(m.key)
                return (
                  <button
                    key={m.key}
                    onClick={() => toggleMethod(m.key)}
                    className={`
                      w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs transition-all border
                      ${active
                        ? 'method-btn-active text-mint-300'
                        : 'text-neutral-500 border-transparent hover:bg-white/[0.03] hover:text-neutral-400'
                      }
                    `}
                  >
                    <MethodIcon type={m.icon} className={`w-3.5 h-3.5 flex-shrink-0 ${active ? 'text-mint-400' : 'text-neutral-600'}`} />
                    <span className="truncate">{m.label}</span>
                    {active && (
                      <svg className="w-3 h-3 ml-auto text-mint-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Book filter */}
          <div>
            <label className="text-[10px] font-medium text-neutral-500 uppercase tracking-wider">Book Filter</label>
            <input
              type="text"
              value={settings.bookFilter}
              onChange={e => update('bookFilter', e.target.value)}
              placeholder="e.g. jurafsky_slp3"
              className="mt-1 w-full px-2.5 py-1.5 bg-white/[0.03] rounded-md border border-white/[0.06] text-xs text-neutral-300
                         placeholder:text-neutral-700
                         focus:outline-none focus:border-mint-500/40 transition-all"
            />
          </div>
        </div>
      )}

      {/* Stats footer */}
      {!collapsed && stats && (
        <div className="px-3 py-2.5 border-t border-white/[0.04]">
          <div className="flex gap-3">
            <div className="text-center flex-1">
              <div className="text-base font-semibold text-neutral-300">{stats.total_books}</div>
              <div className="text-[9px] text-neutral-600 uppercase tracking-wider">Books</div>
            </div>
            <div className="text-center flex-1">
              <div className="text-base font-semibold text-neutral-300">{stats.total_chunks?.toLocaleString()}</div>
              <div className="text-[9px] text-neutral-600 uppercase tracking-wider">Chunks</div>
            </div>
          </div>
        </div>
      )}

      {/* Collapsed icon */}
      {collapsed && (
        <div className="hidden lg:flex flex-col items-center gap-2 mt-3">
          <svg className="w-4 h-4 text-neutral-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
      )}
    </aside>
  )
}
