import { useState } from "react"

interface FileUploadProps {
  onUploadSuccess: () => void
}

export function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState("")

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    setMessage("")

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8081/upload', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        setMessage(`✅ ${data.message}`)
        onUploadSuccess()
      } else {
        const errorData = await response.json()
        setMessage(`❌ Error: ${errorData.error}`)
      }
    } catch (error) {
      console.error('Upload error:', error)
      setMessage('❌ Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-800">📁 Upload Documents</h3>
      
      <div className="flex items-center space-x-4">
        <input
          type="file"
          onChange={handleFileUpload}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          disabled={uploading}
        />
      </div>

      {uploading && (
        <div className="text-blue-600 text-sm">
          ⏳ Uploading...
        </div>
      )}

      {message && (
        <div className={`text-sm p-3 rounded-lg ${
          message.includes('✅') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {message}
        </div>
      )}
    </div>
  )
}
