import { useState, useRef, useEffect } from "react"
import ChatWindow from "./components/ChatWindow"
import FileUpload from "./components/FileUpload"
import "./index.css"

export interface TraceStep {
  tool: string
  status: string
  duration_ms: number
  note?: string
}

export interface Message {
  role: "user" | "agent"
  content: string
  planTrace?: TraceStep[]
  extractedText?: string
  followUp?: string | null
  ocrMeta?: Record<string, number>
  streaming?: boolean
}

const BACKEND = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"

const formatResult = (result: unknown): string => {
  if (typeof result === "string") return result
  if (!result || typeof result !== "object") return String(result)
  const r = result as Record<string, unknown>
  const parts: string[] = []
  if (r.one_liner) parts.push(`📌 ${r.one_liner}`)
  if (Array.isArray(r.bullets) && r.bullets.length)
    parts.push(r.bullets.map((b: unknown) => `• ${b}`).join("\n"))
  if (r.five_sentences) parts.push(`\n${r.five_sentences}`)
  if (r.label) parts.push(`Sentiment: ${r.label} (confidence: ${r.confidence})\n${r.justification}`)
  if (r.explanation) parts.push(`Explanation:\n${r.explanation}`)
  if (r.bugs) parts.push(`Bugs: ${r.bugs}`)
  if (r.time_complexity) parts.push(`Time Complexity: ${r.time_complexity}`)
  if (r.same_topic) parts.push(`Same Topic: ${r.same_topic}\nCommon Themes: ${r.common_themes}\nDifferences: ${r.differences}\n${r.summary}`)
  if (r.answer) parts.push(String(r.answer))
  if (r.video_id) parts.push(`🎬 YouTube video: ${r.video_id}`)
  if (r.duration_seconds) parts.push(`⏱ Audio duration: ${r.duration_seconds}s`)
  if (r.ocr_confidence && typeof r.ocr_confidence === "object") {
    const conf = r.ocr_confidence as Record<string, number>
    parts.push(Object.entries(conf).map(([k, v]) => `OCR confidence (${k}): ${v}%`).join("\n"))
  }
  if (r.error) parts.push(`⚠️ Error: ${r.error}`)
  return parts.length ? parts.join("\n\n") : JSON.stringify(result, null, 2)
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [query, setQuery] = useState("")
  const [files, setFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!loading) inputRef.current?.focus()
  }, [loading])

  const handleSend = async () => {
    if (!query.trim() && files.length === 0) return

    const userMsg: Message = { role: "user", content: query }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)
    setQuery("")

    const formData = new FormData()
    formData.append("query", query)
    files.forEach(f => formData.append("files", f))

    // Add a streaming placeholder agent message
    const agentMsgIndex = messages.length + 1
    setMessages(prev => [...prev, {
      role: "agent",
      content: "",
      planTrace: [],
      streaming: true,
    }])

    try {
      const res = await fetch(`${BACKEND}/chat/stream`, { method: "POST", body: formData })
      if (!res.ok || !res.body) throw new Error("Stream failed")

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      let traceSteps: TraceStep[] = []
      let extractedText = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n\n")
        buffer = lines.pop() ?? ""

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          const raw = line.replace("data: ", "").trim()
          if (raw === "[DONE]") break

          try {
            const event = JSON.parse(raw)

            if (event.type === "trace") {
              traceSteps = [...traceSteps, event.step]
              setMessages(prev => prev.map((m, i) =>
                i === agentMsgIndex ? { ...m, planTrace: traceSteps } : m
              ))
            } else if (event.type === "extracted") {
              extractedText = event.text
              setMessages(prev => prev.map((m, i) =>
                i === agentMsgIndex ? { ...m, extractedText } : m
              ))
            } else if (event.type === "result") {
              const content = event.follow_up
                ? `❓ ${event.follow_up}`
                : formatResult(event.data)
              setMessages(prev => prev.map((m, i) =>
                i === agentMsgIndex
                  ? { ...m, content, streaming: false, followUp: event.follow_up, ocrMeta: event.ocr_meta }
                  : m
              ))
              if (!event.follow_up) setFiles([])
            } else if (event.type === "error") {
              setMessages(prev => prev.map((m, i) =>
                i === agentMsgIndex ? { ...m, content: `⚠️ ${event.message}`, streaming: false } : m
              ))
            }
          } catch {
            // skip malformed event
          }
        }
      }
    } catch {
      setMessages(prev => prev.map((m, i) =>
        i === agentMsgIndex
          ? { ...m, content: "Error: Could not reach backend.", streaming: false }
          : m
      ))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="app-logo">⚡</span>
        <h1 className="app-title">QueryPilot</h1>
        <span className="app-subtitle">Multi-modal AI Agent</span>
      </header>
      <ChatWindow messages={messages} loading={loading} />
      <div className="input-row">
        <FileUpload files={files} setFiles={setFiles} />
        <div className="query-row">
          <input
            ref={inputRef}
            className="query-input"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !loading && handleSend()}
            placeholder="Ask anything — or upload a PDF, image, or audio file…"
            disabled={loading}
          />
          <button
            className={`send-btn ${loading ? "send-btn--loading" : ""}`}
            onClick={handleSend}
            disabled={loading}
          >
            {loading ? <span className="spinner" /> : "Send"}
          </button>
        </div>
      </div>
    </div>
  )
}
