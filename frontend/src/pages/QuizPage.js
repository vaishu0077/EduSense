import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
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
  Lightbulb
} from 'lucide-react';
import { api, textToSpeech, speechToText } from '../services/api';
import toast from 'react-hot-toast';

export const QuizPage = () => {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [responses, setResponses] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [attemptId, setAttemptId] = useState(null);

  const { data: quiz, isLoading: quizLoading } = useQuery(
    ['quiz', quizId],
    () => api.quizzes.getQuiz(quizId),
    {
      select: (response) => response.data,
      onSuccess: (data) => {
        if (data.time_limit) {
          setTimeRemaining(data.time_limit * 60); // Convert minutes to seconds
        }
      }
    }
  );

  const { data: attempt, isLoading: attemptLoading } = useQuery(
    ['quiz-attempt', attemptId],
    () => api.quizzes.getAttempt(attemptId),
    {
      enabled: !!attemptId,
      select: (response) => response.data,
    }
  );

  const startAttemptMutation = useMutation(
    () => api.quizzes.startAttempt(quizId),
    {
      onSuccess: (response) => {
        setAttemptId(response.data.id);
        toast.success('Quiz started!');
      },
      onError: (error) => {
        toast.error('Failed to start quiz');
      }
    }
  );

  const submitAttemptMutation = useMutation(
    (responses) => api.quizzes.submitAttempt(attemptId, responses),
    {
      onSuccess: (response) => {
        const result = response.data;
        toast.success(`Quiz completed! Score: ${result.percentage}%`);
        navigate(`/quiz/${quizId}/results`, { state: { result } });
      },
      onError: (error) => {
        toast.error('Failed to submit quiz');
      }
    }
  );

  useEffect(() => {
    if (!attemptId && quiz) {
      startAttemptMutation.mutate();
    }
  }, [quiz, attemptId]);

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0) {
      handleSubmitQuiz();
    }
  }, [timeRemaining]);

  const currentQuestion = quiz?.questions?.[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === (quiz?.questions?.length || 0) - 1;
  const isFirstQuestion = currentQuestionIndex === 0;

  const handleAnswerSelect = (answer) => {
    setSelectedAnswer(answer);
    setResponses(prev => ({
      ...prev,
      [currentQuestion.id]: answer
    }));
  };

  const handleNextQuestion = () => {
    if (selectedAnswer) {
      setCurrentQuestionIndex(prev => prev + 1);
      setSelectedAnswer(responses[quiz.questions[currentQuestionIndex + 1]?.id] || '');
      setShowHint(false);
    } else {
      toast.error('Please select an answer before continuing');
    }
  };

  const handlePreviousQuestion = () => {
    setCurrentQuestionIndex(prev => prev - 1);
    setSelectedAnswer(responses[quiz.questions[currentQuestionIndex - 1]?.id] || '');
    setShowHint(false);
  };

  const handleSubmitQuiz = () => {
    const finalResponses = Object.entries(responses).map(([questionId, answer]) => ({
      question_id: parseInt(questionId),
      answer: answer
    }));
    
    submitAttemptMutation.mutate(finalResponses);
  };

  const handleTextToSpeech = () => {
    if (currentQuestion) {
      textToSpeech(currentQuestion.question_text);
    }
  };

  const handleSpeechToText = async () => {
    try {
      setIsListening(true);
      const transcript = await speechToText();
      setSelectedAnswer(transcript);
      setResponses(prev => ({
        ...prev,
        [currentQuestion.id]: transcript
      }));
    } catch (error) {
      toast.error('Speech recognition failed');
    } finally {
      setIsListening(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (quizLoading || attemptLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-8 h-8"></div>
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="text-center py-12">
        <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Quiz not found</h3>
        <p className="text-gray-500">The quiz you're looking for doesn't exist.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="card">
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

      {/* Progress Bar */}
      <div className="card">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestionIndex + 1) / quiz.questions.length) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Question */}
      {currentQuestion && (
        <div className="card">
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
            {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options ? (
              currentQuestion.options.map((option, index) => (
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
            ) : (
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
            )}
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="card">
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
                  setCurrentQuestionIndex(index);
                  setSelectedAnswer(responses[quiz.questions[index].id] || '');
                  setShowHint(false);
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

          {isLastQuestion ? (
            <button
              onClick={handleSubmitQuiz}
              disabled={!selectedAnswer || submitAttemptMutation.isLoading}
              className="btn-primary flex items-center"
            >
              {submitAttemptMutation.isLoading ? (
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
  );
};
