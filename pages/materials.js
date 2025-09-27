import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { BookOpen, Upload, FileText, Brain } from 'lucide-react'

export default function Materials() {
  const { user, loading } = useAuth()
  const router = useRouter()

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!user) {
    router.push('/auth')
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-indigo-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">Study Materials</span>
            </div>
            <button
              onClick={() => router.push('/')}
              className="text-indigo-600 hover:text-indigo-500 font-medium"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Coming Soon Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <Brain className="h-16 w-16 text-indigo-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Study Materials</h1>
          <p className="text-xl text-gray-600 mb-8">
            Upload and manage your study materials with AI-powered insights
          </p>

          {/* Feature Preview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 p-6 rounded-lg">
              <Upload className="h-12 w-12 text-blue-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Documents</h3>
              <p className="text-gray-600">Upload PDFs, notes, and study materials</p>
            </div>

            <div className="bg-green-50 p-6 rounded-lg">
              <FileText className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Analysis</h3>
              <p className="text-gray-600">Get AI-powered summaries and insights</p>
            </div>

            <div className="bg-purple-50 p-6 rounded-lg">
              <Brain className="h-12 w-12 text-purple-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Quizzes</h3>
              <p className="text-gray-600">Generate quizzes from your materials</p>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-yellow-800 mb-2">🚧 Coming Soon!</h3>
            <p className="text-yellow-700">
              This feature is under development. For now, you can create custom quizzes and track your progress!
            </p>
            <div className="mt-4 space-x-4">
              <button
                onClick={() => router.push('/create-quiz')}
                className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors"
              >
                Create a Quiz
              </button>
              <button
                onClick={() => router.push('/progress')}
                className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                View Progress
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
