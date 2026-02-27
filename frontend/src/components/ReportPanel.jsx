import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function ReportPanel({ report }) {
  const handleCopy = () => {
    navigator.clipboard.writeText(report)
  }

  return (
    <div className="mt-6 bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-gray-700 bg-gray-800">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Research Report
        </span>
        <button
          onClick={handleCopy}
          className="text-xs text-gray-500 hover:text-gray-200 transition-colors px-2 py-1 rounded hover:bg-gray-700"
        >
          Copy markdown
        </button>
      </div>

      {/* Report content */}
      <div className="p-6 prose prose-invert prose-sm max-w-none
        prose-headings:text-gray-100
        prose-p:text-gray-300
        prose-li:text-gray-300
        prose-a:text-cyan-400 hover:prose-a:text-cyan-300
        prose-strong:text-gray-100
        prose-code:text-cyan-300
        prose-hr:border-gray-700">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
      </div>
    </div>
  )
}
