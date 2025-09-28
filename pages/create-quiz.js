import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { Brain, Plus, X, Save, Play } from 'lucide-react'
import toast from 'react-hot-toast'

export default function CreateQuiz() {
  const { user, loading } = useAuth()
  const router = useRouter()
  
  const [quizData, setQuizData] = useState({
    title: '',
    topic: '',
    difficulty: 'medium',
    numQuestions: 5,
    timeLimit: 30, // Time limit in minutes
    questions: [
      {
        question: '',
        options: ['', '', '', ''],
        correct_answer: 0,
        explanation: ''
      }
    ]
  })
  
  const [generating, setGenerating] = useState(false)

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

  const addQuestion = () => {
    setQuizData(prev => ({
      ...prev,
      questions: [
        ...prev.questions,
        {
          question: '',
          options: ['', '', '', ''],
          correct_answer: 0,
          explanation: ''
        }
      ]
    }))
  }

  const removeQuestion = (index) => {
    if (quizData.questions.length > 1) {
      setQuizData(prev => ({
        ...prev,
        questions: prev.questions.filter((_, i) => i !== index)
      }))
    }
  }

  const updateQuestion = (questionIndex, field, value) => {
    setQuizData(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => 
        i === questionIndex ? { ...q, [field]: value } : q
      )
    }))
  }

  const updateOption = (questionIndex, optionIndex, value) => {
    setQuizData(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => 
        i === questionIndex 
          ? { ...q, options: q.options.map((opt, j) => j === optionIndex ? value : opt) }
          : q
      )
    }))
  }

  const generateWithAI = async () => {
    if (!quizData.topic.trim()) {
      toast.error('Please enter a topic first')
      return
    }

    setGenerating(true)
    try {
      const response = await fetch('/api/generate_quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: quizData.topic,
          difficulty: quizData.difficulty,
          num_questions: quizData.numQuestions,
          time_limit: quizData.timeLimit
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate quiz')
      }

      const data = await response.json()
      
      let questions = []
      if (data.quiz && data.quiz.questions) {
        questions = data.quiz.questions
      } else if (data.questions) {
        questions = data.questions
      }

      if (questions && questions.length > 0) {
        setQuizData(prev => ({
          ...prev,
          title: `${quizData.topic} Quiz`,
          questions: questions.map(q => ({
            question: q.question,
            options: q.options,
            correct_answer: q.correct_answer,
            explanation: q.explanation || ''
          }))
        }))
        toast.success('Quiz generated successfully!')
      } else {
        throw new Error('No questions generated')
      }
    } catch (error) {
      console.error('Error generating quiz:', error)
      toast.error('Failed to generate quiz with AI. You can create questions manually.')
    } finally {
      setGenerating(false)
    }
  }

  const startQuiz = () => {
    if (!quizData.title.trim()) {
      toast.error('Please enter a quiz title')
      return
    }

    if (quizData.questions.some(q => !q.question.trim() || q.options.some(opt => !opt.trim()))) {
      toast.error('Please fill in all questions and options')
      return
    }

    // Store quiz in localStorage for the quiz page
    const quizWithTimeLimit = {
      ...quizData,
      timeLimit: quizData.timeLimit
    }
    localStorage.setItem('customQuiz', JSON.stringify(quizWithTimeLimit))
    router.push('/take-quiz')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-indigo-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">Create Quiz</span>
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

      {/* Notice */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Brain className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-800">
                <strong>Quiz Creator Mode:</strong> This page is for creating custom quizzes. 
                The correct answers are shown here for quiz creators to set up the quiz properly. 
                When students take the quiz, they won't see the correct answers.
              </p>
            </div>
          </div>
        </div>
      </div>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Quiz Settings */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Quiz Settings</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quiz Title
                </label>
                <input
                  type="text"
                  value={quizData.title}
                  onChange={(e) => setQuizData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter quiz title"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Topic
                </label>
                <input
                  type="text"
                  value={quizData.topic}
                  onChange={(e) => setQuizData(prev => ({ ...prev, topic: e.target.value }))}
                  placeholder="e.g., Mathematics, Physics, History"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty
                </label>
                <select
                  value={quizData.difficulty}
                  onChange={(e) => setQuizData(prev => ({ ...prev, difficulty: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Questions
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={quizData.numQuestions}
                  onChange={(e) => setQuizData(prev => ({ ...prev, numQuestions: parseInt(e.target.value) || 5 }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time Limit (minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  max="120"
                  value={quizData.timeLimit}
                  onChange={(e) => setQuizData(prev => ({ ...prev, timeLimit: parseInt(e.target.value) || 30 }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={generateWithAI}
                  disabled={generating || !quizData.topic.trim()}
                  className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {generating ? 'Generating...' : 'Generate with AI'}
                </button>
              </div>
            </div>
          </div>

          {/* Quiz Status */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-900">Quiz Status</h2>
              {quizData.questions.length > 0 && (
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    {quizData.questions.length} questions ready
                  </span>
                  <button
                    onClick={startQuiz}
                    className="flex items-center px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Attempt Quiz
                  </button>
                </div>
              )}
            </div>

            {/* Quiz Summary - Hidden Questions */}
            {quizData.questions.length > 0 ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <div className="flex-shrink-0">
                    <Brain className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-medium text-blue-900">
                      Quiz Ready!
                    </h3>
                    <p className="text-sm text-blue-700">
                      Your quiz has been generated with {quizData.questions.length} questions.
                      Click "Attempt Quiz" to start taking the quiz.
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-blue-900">Time Limit:</span>
                    <span className="ml-2 text-blue-700">{quizData.timeLimit} minutes</span>
                  </div>
                  <div>
                    <span className="font-medium text-blue-900">Difficulty:</span>
                    <span className="ml-2 text-blue-700 capitalize">{quizData.difficulty}</span>
                  </div>
                  <div>
                    <span className="font-medium text-blue-900">Questions:</span>
                    <span className="ml-2 text-blue-700">{quizData.questions.length}</span>
                  </div>
                  <div>
                    <span className="font-medium text-blue-900">Topic:</span>
                    <span className="ml-2 text-blue-700">{quizData.topic}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
                <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Quiz Generated Yet
                </h3>
                <p className="text-gray-600">
                  Click "Generate with AI" to create your quiz questions.
                </p>
              </div>
            )}
          </div>

          {/* Actions - Removed duplicate buttons, using Attempt Quiz button in status section */}
        </div>
      </main>
    </div>
  )
}
