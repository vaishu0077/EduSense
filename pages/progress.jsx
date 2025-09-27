import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { 
  BarChart3, 
  TrendingUp, 
  BookOpen, 
  Clock, 
  Target,
  Award,
  AlertTriangle,
  CheckCircle,
  Volume2,
  GraduationCap
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts'
import { textToSpeech } from '../utils/accessibility'
import toast from 'react-hot-toast'

export default function Progress() {
  const { user } = useAuth()
  const router = useRouter()
  const [progressData, setProgressData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      router.push('/auth')
      return
    }
    loadProgressData()
  }, [user, router])

  const loadProgressData = async () => {
    try {
      const response = await fetch('/api/performance')
      const data = await response.json()
      setProgressData(data)
    } catch (error) {
      console.error('Error loading progress data:', error)
      toast.error('Failed to load progress data')
    } finally {
      setLoading(false)
    }
  }

  const handleTextToSpeech = (text) => {
    textToSpeech(text)
  }

  if (!user) {
    return null
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your progress...</p>
        </div>
      </div>
    )
  }

  // Sample data for charts
  const performanceOverTime = [
    { name: 'Week 1', score: 65, time: 120 },
    { name: 'Week 2', score: 72, time: 150 },
    { name: 'Week 3', score: 68, time: 140 },
    { name: 'Week 4', score: 78, time: 180 },
    { name: 'Week 5', score: 82, time: 200 },
    { name: 'Week 6', score: 85, time: 220 },
  ]

  const subjectPerformance = [
    { subject: 'Mathematics', score: 85, attempts: 12 },
    { subject: 'Science', score: 72, attempts: 8 },
    { subject: 'English', score: 78, attempts: 10 },
    { subject: 'History', score: 65, attempts: 6 },
  ]

  const topicMastery = [
    { name: 'Algebra', value: 85, color: '#3b82f6' },
    { name: 'Geometry', value: 72, color: '#10b981' },
    { name: 'Biology', value: 78, color: '#f59e0b' },
    { name: 'Chemistry', value: 65, color: '#ef4444' },
  ]

  const weeklyActivity = [
    { day: 'Mon', quizzes: 2, time: 45 },
    { day: 'Tue', quizzes: 1, time: 30 },
    { day: 'Wed', quizzes: 3, time: 60 },
    { day: 'Thu', quizzes: 2, time: 40 },
    { day: 'Fri', quizzes: 1, time: 25 },
    { day: 'Sat', quizzes: 4, time: 80 },
    { day: 'Sun', quizzes: 2, time: 35 },
  ]

  const stats = [
    {
      name: 'Overall Performance',
      value: `${progressData?.overall_score || 75}%`,
      change: '+5%',
      changeType: 'positive',
      icon: TrendingUp,
    },
    {
      name: 'Quizzes Completed',
      value: progressData?.quizzes_completed || 24,
      change: '+3 this week',
      changeType: 'positive',
      icon: BookOpen,
    },
    {
      name: 'Study Time',
      value: `${Math.round((progressData?.total_time || 3600) / 3600)}h`,
      change: '+2h this week',
      changeType: 'positive',
      icon: Clock,
    },
    {
      name: 'Topics Mastered',
      value: progressData?.topics_mastered || 8,
      change: '+1 this week',
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
                onClick={() => handleTextToSpeech('Your learning progress is looking great')}
                className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                title="Text to Speech"
              >
                <Volume2 className="h-5 w-5" />
              </button>
              <button
                onClick={() => router.push('/')}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Learning Progress</h1>
            <p className="text-gray-600">
              Track your learning journey with detailed analytics and insights
            </p>
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

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Performance Over Time */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Performance Over Time</h3>
                <button
                  onClick={() => handleTextToSpeech('Your performance has been steadily improving over the past 6 weeks')}
                  className="p-1 text-gray-400 hover:text-primary-600"
                >
                  <Volume2 className="h-4 w-4" />
                </button>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceOverTime}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Area 
                      type="monotone" 
                      dataKey="score" 
                      stroke="#3b82f6" 
                      fill="#3b82f6"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Subject Performance */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Subject Performance</h3>
                <button
                  onClick={() => handleTextToSpeech('Mathematics is your strongest subject')}
                  className="p-1 text-gray-400 hover:text-primary-600"
                >
                  <Volume2 className="h-4 w-4" />
                </button>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={subjectPerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="subject" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="score" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Topic Mastery */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Topic Mastery</h3>
                <button
                  onClick={() => handleTextToSpeech('You have mastered 4 different topics')}
                  className="p-1 text-gray-400 hover:text-primary-600"
                >
                  <Volume2 className="h-4 w-4" />
                </button>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={topicMastery}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {topicMastery.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Weekly Activity */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Weekly Activity</h3>
                <button
                  onClick={() => handleTextToSpeech('You are most active on Wednesdays and Saturdays')}
                  className="p-1 text-gray-400 hover:text-primary-600"
                >
                  <Volume2 className="h-4 w-4" />
                </button>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklyActivity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="quizzes" fill="#10b981" />
                    <Bar dataKey="time" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Detailed Analytics */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Strengths */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Strengths</h3>
                <CheckCircle className="h-5 w-5 text-green-500" />
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Algebra</p>
                    <p className="text-sm text-gray-600">Consistent high scores</p>
                  </div>
                  <span className="badge badge-success">85%</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Biology</p>
                    <p className="text-sm text-gray-600">Strong understanding</p>
                  </div>
                  <span className="badge badge-success">78%</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">English</p>
                    <p className="text-sm text-gray-600">Good progress</p>
                  </div>
                  <span className="badge badge-success">78%</span>
                </div>
              </div>
            </div>

            {/* Areas for Improvement */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Areas to Improve</h3>
                <AlertTriangle className="h-5 w-5 text-warning-500" />
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-warning-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">History</p>
                    <p className="text-sm text-gray-600">Need more practice</p>
                  </div>
                  <span className="badge badge-warning">65%</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-warning-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Chemistry</p>
                    <p className="text-sm text-gray-600">Focus on basics</p>
                  </div>
                  <span className="badge badge-warning">65%</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-warning-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Geometry</p>
                    <p className="text-sm text-gray-600">Review concepts</p>
                  </div>
                  <span className="badge badge-warning">72%</span>
                </div>
              </div>
            </div>

            {/* Achievements */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Recent Achievements</h3>
                <Award className="h-5 w-5 text-primary-600" />
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center">
                    🏆
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Quiz Master</p>
                    <p className="text-sm text-gray-600">Completed 20+ quizzes</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center">
                    📚
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Study Streak</p>
                    <p className="text-sm text-gray-600">7 days in a row</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center">
                    🎯
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Goal Achiever</p>
                    <p className="text-sm text-gray-600">Met weekly target</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
