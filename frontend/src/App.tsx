import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg hover:shadow-xl transition-all duration-300">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-gray-900 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            🚀 Stack Guide
          </CardTitle>
          <CardDescription className="text-gray-600 text-lg">
            Local-first AI Knowledge Assistant
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-gray-700 text-center">
            Welcome to Stack Guide! This is the new React frontend.
          </p>
          
          {/* Test different button variants */}
          <div className="space-y-3">
            <Button className="w-full hover:scale-105 transition-transform">
              Get Started
            </Button>
            
            <Button variant="outline" className="w-full hover:bg-blue-50">
              Learn More
            </Button>
            
            <Button variant="secondary" className="w-full hover:bg-gray-200">
              Documentation
            </Button>
          </div>
          
          {/* Test Tailwind utilities */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-800 font-medium">
              🧪 Testing Tailwind CSS:
            </p>
            <ul className="text-xs text-blue-700 mt-2 space-y-1">
              <li>✅ Colors & gradients</li>
              <li>✅ Hover effects</li>
              <li>✅ Transitions & transforms</li>
              <li>✅ Spacing & typography</li>
            </ul>
          </div>
          
          <p className="text-xs text-gray-500 text-center">
            Spike 1: React Frontend Setup Complete ✅
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default App
