import { useState } from 'react'

export default function Test() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const testAPI = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/generate_quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: 'Mathematics',
          difficulty: 'easy',
          num_questions: 2
        })
      })
      
      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({ error: error.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-center mb-6">EduSense Test Page</h1>
        
        <div className="space-y-4">
          <button
            onClick={testAPI}
            disabled={loading}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test API'}
          </button>
          
          {result && (
            <div className="mt-4 p-4 bg-gray-100 rounded">
              <h3 className="font-semibold mb-2">API Response:</h3>
              <pre className="text-sm overflow-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>
        
        <div className="mt-6 text-center">
          <a href="/" className="text-blue-500 hover:underline">
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}
