import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { 
  BookOpen, 
  Brain, 
  TrendingUp, 
  Users, 
  Award, 
  Clock, 
  ChevronRight,
  Play,
  BarChart3,
  Target,
  Zap
} from 'lucide-react'

export default function Dashboard() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [stats, setStats] = useState({
    completedQuizzes: 0,
    averageScore: 0,
    studyStreak: 0,
    totalStudyTime: 0
  })

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth')
    }
  }, [user, loading, router])

  useEffect(() => {
    if (user) {
      fetchUserStats()
    }
  }, [user])

  const fetchUserStats = async () => {
    try {
      const response = await fetch('/api/performance', {
        headers: {
          'Authorization': `Bearer ${user.session?.access_token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setStats(data.stats || stats)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const quickActions = [
    {
      title: 'Create a Quiz',
      description: 'Generate quizzes with AI or create manually',
      icon: Brain,
      color: 'bg-blue-500',
      href: '/create-quiz'
    },
    {
      title: 'View Progress',
      description: 'Track your learning journey and achievements',
      icon: TrendingUp,
      color: 'bg-green-500',
      href: '/progress'
    },
    {
      title: 'Study Materials',
      description: 'Access personalized learning content',
      icon: BookOpen,
      color: 'bg-purple-500',
      href: '/materials'
    }
  ]

  const recentTopics = analytics?.recent_topics || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex items-center">
                <Brain className="h-8 w-8 text-indigo-600" />
                <span className="ml-2 text-2xl font-bold text-gray-900">EduSense</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Welcome back, {user.user_metadata?.full_name || user.email}
              </div>
              <button
                onClick={() => router.push('/auth')}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                Profile
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}!
          </h1>
          <p className="text-gray-600">Ready to continue your learning journey?</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed Quizzes</p>
                <p className="text-3xl font-bold text-gray-900">{stats.completedQuizzes}</p>
              </div>
              <Award className="h-12 w-12 text-yellow-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Average Score</p>
                <p className="text-3xl font-bold text-gray-900">{stats.averageScore}%</p>
              </div>
              <Target className="h-12 w-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Study Streak</p>
                <p className="text-3xl font-bold text-gray-900">{stats.studyStreak} days</p>
              </div>
              <Zap className="h-12 w-12 text-orange-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Study Time</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalStudyTime}h</p>
              </div>
              <Clock className="h-12 w-12 text-blue-500" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {quickActions.map((action, index) => {
                const IconComponent = action.icon
                return (
                  <button
                    key={index}
                    onClick={() => router.push(action.href)}
                    className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow group"
                  >
                    <div className={`${action.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                      <IconComponent className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2">{action.title}</h3>
                    <p className="text-sm text-gray-600 mb-4">{action.description}</p>
                    <div className="flex items-center text-indigo-600 text-sm font-medium">
                      Get started
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Recent Topics */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Topics</h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-6">
                <div className="space-y-4">
                  {recentTopics.map((topic, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-medium text-gray-900">{topic.name}</h4>
                          <span className="text-sm text-gray-500">{topic.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                          <div 
                            className="bg-indigo-600 h-2 rounded-full" 
                            style={{ width: `${topic.progress}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-500">{topic.lastStudied}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 rounded-b-lg">
                <button 
                  onClick={() => router.push('/progress')}
                  className="text-indigo-600 text-sm font-medium hover:text-indigo-500"
                >
                  View all topics →
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="mt-8">
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold mb-2">🧠 AI Recommendation</h2>
                <p className="text-indigo-100 mb-4">
                  Based on your recent performance, we recommend focusing on advanced calculus problems.
                </p>
                <button 
                  onClick={() => router.push('/quiz?topic=calculus&difficulty=hard')}
                  className="bg-white text-indigo-600 px-4 py-2 rounded-md font-medium hover:bg-gray-100 transition-colors"
                >
                  Start Practice Session
                </button>
              </div>
              <div className="hidden md:block">
                <Brain className="h-16 w-16 text-indigo-200" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
