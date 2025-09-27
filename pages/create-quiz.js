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
          num_questions: 5
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
    localStorage.setItem('customQuiz', JSON.stringify(quizData))
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

          {/* Questions */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-900">Questions</h2>
              <button
                onClick={addQuestion}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Question
              </button>
            </div>

            {quizData.questions.map((question, questionIndex) => (
              <div key={questionIndex} className="border border-gray-200 rounded-lg p-6 mb-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Question {questionIndex + 1}
                  </h3>
                  {quizData.questions.length > 1 && (
                    <button
                      onClick={() => removeQuestion(questionIndex)}
                      className="text-red-600 hover:text-red-500"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  )}
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Question Text
                    </label>
                    <textarea
                      value={question.question}
                      onChange={(e) => updateQuestion(questionIndex, 'question', e.target.value)}
                      placeholder="Enter your question"
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Options
                    </label>
                    <div className="space-y-2">
                      {question.options.map((option, optionIndex) => (
                        <div key={optionIndex} className="flex items-center space-x-3">
                          <input
                            type="radio"
                            name={`correct-${questionIndex}`}
                            checked={question.correct_answer === optionIndex}
                            onChange={() => updateQuestion(questionIndex, 'correct_answer', optionIndex)}
                            className="h-4 w-4 text-indigo-600"
                          />
                          <input
                            type="text"
                            value={option}
                            onChange={(e) => updateOption(questionIndex, optionIndex, e.target.value)}
                            placeholder={`Option ${String.fromCharCode(65 + optionIndex)}`}
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          />
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Explanation (Optional)
                    </label>
                    <textarea
                      value={question.explanation}
                      onChange={(e) => updateQuestion(questionIndex, 'explanation', e.target.value)}
                      placeholder="Explain why this answer is correct"
                      rows={2}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-4">
            <button
              onClick={() => router.push('/')}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={startQuiz}
              className="flex items-center px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
            >
              <Play className="h-4 w-4 mr-2" />
              Start Quiz
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
