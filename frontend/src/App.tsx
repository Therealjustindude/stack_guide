import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileUpload } from "@/components/FileUpload"
import { FileList } from "@/components/FileList"
import { StatusDisplay } from "@/components/StatusDisplay"
import { ApiService } from "@/services/api"
import type { FileInfo } from "@/services/api"

function App() {
  const [files, setFiles] = useState<FileInfo[]>([])

  const fetchFiles = async () => {
    try {
      const data = await ApiService.getFiles()
      setFiles(data.files || [])
    } catch (error) {
      console.error('Error fetching files:', error)
    }
  }

  const handleUploadSuccess = () => {
    fetchFiles()
  }

  // Load files on component mount
  useEffect(() => {
    fetchFiles()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl shadow-lg hover:shadow-xl transition-all duration-300">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-gray-900 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            🚀 Stack Guide
          </CardTitle>
          <CardDescription className="text-gray-600 text-lg">
            Local-first AI Knowledge Assistant
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <FileUpload onUploadSuccess={handleUploadSuccess} />
          <FileList files={files} onRefresh={fetchFiles} />
          <StatusDisplay />
          
          <p className="text-xs text-gray-500 text-center">
            Spike 3: Frontend-Backend Integration Complete ✅
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default App
