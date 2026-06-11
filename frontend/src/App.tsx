import { useState } from "react"
import ChatWindow from "./components/ChatWindow"
import FileUpload from "./components/FileUpload"

interface Message {
  role: "user" | "agent"
  content: string
  planTrace?: string[]
  extractedText?: string
  followUp?: string | null
}

const BACKEND = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"

const formatResult = (result: unknown): string => {
  if (typeof result === "string") return result
  if (!result || typeof result !== "object") return String(result)
  const r = result as Record<string, unknown>
  const parts: string[] = []
  if (r.one_liner) parts.push(`📌 ${r.one_liner}`)
  if (Array.isArray(r.bullets) && r.bullets.length) parts.push(r.bullets.map((b: unknown) => `• ${b}`).join("\n"))
  if (r.five_sentences) parts.push(`\n${r.five_sentences}`)
  if (r.label) parts.push(`Sentiment: ${r.label} (confidence: ${r.confidence})\n${r.justification}`)
  if (r.explanation) parts.push(`Explanation: ${r.explanation}`)
  if (r.bugs) parts.push(`Bugs: ${r.bugs}`)
  if (r.time_complexity) parts.push(`Time Complexity: ${r.time_complexity}`)
  if (r.same_topic) parts.push(`Same Topic: ${r.same_topic}\nCommon Themes: ${r.common_themes}\nDifferences: ${r.differences}\n${r.summary}`)
  if (r.answer) parts.push(String(r.answer))
  if (r.error) parts.push(`⚠️ Error: ${r.error}`)
  return parts.length ? parts.join("\n\n") : JSON.stringify(result, null, 2)
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [query, setQuery] = useState("")
  const [files, setFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!query.trim() && files.length === 0) return

    setMessages(prev => [...prev, { role: "user", content: query }])
    setLoading(true)

    const formData = new FormData()
    formData.append("query", query)
    files.forEach(f => formData.append("files", f))

    try {
      const res = await fetch(`${BACKEND}/chat`, { method: "POST", body: formData })
      const data = await res.json()

      const resultText = data.follow_up
        ? `❓ ${data.follow_up}`
        : formatResult(data.result)

      setMessages(prev => [...prev, {
        role: "agent",
        content: resultText,
        planTrace: data.plan_trace,
        extractedText: data.extracted_text,
        followUp: data.follow_up,
      }])

      setQuery("")
      if (!data.follow_up) setFiles([])
    } catch {
      setMessages(prev => [...prev, { role: "agent", content: "Error: Could not reach backend." }])
      setQuery("")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "40px auto", padding: "0 16px", fontFamily: "sans-serif" }}>
      <h2 style={{ marginBottom: 16 }}>Query Pilot</h2>
      <ChatWindow messages={messages} loading={loading} />
      <FileUpload files={files} setFiles={setFiles} />
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <input
          style={{ flex: 1, padding: 10, fontSize: 14, border: "1px solid #d1d5db", borderRadius: 6 }}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !loading && handleSend()}
          placeholder="Type your query..."
        />
        <button
          onClick={handleSend}
          disabled={loading}
          style={{ padding: "10px 20px", background: loading ? "#9ca3af" : "#2563eb", color: "#fff", border: "none", borderRadius: 6, cursor: loading ? "default" : "pointer" }}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  )
}