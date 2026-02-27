import { useEffect, useRef } from 'react'

const EVENT_CONFIG = {
  planning: {
    icon: '⚡',
    color: 'text-blue-400',
  },
  searching: {
    icon: '🔍',
    color: 'text-purple-400',
  },
  reflecting: {
    icon: '🤔',
    color: 'text-yellow-400',
  },
  synthesizing: {
    icon: '✍️',
    color: 'text-green-400',
  },
}

function TraceEvent({ event }) {
  const cfg = EVENT_CONFIG[event.type] ?? { icon: '•', color: 'text-gray-400' }
  return (
    <div className="flex items-start gap-2 py-0.5">
      <span className="text-sm leading-5 shrink-0">{cfg.icon}</span>
      <span className={`text-sm font-mono leading-5 ${cfg.color} break-words`}>
        {event.content}
      </span>
    </div>
  )
}

export default function TracePanel({ events, isRunning }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events.length])

  return (
    <div className="mt-6 bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-2.5 border-b border-gray-700 bg-gray-800">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Agent Reasoning Trace
        </span>
        {isRunning && (
          <span className="flex items-center gap-1.5 text-xs text-cyan-400">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse" />
            Running
          </span>
        )}
      </div>

      {/* Events */}
      <div className="p-4 space-y-0.5 max-h-80 overflow-y-auto">
        {events.length === 0 && isRunning ? (
          <p className="text-gray-500 text-sm">Starting agent...</p>
        ) : (
          events.map((event, i) => <TraceEvent key={i} event={event} />)
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
