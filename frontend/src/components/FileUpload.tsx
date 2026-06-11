interface Props {
  files: File[]
  setFiles: (f: File[]) => void
}

const iconFor = (name: string) => {
  const ext = name.split(".").pop() ?? ""
  if (["jpg", "jpeg", "png"].includes(ext)) return "🖼"
  if (ext === "pdf") return "📄"
  if (["mp3", "wav", "m4a"].includes(ext)) return "🎵"
  return "📎"
}

export default function FileUpload({ files, setFiles }: Props) {
  return (
    <div className="file-upload">
      <label className="file-label">
        <span className="file-label-text">📎 Attach files</span>
        <input
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.mp3,.wav,.m4a"
          onChange={e => e.target.files && setFiles(Array.from(e.target.files))}
          className="file-input-hidden"
        />
      </label>
      {files.length > 0 && (
        <div className="file-chips">
          {files.map((f, i) => (
            <span key={i} className="file-chip">
              {iconFor(f.name)} {f.name}
              <button
                className="file-chip-remove"
                onClick={() => setFiles(files.filter((_, j) => j !== i))}
              >×</button>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
