export default function ResearchInput({ onSubmit, onStop, isRunning, value, onChange }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    const topic = value.trim()
    if (topic) onSubmit(topic)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter a research topic — e.g. 'quantum computing applications in drug discovery'"
        disabled={isRunning}
        className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 disabled:opacity-50 transition-colors"
        autoComplete="off"
      />
      {isRunning ? (
        <button
          type="button"
          onClick={onStop}
          className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors whitespace-nowrap"
        >
          Stop
        </button>
      ) : (
        <button
          type="submit"
          className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-medium rounded-lg transition-colors whitespace-nowrap"
        >
          Research
        </button>
      )}
    </form>
  )
}
