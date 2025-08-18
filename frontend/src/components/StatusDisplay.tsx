export function StatusDisplay() {
  return (
    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
      <p className="text-sm text-blue-800 font-medium">
        🧪 Testing Frontend-Backend Integration:
      </p>
      <ul className="text-xs text-blue-700 mt-2 space-y-1">
        <li>✅ React + TypeScript + Vite</li>
        <li>✅ Tailwind CSS + shadcn/ui</li>
        <li>✅ Go backend with Gin</li>
        <li>✅ File upload & listing</li>
        <li>✅ API integration</li>
      </ul>
    </div>
  )
}
