import { useState } from 'react'
import { useRouter } from 'next/router'

export default function DebugQuiz() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const testQuizAPI = async () => {
    setLoading(true)
    try {
      console.log('Testing quiz API...')
      
      const response = await fetch('/api/generate_quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: 'Mathematics',
          difficulty: 'medium',
          num_questions: 3,
          time_limit: 30
        })
      })
      
      console.log('Response status:', response.status)
      console.log('Response ok:', response.ok)
      
      const data = await response.json()
      console.log('Response data:', data)
      
      setResult({
        status: response.status,
        ok: response.ok,
        data: data
      })
      
    } catch (error) {
      console.error('Quiz API error:', error)
      setResult({
        error: error.message
      })
    } finally {
      setLoading(false)
    }
  }

  const testQuizWithMaterial = async () => {
    setLoading(true)
    try {
      console.log('Testing quiz API with material...')
      
      const response = await fetch('/api/generate_quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: 'Smart Cities',
          difficulty: 'intermediate',
          num_questions: 3,
          time_limit: 30,
          material_content: 'Smart cities use technology to improve urban living. They integrate IoT devices, data analytics, and sustainable energy solutions.',
          ai_analysis: {
            key_topics: ['Smart Cities', 'Technology', 'Urban Development'],
            learning_objectives: ['Understand smart city concepts', 'Learn about IoT integration']
          }
        })
      })
      
      const data = await response.json()
      console.log('Material quiz response:', data)
      
      setResult({
        status: response.status,
        ok: response.ok,
        data: data
      })
      
    } catch (error) {
      console.error('Material quiz API error:', error)
      setResult({
        error: error.message
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Quiz API Debug</h1>
        
        <div className="space-y-4 mb-8">
          <button
            onClick={testQuizAPI}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test Basic Quiz API'}
          </button>
          
          <button
            onClick={testQuizWithMaterial}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 ml-4"
          >
            {loading ? 'Testing...' : 'Test Material Quiz API'}
          </button>
          
          <button
            onClick={() => router.push('/materials')}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 ml-4"
          >
            Back to Materials
          </button>
        </div>

        {result && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">API Response:</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
