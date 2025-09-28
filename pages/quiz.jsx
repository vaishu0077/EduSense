import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  Volume2, 
  Mic, 
  MicOff,
  ArrowLeft,
  ArrowRight,
  Brain,
  Lightbulb,
  GraduationCap,
  User
} from 'lucide-react'
import { textToSpeech, speechToText } from '../utils/accessibility'
import toast from 'react-hot-toast'

export default function Quiz() {
  const { user } = useAuth()
  const router = useRouter()
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState('')
  const [responses, setResponses] = useState({})
  const [timeRemaining, setTimeRemaining] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const [showHint, setShowHint] = useState(false)
  const [quiz, setQuiz] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [quizStarted, setQuizStarted] = useState(false)
  const [quizCompleted, setQuizCompleted] = useState(false)
  const [quizResults, setQuizResults] = useState(null)
  const [reviewMode, setReviewMode] = useState(false)

  useEffect(() => {
    if (!user) {
      router.push('/auth')
      return
    }
    loadQuiz()
  }, [user, router])

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000)
      return () => clearTimeout(timer)
    } else if (timeRemaining === 0) {
      handleSubmitQuiz()
    }
  }, [timeRemaining])

  const generateQuizFromMaterial = async (quizData) => {
    try {
      // Use AI-suggested questions if available (but still generate proper options)
      if (quizData.suggestedQuestions && quizData.suggestedQuestions.length > 0) {
        // For now, skip suggested questions and use AI generation for better options
        console.log('Using AI generation instead of suggested questions for better options')
      }

      // If no suggested questions, generate from content using AI
      console.log('Sending quiz generation request:', {
        topic: quizData.topic,
        difficulty: quizData.difficulty,
        num_questions: quizData.numQuestions || 5,
        time_limit: quizData.timeLimit,
        material_content_length: quizData.materialContent?.length || 0,
        has_ai_analysis: !!quizData.aiAnalysis
      })
      
      const response = await fetch('/api/generate_quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: quizData.topic,
          difficulty: quizData.difficulty,
          num_questions: quizData.numQuestions || 5,
          time_limit: quizData.timeLimit,
          material_content: quizData.materialContent, // Pass the actual content
          ai_analysis: quizData.aiAnalysis // Pass the AI analysis
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Quiz generation response:', data)
      
      if (data.success && data.questions) {
        console.log('Questions received:', data.questions)
        setQuiz({
          ...quizData,
          questions: data.questions
        })
      } else {
        console.error('Quiz generation failed:', data)
        throw new Error('Failed to generate quiz from material')
      }
    } catch (error) {
      console.error('Error generating quiz from material:', error)
      toast.error('Failed to generate quiz from material content')
      
      // Create a fallback quiz with basic questions
      const fallbackQuiz = {
        ...quizData,
        questions: [
          {
            id: 1,
            question_text: `What is the main topic of this ${quizData.topic} material?`,
            question_type: 'multiple_choice',
            options: [
              'General concepts',
              'Advanced topics', 
              'Basic principles',
              'Complex theories'
            ],
            correct_answer: 0,
            explanation: 'This question tests your understanding of the main topic'
          },
          {
            id: 2,
            question_text: `Which of the following best describes the content of this material?`,
            question_type: 'multiple_choice',
            options: [
              'Educational content',
              'Technical documentation',
              'Research findings',
              'Practical guidelines'
            ],
            correct_answer: 0,
            explanation: 'This question evaluates your comprehension of the material type'
          }
        ]
      }
      
      setQuiz(fallbackQuiz)
      setLoading(false)
      toast.success('Quiz generated with fallback questions')
    }
  }

  const loadQuiz = async () => {
    try {
      // Check if there's a stored quiz from localStorage first
      const storedQuiz = localStorage.getItem('materialQuiz')
      if (storedQuiz) {
        const quizData = JSON.parse(storedQuiz)
        
        // If it's a material-based quiz, generate questions from content
        if (quizData.materialContent && quizData.aiAnalysis) {
          await generateQuizFromMaterial(quizData)
        } else {
          // Check if quiz has questions, if not create fallback
          if (!quizData.questions || quizData.questions.length === 0) {
            console.log('Quiz has no questions, creating fallback')
            const fallbackQuiz = {
              ...quizData,
              questions: [
                {
                  id: 1,
                  question_text: `What is the main topic of this ${quizData.topic || 'material'}?`,
                  question_type: 'multiple_choice',
                  options: [
                    'General concepts',
                    'Advanced topics', 
                    'Basic principles',
                    'Complex theories'
                  ],
                  correct_answer: 0,
                  explanation: 'This question tests your understanding of the main topic'
                },
                {
                  id: 2,
                  question_text: `Which best describes this ${quizData.topic || 'material'} content?`,
                  question_type: 'multiple_choice',
                  options: [
                    'Educational content',
                    'Technical documentation',
                    'Research findings',
                    'Practical guidelines'
                  ],
                  correct_answer: 0,
                  explanation: 'This question evaluates your comprehension of the material type'
                }
              ]
            }
            setQuiz(fallbackQuiz)
          } else {
            setQuiz(quizData)
          }
          setLoading(false)
        }
        return
      }

      const response = await fetch('/api/generate_quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: router.query.topic || 'Mathematics',
          difficulty: router.query.difficulty || 'medium',
          num_questions: parseInt(router.query.num_questions) || 5,
          time_limit: parseInt(router.query.time_limit) || 30
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('API Response:', data) // Debug log
      
      // Check if the response has the expected structure
      if (!data || (!data.questions && !data.quiz)) {
        throw new Error('Invalid response format from API')
      }
      
      // Handle different response formats
      let questions = []
      if (data.quiz && data.quiz.questions) {
        questions = data.quiz.questions
      } else if (data.questions) {
        questions = data.questions
      } else {
        throw new Error('No questions found in API response')
      }
      
      if (!questions || questions.length === 0) {
        throw new Error('No questions generated')
      }
      
      // Transform the API response to match our component structure
      const transformedQuiz = {
        id: Date.now(),
        title: `${router.query.topic || 'Mathematics'} Quiz`,
        description: `Test your knowledge in ${router.query.topic || 'Mathematics'}`,
        time_limit: 5, // 5 minutes
        questions: questions.map((q, index) => ({
          id: index + 1,
          question_text: q.question || q.question_text,
          question_type: 'multiple_choice',
          options: q.options,
          correct_answer: q.correct_answer,
          hints: q.explanation ? [q.explanation] : []
        }))
      }
      
      setQuiz(transformedQuiz)
      setTimeRemaining(5 * 60) // 5 minutes in seconds
    } catch (error) {
      console.error('Error loading quiz:', error)
      toast.error(`Failed to load quiz: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const currentQuestion = quiz?.questions?.[currentQuestionIndex]
  const isLastQuestion = currentQuestionIndex === (quiz?.questions?.length || 0) - 1
  const isFirstQuestion = currentQuestionIndex === 0

  const handleAnswerSelect = (answer) => {
    setSelectedAnswer(answer)
    setResponses(prev => ({
      ...prev,
      [currentQuestion.id]: answer
    }))
  }

  const handleNextQuestion = () => {
    if (selectedAnswer) {
      setCurrentQuestionIndex(prev => prev + 1)
      setSelectedAnswer(responses[quiz.questions[currentQuestionIndex + 1]?.id] || '')
      setShowHint(false)
    } else {
      toast.error('Please select an answer before continuing')
    }
  }

  const handlePreviousQuestion = () => {
    setCurrentQuestionIndex(prev => prev - 1)
    setSelectedAnswer(responses[quiz.questions[currentQuestionIndex - 1]?.id] || '')
    setShowHint(false)
  }

  const startQuiz = () => {
    setQuizStarted(true)
    if (quiz.timeLimit) {
      setTimeRemaining(quiz.timeLimit * 60) // Convert minutes to seconds
    }
  }

  const goToDashboard = () => {
    router.push('/')
  }

  const reviewAnswers = () => {
    setCurrentQuestionIndex(0)
    setQuizStarted(true)
    setQuizCompleted(false)
    setReviewMode(true)
  }

  const handleSubmitQuiz = async () => {
    setSubmitting(true)
    try {
      const finalResponses = Object.entries(responses).map(([questionId, answer]) => ({
        question_id: parseInt(questionId),
        answer: answer
      }))
      
      const response = await fetch('/api/performance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quiz_id: quiz.id,
          responses: finalResponses,
          time_taken: quiz.time_limit * 60 - timeRemaining
        })
      })
      
      const result = await response.json()
      
      // Calculate detailed results
      const detailedResults = quiz.questions.map((question, index) => {
        const userAnswer = responses[question.id]
        const isCorrect = userAnswer === question.correct_answer
        return {
          question: question,
          userAnswer: userAnswer,
          correctAnswer: question.correct_answer,
          isCorrect: isCorrect,
          explanation: question.explanation
        }
      })
      
      // Calculate score manually if API doesn't provide it
      const correctCount = detailedResults.filter(r => r.isCorrect).length
      const calculatedScore = Math.round((correctCount / quiz.questions.length) * 100)
      
      setQuizResults({
        score: result.score || calculatedScore,
        totalQuestions: quiz.questions.length,
        correctAnswers: correctCount,
        detailedResults: detailedResults,
        timeTaken: quiz.timeLimit ? (quiz.timeLimit * 60 - timeRemaining) : null
      })
      
      setQuizCompleted(true)
      toast.success(`Quiz completed! Score: ${result.score}%`)
    } catch (error) {
      console.error('Error submitting quiz:', error)
      toast.error('Failed to submit quiz')
    } finally {
      setSubmitting(false)
    }
  }

  const handleTextToSpeech = () => {
    if (currentQuestion) {
      textToSpeech(currentQuestion.question_text)
    }
  }

  const handleSpeechToText = async () => {
    try {
      setIsListening(true)
      const transcript = await speechToText()
      setSelectedAnswer(transcript)
      setResponses(prev => ({
        ...prev,
        [currentQuestion.id]: transcript
      }))
    } catch (error) {
      toast.error('Speech recognition failed')
    } finally {
      setIsListening(false)
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!user) {
    return null
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
        <div className="text-center">
          <div className="spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading AI-generated quiz...</p>
        </div>
      </div>
    )
  }

  if (!quiz) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
        <div className="text-center">
          <XCircle className="h-12 w-12 text-red-500 dark:text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Quiz not found</h3>
          <p className="text-gray-500 dark:text-gray-400">The quiz you're looking for doesn't exist.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <GraduationCap className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
              <span className="ml-2 text-xl font-bold text-gray-900 dark:text-gray-100">EduSense</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/profile')}
                className="flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
              >
                <User className="w-4 h-4" />
                <span>Profile</span>
              </button>
              <button
                onClick={() => router.push('/')}
                className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
              >
                Dashboard
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="card mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
                <p className="text-gray-600">{quiz.description}</p>
              </div>
              <div className="flex items-center space-x-4">
                {timeRemaining !== null && (
                  <div className="flex items-center text-lg font-medium">
                    <Clock className="h-5 w-5 mr-2 text-primary-600" />
                    {formatTime(timeRemaining)}
                  </div>
                )}
                <div className="text-sm text-gray-500">
                  Question {currentQuestionIndex + 1} of {quiz.questions.length}
                </div>
              </div>
            </div>
          </div>

          {/* Quiz Completion Screen */}
          {quizCompleted && quizResults ? (
            <div className="card mb-6 text-center">
              <div className="mb-6">
                <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Quiz Completed!</h2>
                <div className="text-4xl font-bold text-indigo-600 mb-2">{quizResults.score}%</div>
                <p className="text-gray-600 mb-4">
                  You got {quizResults.correctAnswers} out of {quizResults.totalQuestions} questions correct
                  {quizResults.timeTaken && ` in ${Math.floor(quizResults.timeTaken / 60)}:${(quizResults.timeTaken % 60).toString().padStart(2, '0')}`}
                </p>
                
                <div className="flex justify-center space-x-4 mb-6">
                  <button
                    onClick={reviewAnswers}
                    className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors flex items-center"
                  >
                    <Brain className="h-5 w-5 mr-2" />
                    Review Answers
                  </button>
                  <button
                    onClick={goToDashboard}
                    className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors flex items-center"
                  >
                    <GraduationCap className="h-5 w-5 mr-2" />
                    Dashboard
                  </button>
                </div>
              </div>
            </div>
          ) : !quizStarted ? (
            /* Quiz Start Screen */
            <div className="card mb-6 text-center">
              <div className="mb-6">
                <Brain className="h-16 w-16 text-indigo-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Ready to Start?</h2>
                <p className="text-gray-600 mb-4">
                  This quiz has {quiz.questions.length} questions
                  {quiz.timeLimit && ` with a ${quiz.timeLimit} minute time limit`}.
                </p>
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Quiz Instructions:</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Read each question carefully</li>
                    <li>• Select the best answer</li>
                    <li>• Use the hint button if you need help</li>
                    <li>• You can navigate between questions</li>
                    {quiz.timeLimit && <li>• Complete within the time limit</li>}
                  </ul>
                </div>
                <button
                  onClick={startQuiz}
                  className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors"
                >
                  Start Quiz
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Progress Bar */}
              <div className="card mb-6">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentQuestionIndex + 1) / quiz.questions.length) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Question */}
              {currentQuestion && (
            <div className="card mb-6">
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <div className="flex items-center mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 mr-4">
                      {currentQuestion.question_text}
                    </h2>
                    <button
                      onClick={handleTextToSpeech}
                      className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                      title="Read question aloud"
                    >
                      <Volume2 className="h-5 w-5" />
                    </button>
                  </div>
                  
                  {/* Review Mode Information */}
                  {reviewMode && quizResults && (
                    <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-center mb-2">
                        {quizResults.detailedResults[currentQuestionIndex]?.isCorrect ? (
                          <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-600 mr-2" />
                        )}
                        <span className={`font-medium ${
                          quizResults.detailedResults[currentQuestionIndex]?.isCorrect 
                            ? 'text-green-800' 
                            : 'text-red-800'
                        }`}>
                          {quizResults.detailedResults[currentQuestionIndex]?.isCorrect 
                            ? 'Correct!' 
                            : 'Incorrect'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-700">
                        <p><strong>Your answer:</strong> {quizResults.detailedResults[currentQuestionIndex]?.userAnswer || 'No answer'}</p>
                        <p><strong>Correct answer:</strong> {quizResults.detailedResults[currentQuestionIndex]?.correctAnswer}</p>
                        {quizResults.detailedResults[currentQuestionIndex]?.explanation && (
                          <p className="mt-2"><strong>Explanation:</strong> {quizResults.detailedResults[currentQuestionIndex].explanation}</p>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {currentQuestion.hints && currentQuestion.hints.length > 0 && (
                    <div className="mb-4">
                      <button
                        onClick={() => setShowHint(!showHint)}
                        className="flex items-center text-sm text-primary-600 hover:text-primary-700"
                      >
                        <Lightbulb className="h-4 w-4 mr-1" />
                        {showHint ? 'Hide Hint' : 'Show Hint'}
                      </button>
                      {showHint && (
                        <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <p className="text-sm text-yellow-800">
                            {currentQuestion.hints[0]}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Answer Options */}
              <div className="space-y-3">
                {(() => {
                  console.log('Current question:', currentQuestion)
                  console.log('Question type:', currentQuestion.question_type)
                  console.log('Options:', currentQuestion.options)
                  console.log('Has options:', !!currentQuestion.options)
                  
                  if (currentQuestion.question_type === 'multiple_choice' && currentQuestion.options && currentQuestion.options.length > 0) {
                    return currentQuestion.options.map((option, index) => (
                      <label
                        key={index}
                        className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                          selectedAnswer === option
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <input
                          type="radio"
                          name="answer"
                          value={option}
                          checked={selectedAnswer === option}
                          onChange={(e) => handleAnswerSelect(e.target.value)}
                          className="sr-only"
                        />
                        <div className={`w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center ${
                          selectedAnswer === option
                            ? 'border-primary-500 bg-primary-500'
                            : 'border-gray-300'
                        }`}>
                          {selectedAnswer === option && (
                            <div className="w-2 h-2 bg-white rounded-full"></div>
                          )}
                        </div>
                        <span className="text-gray-900">{option}</span>
                      </label>
                    ))
                  } else {
                    console.log('Falling back to text input - no options available')
                    return (
                  <div className="space-y-4">
                    <textarea
                      value={selectedAnswer}
                      onChange={(e) => handleAnswerSelect(e.target.value)}
                      placeholder="Type your answer here..."
                      className="input-field h-32 resize-none"
                    />
                    <button
                      onClick={handleSpeechToText}
                      disabled={isListening}
                      className={`btn-secondary flex items-center ${
                        isListening ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                    >
                      {isListening ? (
                        <>
                          <MicOff className="h-4 w-4 mr-2" />
                          Listening...
                        </>
                      ) : (
                        <>
                          <Mic className="h-4 w-4 mr-2" />
                          Voice Input
                        </>
                      )}
                    </button>
                  </div>
                    )
                  }
                })()}
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="card mb-6">
            <div className="flex items-center justify-between">
              <button
                onClick={handlePreviousQuestion}
                disabled={isFirstQuestion}
                className={`btn-secondary flex items-center ${
                  isFirstQuestion ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </button>

              <div className="flex items-center space-x-2">
                {quiz.questions.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setCurrentQuestionIndex(index)
                      setSelectedAnswer(responses[quiz.questions[index].id] || '')
                      setShowHint(false)
                    }}
                    className={`w-8 h-8 rounded-full text-sm font-medium ${
                      index === currentQuestionIndex
                        ? 'bg-primary-600 text-white'
                        : responses[quiz.questions[index].id]
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>

              {reviewMode ? (
                <div className="flex space-x-2">
                  <button
                    onClick={goToDashboard}
                    className="btn-secondary flex items-center"
                  >
                    <GraduationCap className="h-4 w-4 mr-2" />
                    Dashboard
                  </button>
                  {!isLastQuestion && (
                    <button
                      onClick={handleNextQuestion}
                      className="btn-primary flex items-center"
                    >
                      Next
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </button>
                  )}
                </div>
              ) : isLastQuestion ? (
                <button
                  onClick={handleSubmitQuiz}
                  disabled={!selectedAnswer || submitting}
                  className="btn-primary flex items-center"
                >
                  {submitting ? (
                    <div className="spinner w-4 h-4 mr-2"></div>
                  ) : (
                    <CheckCircle className="h-4 w-4 mr-2" />
                  )}
                  Submit Quiz
                </button>
              ) : (
                <button
                  onClick={handleNextQuestion}
                  disabled={!selectedAnswer}
                  className="btn-primary flex items-center"
                >
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </button>
              )}
            </div>
          </div>
            </>
          )}

          {/* AI Features */}
          <div className="card bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Brain className="h-6 w-6 text-purple-600 mr-3" />
                <div>
                  <h3 className="font-medium text-gray-900">AI-Powered Features</h3>
                  <p className="text-sm text-gray-600">
                    This quiz was generated using Gemini AI for personalized learning
                  </p>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleTextToSpeech}
                  className="btn-secondary text-sm"
                >
                  <Volume2 className="h-4 w-4 mr-1" />
                  TTS
                </button>
                <button
                  onClick={handleSpeechToText}
                  disabled={isListening}
                  className="btn-secondary text-sm"
                >
                  <Mic className="h-4 w-4 mr-1" />
                  STT
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
