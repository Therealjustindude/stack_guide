export interface FileInfo {
  name: string
  size: number
}

export interface UploadResponse {
  message: string
  filename: string
  size: number
}

export interface FilesResponse {
  files: FileInfo[]
}

const API_BASE_URL = 'http://localhost:8081'

export class ApiService {
  static async getHealth(): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE_URL}/health`)
    if (!response.ok) {
      throw new Error('Backend service is unavailable. Please check if the Go server is running.')
    }
    return response.json()
  }

  static async getFiles(): Promise<FilesResponse> {
    const response = await fetch(`${API_BASE_URL}/files`)
    if (!response.ok) {
      throw new Error('Failed to fetch files from server')
    }
    return response.json()
  }

  static async uploadFile(file: File): Promise<UploadResponse> {
    // Validate file size (10MB limit)
    const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
    if (file.size > MAX_FILE_SIZE) {
      throw new Error(`File size (${(file.size / 1024 / 1024).toFixed(1)}MB) exceeds the 10MB limit`)
    }

    // Validate file type (basic check)
    const allowedExtensions = ['.md', '.txt', '.pdf', '.json', '.csv', '.xml', '.yaml', '.yml']
    const hasValidExtension = allowedExtensions.some(ext => 
      file.name.toLowerCase().endsWith(ext)
    )
    
    if (!hasValidExtension) {
      throw new Error(`File type not supported. Please upload text, markdown, PDF, or data files.`)
    }

    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Upload failed')
    }

    return response.json()
  }
}
