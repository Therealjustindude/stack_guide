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
  static async getHealth(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.json()
  }

  static async getFiles(): Promise<FilesResponse> {
    const response = await fetch(`${API_BASE_URL}/files`)
    if (!response.ok) {
      throw new Error('Failed to fetch files')
    }
    return response.json()
  }

  static async uploadFile(file: File): Promise<UploadResponse> {
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
