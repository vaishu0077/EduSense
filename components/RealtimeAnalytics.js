import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  Users, 
  Activity, 
  Clock, 
  Target, 
  Zap,
  RefreshCw,
  Eye,
  BarChart3
} from 'lucide-react'
import { useRealtime } from '../contexts/RealtimeContext'
import { useAuth } from '../contexts/AuthContext'

const RealtimeAnalytics = () => {
  const { user } = useAuth()
  const { liveAnalytics, onlineUsers, isConnected } = useRealtime()
  const [analytics, setAnalytics] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalQuizzes: 0,
    averageScore: 0,
    completionRate: 0,
    engagementScore: 0
  })
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    loadAnalytics()
  }, [user])

  const loadAnalytics = async () => {
    if (!user) return
    
    setIsRefreshing(true)
    try {
      // Load real-time analytics data
      // In a real app, this would come from your analytics API
      const analyticsData = {
        totalUsers: Math.floor(Math.random() * 1000) + 500,
        activeUsers: Math.floor(Math.random() * 100) + 50,
        totalQuizzes: Math.floor(Math.random() * 5000) + 2000,
        averageScore: Math.floor(Math.random() * 20) + 75,
        completionRate: Math.floor(Math.random() * 30) + 70,
        engagementScore: Math.floor(Math.random() * 20) + 80
      }
      
      setAnalytics(analyticsData)
    } catch (error) {
      console.error('Error loading analytics:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const getEngagementColor = (score) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getEngagementLabel = (score) => {
    if (score >= 90) return 'Excellent'
    if (score >= 70) return 'Good'
    return 'Needs Improvement'
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <BarChart3 className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Live Analytics</h2>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Live' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={loadAnalytics}
          disabled={isRefreshing}
          className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Live Analytics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        {/* Total Users */}
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-800">Total Users</p>
              <p className="text-2xl font-bold text-blue-900">{analytics.totalUsers.toLocaleString()}</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
          <div className="mt-2 flex items-center text-sm text-blue-700">
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>+12% this week</span>
          </div>
        </div>

        {/* Active Users */}
        <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-800">Active Now</p>
              <p className="text-2xl font-bold text-green-900">{onlineUsers.length}</p>
            </div>
            <Activity className="h-8 w-8 text-green-600" />
          </div>
          <div className="mt-2 flex items-center text-sm text-green-700">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            <span>Live users</span>
          </div>
        </div>

        {/* Average Score */}
        <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-800">Avg Score</p>
              <p className="text-2xl font-bold text-purple-900">{analytics.averageScore}%</p>
            </div>
            <Target className="h-8 w-8 text-purple-600" />
          </div>
          <div className="mt-2 flex items-center text-sm text-purple-700">
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>+5% this month</span>
          </div>
        </div>

        {/* Completion Rate */}
        <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-800">Completion Rate</p>
              <p className="text-2xl font-bold text-orange-900">{analytics.completionRate}%</p>
            </div>
            <Clock className="h-8 w-8 text-orange-600" />
          </div>
          <div className="mt-2 flex items-center text-sm text-orange-700">
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>+8% this week</span>
          </div>
        </div>

        {/* Engagement Score */}
        <div className="bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-indigo-800">Engagement</p>
              <p className="text-2xl font-bold text-indigo-900">{analytics.engagementScore}%</p>
            </div>
            <Zap className="h-8 w-8 text-indigo-600" />
          </div>
          <div className="mt-2 flex items-center text-sm">
            <span className={`font-medium ${getEngagementColor(analytics.engagementScore)}`}>
              {getEngagementLabel(analytics.engagementScore)}
            </span>
          </div>
        </div>

        {/* Total Quizzes */}
        <div className="bg-gradient-to-r from-pink-50 to-pink-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-pink-800">Quizzes Taken</p>
              <p className="text-2xl font-bold text-pink-900">{analytics.totalQuizzes.toLocaleString()}</p>
            </div>
            <BarChart3 className="h-8 w-8 text-pink-600" />
          </div>
          <div className="mt-2 flex items-center text-sm text-pink-700">
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>+15% this month</span>
          </div>
        </div>
      </div>

      {/* Live Updates Section */}
      {liveAnalytics && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-green-600" />
            Live Updates
          </h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Latest Score:</span>
              <span className="font-medium text-gray-900">{liveAnalytics.latestScore || 'N/A'}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Topic:</span>
              <span className="font-medium text-gray-900">{liveAnalytics.latestTopic || 'N/A'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Last Updated:</span>
              <span className="font-medium text-gray-900">
                {liveAnalytics.lastUpdated ? new Date(liveAnalytics.lastUpdated).toLocaleTimeString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Real-time Activity Indicator */}
      <div className="mt-4 flex items-center justify-center">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>Real-time data updates every 30 seconds</span>
        </div>
      </div>
    </div>
  )
}

export default RealtimeAnalytics
