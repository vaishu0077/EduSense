import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { Clock, CheckCircle, ArrowRight, ArrowLeft, Trophy } from 'lucide-react'
import toast from 'react-hot-toast'

export default function TakeQuiz() {
  const { user, loading } = useAuth()
  const router = useRouter()
  
  const [quiz, setQuiz] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [answers, setAnswers] = useState([])
  const [timeLeft, setTimeLeft] = useState(300) // 5 minutes
  const [showResults, setShowResults] = useState(false)
  const [score, setScore] = useState(0)

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth')
      return
    }

    // Load quiz from localStorage
    const storedQuiz = localStorage.getItem('customQuiz')
    if (storedQuiz) {
      setQuiz(JSON.parse(storedQuiz))
      setAnswers(new Array(JSON.parse(storedQuiz).questions.length).fill(null))
    } else {
      toast.error('No quiz found')
      router.push('/create-quiz')
    }
  }, [user, loading, router])

  useEffect(() => {
    if (timeLeft > 0 && !showResults) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000)
      return () => clearTimeout(timer)
    } else if (timeLeft === 0) {
      handleFinishQuiz()
    }
  }, [timeLeft, showResults])

  const handleAnswerSelect = (answerIndex) => {
    setSelectedAnswer(answerIndex)
    const newAnswers = [...answers]
    newAnswers[currentQuestion] = answerIndex
    setAnswers(newAnswers)
  }

  const handleNextQuestion = () => {
    if (currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setSelectedAnswer(answers[currentQuestion + 1])
    } else {
      handleFinishQuiz()
    }
  }

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
      setSelectedAnswer(answers[currentQuestion - 1])
    }
  }

  const handleFinishQuiz = () => {
    let correctAnswers = 0
    quiz.questions.forEach((question, index) => {
      if (answers[index] === question.correct_answer) {
        correctAnswers++
      }
    })
    setScore(correctAnswers)
    setShowResults(true)
    
    // Save result to API
    saveQuizResult(correctAnswers)
  }

  const saveQuizResult = async (finalScore) => {
    try {
      await fetch('/api/performance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: quiz.topic,
          difficulty: quiz.difficulty,
          score: finalScore,
          total_questions: quiz.questions.length,
          time_spent: 300 - timeLeft
        })
      })
    } catch (error) {
      console.error('Error saving quiz result:', error)
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!user || !quiz) {
    return null
  }

  if (showResults) {
    const percentage = Math.round((score / quiz.questions.length) * 100)
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <Trophy className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Quiz Complete!</h1>
            
            <div className="text-6xl font-bold text-indigo-600 mb-4">
              {percentage}%
            </div>
            
            <p className="text-xl text-gray-600 mb-6">
              You scored {score} out of {quiz.questions.length} questions correctly
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{score}</div>
                <div className="text-sm text-blue-800">Correct Answers</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{percentage}%</div>
                <div className="text-sm text-green-800">Accuracy</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{formatTime(300 - timeLeft)}</div>
                <div className="text-sm text-purple-800">Time Taken</div>
              </div>
            </div>

            {percentage >= 80 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <p className="text-green-800 font-medium">
                  🎉 Excellent work! You've mastered this topic!
                </p>
              </div>
            )}

            {percentage < 60 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <p className="text-yellow-800 font-medium">
                  💪 Keep practicing! Review the topics and try again.
                </p>
              </div>
            )}

            <div className="space-x-4">
              <button
                onClick={() => router.push('/create-quiz')}
                className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
              >
                Create Another Quiz
              </button>
              <button
                onClick={() => router.push('/progress')}
                className="px-6 py-3 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                View Progress
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const currentQ = quiz.questions[currentQuestion]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
              <p className="text-gray-600">Question {currentQuestion + 1} of {quiz.questions.length}</p>
            </div>
            <div className="flex items-center text-red-500">
              <Clock className="h-5 w-5 mr-2" />
              <span className="font-mono text-lg">{formatTime(timeLeft)}</span>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-indigo-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${((currentQuestion + 1) / quiz.questions.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            {currentQ.question}
          </h2>

          <div className="space-y-3">
            {currentQ.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswerSelect(index)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  selectedAnswer === index
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-900'
                    : 'border-gray-200 bg-gray-50 text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center">
                  <span className="flex-shrink-0 w-8 h-8 rounded-full bg-white border-2 border-gray-300 flex items-center justify-center text-sm font-medium mr-3">
                    {String.fromCharCode(65 + index)}
                  </span>
                  {option}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex justify-between items-center">
            <button
              onClick={handlePreviousQuestion}
              disabled={currentQuestion === 0}
              className="flex items-center px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Previous
            </button>

            <div className="flex space-x-2">
              {quiz.questions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setCurrentQuestion(index)
                    setSelectedAnswer(answers[index])
                  }}
                  className={`w-8 h-8 rounded-full text-sm font-medium ${
                    index === currentQuestion
                      ? 'bg-indigo-600 text-white'
                      : answers[index] !== null
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>

            <button
              onClick={currentQuestion === quiz.questions.length - 1 ? handleFinishQuiz : handleNextQuestion}
              disabled={selectedAnswer === null}
              className="flex items-center px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {currentQuestion === quiz.questions.length - 1 ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Finish Quiz
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
