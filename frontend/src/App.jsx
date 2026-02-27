import { useRef, useState } from 'react'
import ReportPanel from './components/ReportPanel'
import ResearchInput from './components/ResearchInput'
import TracePanel from './components/TracePanel'

export default function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [traceEvents, setTraceEvents] = useState([])
  const [report, setReport] = useState('')
  const [error, setError] = useState('')
  const readerRef = useRef(null)

  const handleSubmit = async (topic) => {
    setIsRunning(true)
    setTraceEvents([])
    setReport('')
    setError('')

    try {
      const response = await fetch('/research/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      readerRef.current = reader
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() // keep any incomplete chunk

        for (const part of parts) {
          if (!part.startsWith('data: ')) continue
          try {
            const event = JSON.parse(part.slice(6))
            if (event.type === 'done') {
              setIsRunning(false)
            } else if (event.type === 'report') {
              setReport(event.content)
            } else if (event.type === 'error') {
              setError(event.content)
            } else {
              setTraceEvents((prev) => [...prev, event])
            }
          } catch {
            // malformed chunk — skip
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message)
      }
    } finally {
      setIsRunning(false)
    }
  }

  const handleStop = () => {
    readerRef.current?.cancel()
    readerRef.current = null
    setIsRunning(false)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      <div className="max-w-4xl w-full mx-auto px-4 py-10 flex-1">

        {/* Header */}
        <div className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-white mb-2">ReconAgent</h1>
          <p className="text-gray-400 text-lg">
            <span className="text-cyan-500 font-medium">AutoResearch</span>
            {' · '}Autonomous research with real-time agent reasoning
          </p>
        </div>

        {/* Input */}
        <ResearchInput onSubmit={handleSubmit} onStop={handleStop} isRunning={isRunning} />

        {/* Error banner */}
        {error && (
          <div className="mt-4 p-4 bg-red-900/40 border border-red-700 rounded-lg text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Agent trace */}
        {(traceEvents.length > 0 || isRunning) && !error && (
          <TracePanel events={traceEvents} isRunning={isRunning} />
        )}

        {/* Final report */}
        {report && <ReportPanel report={report} />}

      </div>

      {/* Footer */}
      <div className="w-full px-6 py-4 flex justify-end">
        <p className="text-xs text-gray-600">
          Created by <span className="text-gray-500">Eric Holt</span>
        </p>
      </div>
    </div>
  )
}
