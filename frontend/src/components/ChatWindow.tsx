import type { Message, TraceStep } from "../App"

interface Props {
  messages: Message[]
  loading: boolean
}

const statusColor = (status: string) => {
  if (status === "ok") return "#16a34a"
  if (status === "not_found") return "#d97706"
  if (status === "follow_up") return "#2563eb"
  return "#6b7280"
}

const TraceRow = ({ step }: { step: TraceStep }) => (
  <span className="trace-step">
    <span className="trace-dot" style={{ background: statusColor(step.status) }} />
    <span className="trace-tool">{step.tool}</span>
    {step.note && <span className="trace-note">({step.note})</span>}
    <span className="trace-ms">{step.duration_ms}ms</span>
  </span>
)

export default function ChatWindow({ messages, loading }: Props) {
  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <div className="chat-empty">
          Send a query, or upload a PDF · image · audio file.
        </div>
      )}
      {messages.map((m, i) => (
        <div key={i} className={`msg-wrap msg-wrap--${m.role}`}>
          <div className={`msg-bubble msg-bubble--${m.role}`}>
            {m.streaming && !m.content
              ? <span className="typing-dots"><span /><span /><span /></span>
              : m.content}
          </div>

          {m.planTrace && m.planTrace.length > 0 && (
            <div className="trace-row">
              {m.planTrace.map((s, j) => (
                <TraceRow key={j} step={s} />
              ))}
            </div>
          )}

          {m.ocrMeta && Object.keys(m.ocrMeta).length > 0 && (
            <div className="ocr-meta">
              {Object.entries(m.ocrMeta).map(([k, v]) => (
                <span key={k} className="ocr-badge">OCR: {k} — {v}% confidence</span>
              ))}
            </div>
          )}

          {m.extractedText && m.extractedText.trim() && (
            <details className="extracted-details">
              <summary>Show extracted text</summary>
              <pre className="extracted-pre">
                {m.extractedText.slice(0, 1500)}
                {m.extractedText.length > 1500 ? "\n…(truncated)" : ""}
              </pre>
            </details>
          )}
        </div>
      ))}
      {loading && messages[messages.length - 1]?.role !== "agent" && (
        <div className="msg-wrap msg-wrap--agent">
          <div className="msg-bubble msg-bubble--agent">
            <span className="typing-dots"><span /><span /><span /></span>
          </div>
        </div>
      )}
    </div>
  )
}
