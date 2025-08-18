import { Button } from "@/components/ui/button"

interface FileInfo {
  name: string
  size: number
}

interface FileListProps {
  files: FileInfo[]
  onRefresh: () => void
}

export function FileList({ files, onRefresh }: FileListProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">📋 Uploaded Files</h3>
        <Button 
          onClick={onRefresh} 
          variant="outline" 
          size="sm"
          className="hover:bg-blue-50"
        >
          🔄 Refresh
        </Button>
      </div>

      {files.length === 0 ? (
        <div className="text-gray-500 text-center py-8">
          No files uploaded yet
        </div>
      ) : (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium text-gray-700">{file.name}</span>
              <span className="text-sm text-gray-500">
                {(file.size / 1024).toFixed(1)} KB
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
