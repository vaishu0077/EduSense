import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  Target, 
  Clock, 
  Award, 
  Zap,
  CheckCircle,
  AlertCircle,
  Activity
} from 'lucide-react'
import { useRealtime } from '../contexts/RealtimeContext'
import { useAuth } from '../contexts/AuthContext'

const RealtimeProgress = () => {
  const { user } = useAuth()
  const { liveAnalytics, isConnected } = useRealtime()
  const [progressData, setProgressData] = useState({
    currentStreak: 0,
    weeklyGoal: 5,
    completedToday: 0,
    totalTimeSpent: 0,
    improvementRate: 0,
    nextMilestone: '',
    achievements: []
  })
  const [recentActivity, setRecentActivity] = useState([])

  useEffect(() => {
    loadProgressData()
    loadRecentActivity()
  }, [user])

  const loadProgressData = async () => {
    if (!user) return
    
    try {
      // Simulate real-time progress data
      const mockProgress = {
        currentStreak: Math.floor(Math.random() * 30) + 1,
        weeklyGoal: 5,
        completedToday: Math.floor(Math.random() * 3),
        totalTimeSpent: Math.floor(Math.random() * 120) + 30,
        improvementRate: Math.floor(Math.random() * 20) + 5,
        nextMilestone: 'Complete 10 quizzes this week',
        achievements: [
          { name: 'First Quiz', earned: true, date: '2024-01-15' },
          { name: 'Streak Master', earned: true, date: '2024-01-20' },
          { name: 'Perfect Score', earned: false, date: null }
        ]
      }
      
      setProgressData(mockProgress)
    } catch (error) {
      console.error('Error loading progress data:', error)
    }
  }

  const loadRecentActivity = async () => {
    if (!user) return
    
    try {
      // Simulate recent activity data
      const mockActivity = [
        {
          id: 1,
          type: 'quiz_completed',
          title: 'Mathematics Quiz',
          score: 85,
          time: '2 minutes ago',
          icon: '📊'
        },
        {
          id: 2,
          type: 'streak_achieved',
          title: '7 Day Streak!',
          score: null,
          time: '1 hour ago',
          icon: '🔥'
        },
        {
          id: 3,
          type: 'milestone_reached',
          title: '100 Quizzes Completed',
          score: null,
          time: '3 hours ago',
          icon: '🎯'
        }
      ]
      
      setRecentActivity(mockActivity)
    } catch (error) {
      console.error('Error loading recent activity:', error)
    }
  }

  const getStreakColor = (streak) => {
    if (streak >= 30) return 'text-purple-600'
    if (streak >= 14) return 'text-blue-600'
    if (streak >= 7) return 'text-green-600'
    return 'text-orange-600'
  }

  const getStreakLabel = (streak) => {
    if (streak >= 30) return 'Fire Master!'
    if (streak >= 14) return 'On Fire!'
    if (streak >= 7) return 'Great Streak!'
    return 'Keep Going!'
  }

  const getProgressPercentage = () => {
    return Math.min((progressData.completedToday / progressData.weeklyGoal) * 100, 100)
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-green-100 rounded-lg">
            <TrendingUp className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Live Progress</h2>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Syncing live updates' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Current Streak */}
        <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-800">Current Streak</p>
              <p className={`text-2xl font-bold ${getStreakColor(progressData.currentStreak)}`}>
                {progressData.currentStreak} days
              </p>
            </div>
            <Zap className="h-8 w-8 text-orange-600" />
          </div>
          <div className="mt-2">
            <span className="text-sm font-medium text-orange-700">
              {getStreakLabel(progressData.currentStreak)}
            </span>
          </div>
        </div>

        {/* Weekly Progress */}
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-800">Weekly Goal</p>
              <p className="text-2xl font-bold text-blue-900">
                {progressData.completedToday}/{progressData.weeklyGoal}
              </p>
            </div>
            <Target className="h-8 w-8 text-blue-600" />
          </div>
          <div className="mt-2">
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getProgressPercentage()}%` }}
              ></div>
            </div>
            <p className="text-xs text-blue-700 mt-1">
              {Math.round(getProgressPercentage())}% complete
            </p>
          </div>
        </div>

        {/* Time Spent */}
        <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-800">Time Today</p>
              <p className="text-2xl font-bold text-purple-900">
                {progressData.totalTimeSpent}m
              </p>
            </div>
            <Clock className="h-8 w-8 text-purple-600" />
          </div>
          <div className="mt-2">
            <span className="text-sm text-purple-700">
              {progressData.totalTimeSpent >= 60 ? 
                `${Math.floor(progressData.totalTimeSpent / 60)}h ${progressData.totalTimeSpent % 60}m` : 
                `${progressData.totalTimeSpent} minutes`
              }
            </span>
          </div>
        </div>

        {/* Improvement Rate */}
        <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-800">Improvement</p>
              <p className="text-2xl font-bold text-green-900">
                +{progressData.improvementRate}%
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
          <div className="mt-2">
            <span className="text-sm text-green-700">
              This week
            </span>
          </div>
        </div>
      </div>

      {/* Live Analytics Update */}
      {liveAnalytics && (
        <div className="bg-indigo-50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-indigo-600" />
            Latest Activity
          </h3>
          <div className="bg-white rounded-lg p-3 border border-indigo-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                  <Target className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">
                    {liveAnalytics.latestTopic} Quiz Completed
                  </p>
                  <p className="text-sm text-gray-600">
                    Scored {liveAnalytics.latestScore}%
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Just now</p>
                <div className="flex items-center text-green-600">
                  <CheckCircle className="h-4 w-4 mr-1" />
                  <span className="text-sm font-medium">Live</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl">{activity.icon}</div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">{activity.title}</p>
                {activity.score && (
                  <p className="text-sm text-gray-600">Score: {activity.score}%</p>
                )}
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">{activity.time}</p>
                <div className="flex items-center text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  <span className="text-xs">Live</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Next Milestone */}
      <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <Award className="h-6 w-6 text-yellow-600" />
          <div>
            <h4 className="font-semibold text-yellow-800">Next Milestone</h4>
            <p className="text-yellow-700">{progressData.nextMilestone}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RealtimeProgress
