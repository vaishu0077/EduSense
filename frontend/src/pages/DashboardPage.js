import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
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
  BarChart3
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { api } from '../services/api';

export const DashboardPage = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const { data: dashboardData, isLoading, error } = useQuery(
    'dashboard',
    () => api.get('/analytics/dashboard'),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-8 h-8"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading dashboard</h3>
        <p className="text-gray-500">Please try refreshing the page</p>
      </div>
    );
  }

  const data = dashboardData?.data || {};

  // Sample data for charts (replace with real data)
  const performanceData = [
    { name: 'Week 1', score: 65 },
    { name: 'Week 2', score: 72 },
    { name: 'Week 3', score: 68 },
    { name: 'Week 4', score: 78 },
    { name: 'Week 5', score: 82 },
    { name: 'Week 6', score: 85 },
  ];

  const subjectData = [
    { name: 'Mathematics', value: 85, color: '#3b82f6' },
    { name: 'Science', value: 72, color: '#10b981' },
    { name: 'English', value: 78, color: '#f59e0b' },
    { name: 'History', value: 65, color: '#ef4444' },
  ];

  const stats = [
    {
      name: 'Overall Performance',
      value: `${Math.round(data.user_performance?.average_score || 0)}%`,
      change: '+5%',
      changeType: 'positive',
      icon: TrendingUp,
    },
    {
      name: 'Topics Studied',
      value: data.user_performance?.total_topics_studied || 0,
      change: '+2 this week',
      changeType: 'positive',
      icon: BookOpen,
    },
    {
      name: 'Study Time',
      value: `${Math.round((data.user_performance?.total_time_spent || 0) / 3600)}h`,
      change: '+1.5h today',
      changeType: 'positive',
      icon: Clock,
    },
    {
      name: 'Learning Paths',
      value: data.learning_progress?.active_paths || 0,
      change: '1 completed',
      changeType: 'positive',
      icon: Target,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
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
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Performance Trend</h3>
            <Link to="/analytics" className="text-primary-600 hover:text-primary-500 text-sm font-medium">
              View details
            </Link>
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
            <Link to="/topics" className="text-primary-600 hover:text-primary-500 text-sm font-medium">
              View all topics
            </Link>
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weaknesses */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Areas to Improve</h3>
            <AlertTriangle className="h-5 w-5 text-warning-500" />
          </div>
          <div className="space-y-3">
            {data.weaknesses?.slice(0, 3).map((weakness) => (
              <div key={weakness.id} className="flex items-center justify-between p-3 bg-warning-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">Topic {weakness.topic_id}</p>
                  <p className="text-sm text-gray-600">{weakness.description}</p>
                </div>
                <span className={`badge badge-warning`}>
                  {weakness.severity}
                </span>
              </div>
            )) || (
              <div className="text-center py-4">
                <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No weaknesses identified!</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
            <Clock className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-3">
            {data.recent_activities?.slice(0, 4).map((activity) => (
              <div key={activity.id} className="flex items-center space-x-3">
                <div className={`flex-shrink-0 w-2 h-2 rounded-full ${
                  activity.status === 'passed' ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {activity.title}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(activity.timestamp).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex-shrink-0">
                  <span className={`badge ${
                    activity.status === 'passed' ? 'badge-success' : 'badge-error'
                  }`}>
                    {activity.score}%
                  </span>
                </div>
              </div>
            )) || (
              <div className="text-center py-4">
                <BookOpen className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No recent activity</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
            <Play className="h-5 w-5 text-primary-600" />
          </div>
          <div className="space-y-3">
            <Link
              to="/topics"
              className="flex items-center p-3 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
            >
              <BookOpen className="h-5 w-5 text-primary-600 mr-3" />
              <span className="font-medium text-primary-900">Browse Topics</span>
            </Link>
            <Link
              to="/learning-path"
              className="flex items-center p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
            >
              <Brain className="h-5 w-5 text-green-600 mr-3" />
              <span className="font-medium text-green-900">Start Learning Path</span>
            </Link>
            <Link
              to="/analytics"
              className="flex items-center p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
            >
              <BarChart3 className="h-5 w-5 text-purple-600 mr-3" />
              <span className="font-medium text-purple-900">View Analytics</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">AI Recommendations</h3>
            <Award className="h-5 w-5 text-primary-600" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.recommendations.slice(0, 4).map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <div className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  {index + 1}
                </div>
                <p className="text-sm text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
