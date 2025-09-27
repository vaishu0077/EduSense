import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { 
  BookOpen, 
  Brain, 
  TrendingUp, 
  Clock, 
  Target, 
  Award,
  AlertTriangle,
  CheckCircle,
  Play,
  BarChart3,
  Volume2,
  Mic,
  MicOff,
  GraduationCap
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { textToSpeech, speechToText } from '../utils/accessibility'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const { user, signOut } = useAuth()
  const router = useRouter()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [isListening, setIsListening] = useState(false)
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    if (user) {
      loadDashboardData()
    }
  }, [user])

  const loadDashboardData = async () => {
    try {
      const response = await fetch('/api/performance')
      const data = await response.json()
      setDashboardData(data)
    } catch (error) {
      console.error('Error loading dashboard:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleTextToSpeech = (text) => {
    textToSpeech(text)
  }

  const handleSpeechToText = async () => {
    try {
      setIsListening(true)
      const transcript = await speechToText()
      toast.success(`You said: ${transcript}`)
    } catch (error) {
      toast.error('Speech recognition failed')
    } finally {
      setIsListening(false)
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
        <div className="text-center">
          <GraduationCap className="h-16 w-16 text-primary-600 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome to EduSense</h1>
          <p className="text-gray-600 mb-8">AI-Powered Adaptive Learning Platform</p>
          <button
            onClick={() => router.push('/auth')}
            className="btn-primary text-lg px-8 py-3"
          >
            Get Started
          </button>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-8 h-8"></div>
      </div>
    )
  }

  // Sample data for charts
  const performanceData = [
    { name: 'Week 1', score: 65 },
    { name: 'Week 2', score: 72 },
    { name: 'Week 3', score: 68 },
    { name: 'Week 4', score: 78 },
    { name: 'Week 5', score: 82 },
    { name: 'Week 6', score: 85 },
  ]

  const subjectData = [
    { name: 'Mathematics', value: 85, color: '#3b82f6' },
    { name: 'Science', value: 72, color: '#10b981' },
    { name: 'English', value: 78, color: '#f59e0b' },
    { name: 'History', value: 65, color: '#ef4444' },
  ]

  const stats = [
    {
      name: 'Overall Performance',
      value: `${dashboardData?.overall_score || 75}%`,
      change: '+5%',
      changeType: 'positive',
      icon: TrendingUp,
    },
    {
      name: 'Topics Studied',
      value: dashboardData?.topics_studied || 5,
      change: '+2 this week',
      changeType: 'positive',
      icon: BookOpen,
    },
    {
      name: 'Study Time',
      value: `${Math.round((dashboardData?.total_time || 3600) / 3600)}h`,
      change: '+1.5h today',
      changeType: 'positive',
      icon: Clock,
    },
    {
      name: 'Learning Paths',
      value: dashboardData?.active_paths || 2,
      change: '1 completed',
      changeType: 'positive',
      icon: Target,
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <GraduationCap className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">EduSense</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => handleTextToSpeech('Welcome to your learning dashboard')}
                className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                title="Text to Speech"
              >
                <Volume2 className="h-5 w-5" />
              </button>
              <button
                onClick={handleSpeechToText}
                disabled={isListening}
                className={`p-2 text-gray-400 hover:text-primary-600 transition-colors ${
                  isListening ? 'animate-pulse' : ''
                }`}
                title="Speech to Text"
              >
                {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </button>
              <div className="flex items-center space-x-2">
                <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600">
                    {user?.user_metadata?.full_name?.charAt(0) || user?.email?.charAt(0)}
                  </span>
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {user?.user_metadata?.full_name || user?.email}
                </span>
              </div>
              <button
                onClick={signOut}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600">
                Welcome back! Here's your learning progress overview.
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">
                {currentTime.toLocaleDateString()}
              </p>
              <p className="text-lg font-medium text-gray-900">
                {currentTime.toLocaleTimeString()}
              </p>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat) => {
              const Icon = stat.icon
              return (
                <div key={stat.name} className="card">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Icon className="h-8 w-8 text-primary-600" />
                    </div>
                    <div className="ml-4 flex-1">
                      <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                      <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                      <p className={`text-sm ${stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
                        {stat.change}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Performance Chart */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Performance Trend</h3>
                <button
                  onClick={() => handleTextToSpeech('Your performance has been improving over the past 6 weeks')}
                  className="p-1 text-gray-400 hover:text-primary-600"
                >
                  <Volume2 className="h-4 w-4" />
                </button>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="score" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Subject Performance */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Subject Performance</h3>
                <button
                  onClick={() => handleTextToSpeech('Mathematics is your strongest subject at 85 percent')}
                  className="p-1 text-gray-400 hover:text-primary-600"
                >
                  <Volume2 className="h-4 w-4" />
                </button>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={subjectData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {subjectData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
                <Play className="h-5 w-5 text-primary-600" />
              </div>
              <div className="space-y-3">
                <button
                  onClick={() => router.push('/quiz')}
                  className="w-full flex items-center p-3 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
                >
                  <BookOpen className="h-5 w-5 text-primary-600 mr-3" />
                  <span className="font-medium text-primary-900">Take a Quiz</span>
                </button>
                <button
                  onClick={() => router.push('/progress')}
                  className="w-full flex items-center p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                >
                  <BarChart3 className="h-5 w-5 text-green-600 mr-3" />
                  <span className="font-medium text-green-900">View Progress</span>
                </button>
                <button
                  onClick={() => handleTextToSpeech('You can use voice commands to navigate the platform')}
                  className="w-full flex items-center p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
                >
                  <Brain className="h-5 w-5 text-purple-600 mr-3" />
                  <span className="font-medium text-purple-900">AI Learning Path</span>
                </button>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
                <Clock className="h-5 w-5 text-gray-400" />
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0 w-2 h-2 rounded-full bg-green-500" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      Algebra Quiz
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date().toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <span className="badge badge-success">85%</span>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0 w-2 h-2 rounded-full bg-yellow-500" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      Biology Chapter
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(Date.now() - 86400000).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <span className="badge badge-warning">In Progress</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">AI Recommendations</h3>
                <Award className="h-5 w-5 text-primary-600" />
              </div>
              <div className="space-y-3">
                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    1
                  </div>
                  <p className="text-sm text-gray-700">Focus on practicing algebraic equations</p>
                </div>
                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    2
                  </div>
                  <p className="text-sm text-gray-700">Review photosynthesis concepts</p>
                </div>
                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    3
                  </div>
                  <p className="text-sm text-gray-700">Take more practice quizzes</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
