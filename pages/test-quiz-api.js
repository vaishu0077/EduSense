import { useState } from 'react'

export default function TestQuizAPI() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [apiStatus, setApiStatus] = useState(null)

  const checkAPIStatus = async () => {
    try {
      const response = await fetch('/api/ai-quiz-generation')
      const data = await response.json()
      setApiStatus(data)
    } catch (error) {
      setApiStatus({ error: error.message })
    }
  }

  const testQuizAPI = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/ai-quiz-generation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: 'Smart cities are urban areas that use different types of electronic methods and sensors to collect data. They use this data to manage assets, resources and services efficiently.',
          filename: 'Smart Cities Test',
          num_questions: 3,
          difficulty: 'medium',
          topic: 'Smart Cities'
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
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Quiz API Test</h1>
        
        <div className="space-x-4">
          <button
            onClick={checkAPIStatus}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            Check API Status
          </button>
          
          <button
            onClick={testQuizAPI}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test Quiz API'}
          </button>
        </div>

        {apiStatus && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">API Status:</h2>
            <pre className="bg-white p-4 rounded-lg border overflow-auto">
              {JSON.stringify(apiStatus, null, 2)}
            </pre>
          </div>
        )}

        {result && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Result:</h2>
            <pre className="bg-white p-4 rounded-lg border overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
