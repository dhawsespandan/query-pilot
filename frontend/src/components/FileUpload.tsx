interface Props {
  files: File[]
  setFiles: (f: File[]) => void
}

export default function FileUpload({ files, setFiles }: Props) {
  return (
    <div style={{ marginBottom: 8 }}>
      <label style={{ fontSize: 13, color: "#374151" }}>
        Attach files (PDF, Image, Audio):&nbsp;
        <input
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.mp3,.wav,.m4a"
          onChange={e => e.target.files && setFiles(Array.from(e.target.files))}
          style={{ fontSize: 13 }}
        />
      </label>
      {files.length > 0 && (
        <div style={{ fontSize: 12, color: "#6b7280", marginTop: 4 }}>
          📎 {files.map(f => f.name).join(", ")}
        </div>
      )}
    </div>
  )
}