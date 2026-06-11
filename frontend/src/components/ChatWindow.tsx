interface Message {
  role: "user" | "agent"
  content: string
  planTrace?: string[]
  extractedText?: string
}

interface Props {
  messages: Message[]
  loading: boolean
}

export default function ChatWindow({ messages, loading }: Props) {
  return (
    <div style={{
      border: "1px solid #e5e7eb", borderRadius: 8, padding: 16,
      minHeight: 300, maxHeight: 500, overflowY: "auto",
      background: "#f9fafb", marginBottom: 8
    }}>
      {messages.length === 0 && (
        <div style={{ color: "#9ca3af", fontSize: 13 }}>
          Send a query, or upload a PDF / image / audio file.
        </div>
      )}
      {messages.map((m, i) => (
        <div key={i} style={{ marginBottom: 16 }}>
          <div style={{
            background: m.role === "user" ? "#2563eb" : "#ffffff",
            color: m.role === "user" ? "#fff" : "#111827",
            padding: "10px 14px", borderRadius: 8,
            maxWidth: "85%",
            marginLeft: m.role === "user" ? "auto" : 0,
            border: m.role === "agent" ? "1px solid #e5e7eb" : "none",
            whiteSpace: "pre-wrap", fontSize: 14, lineHeight: 1.5,
          }}>
            {m.content}
          </div>
          {m.planTrace && m.planTrace.length > 0 && (
            <div style={{ fontSize: 12, color: "#6b7280", marginTop: 4 }}>
              🔧 {m.planTrace.join(" → ")}
            </div>
          )}
          {m.extractedText && m.extractedText.trim() && (
            <details style={{ marginTop: 4, fontSize: 12 }}>
              <summary style={{ cursor: "pointer", color: "#6b7280" }}>Show extracted text</summary>
              <pre style={{
                whiteSpace: "pre-wrap", background: "#f3f4f6",
                padding: 8, borderRadius: 4, marginTop: 4,
                fontSize: 11, color: "#374151", maxHeight: 200, overflowY: "auto"
              }}>
                {m.extractedText.slice(0, 1000)}
                {m.extractedText.length > 1000 ? "\n...(truncated)" : ""}
              </pre>
            </details>
          )}
        </div>
      ))}
      {loading && (
        <div style={{ color: "#6b7280", fontSize: 13, fontStyle: "italic" }}>Agent is thinking...</div>
      )}
    </div>
  )
}