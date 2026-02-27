import { useState } from 'react'

function formatDate(dateStr) {
  const date = new Date(dateStr + 'Z') // SQLite stores UTC without Z suffix
  const diff = Date.now() - date.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function HistoryPanel({ history, onSelect }) {
  const [open, setOpen] = useState(false)

  if (history.length === 0) return null

  return (
    <div className="mt-4 bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-gray-800 hover:bg-gray-750 transition-colors"
      >
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Recent Searches ({history.length})
        </span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`text-gray-500 transition-transform ${open ? 'rotate-180' : ''}`}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {open && (
        <div className="divide-y divide-gray-800">
          {history.map((item) => (
            <button
              key={item.id}
              onClick={() => onSelect(item.topic)}
              className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-gray-800 transition-colors text-left"
            >
              <span className="text-sm text-gray-300 truncate pr-4">{item.topic}</span>
              <span className="text-xs text-gray-600 shrink-0">{formatDate(item.created_at)}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
