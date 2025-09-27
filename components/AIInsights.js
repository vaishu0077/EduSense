import React, { useState, useEffect } from 'react'
import { 
  Brain, 
  TrendingUp, 
  Target, 
  AlertTriangle, 
  Lightbulb, 
  BarChart3,
  Clock,
  CheckCircle,
  ArrowRight,
  RefreshCw
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const AIInsights = () => {
  const { user } = useAuth()
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (user) {
      loadAIInsights()
    }
  }, [user])

  const loadAIInsights = async () => {
    try {
      setLoading(true)
      
      // Load multiple AI insights in parallel
      const [predictions, weaknesses, recommendations] = await Promise.all([
        fetch(`/api/ai-services?service=performance-prediction&user_id=${user.id}&type=overall`).then(r => r.json()),
        fetch(`/api/ai-services?service=weakness-detection&user_id=${user.id}&type=comprehensive`).then(r => r.json()),
        fetch(`/api/ai-services?service=content-recommendation&user_id=${user.id}&limit=3`).then(r => r.json())
      ])

      setInsights({
        predictions: predictions.predictions || {},
        weaknesses: weaknesses.analysis || {},
        recommendations: recommendations.recommendations || []
      })
    } catch (error) {
      console.error('Error loading AI insights:', error)
      // Set demo data on error
      setInsights(getDemoInsights())
    } finally {
      setLoading(false)
    }
  }

  const getDemoInsights = () => ({
    predictions: {
      overall_predictions: {
        expected_score_improvement: 12,
        confidence_level: 0.85,
        key_factors: ["Consistent practice", "Difficulty progression"],
        success_probability: 0.8
      },
      performance_trends: {
        short_term: "improving",
        medium_term: "improving",
        long_term: "improving"
      }
    },
    weaknesses: {
      overall_weaknesses: {
        primary_weaknesses: [
          {
            weakness: "Mathematics problem-solving",
            severity: "medium",
            impact: "Affects overall mathematics performance",
            frequency: "frequent"
          }
        ]
      },
      recommendations: [
        {
          priority: "high",
          recommendation: "Practice mathematics problem-solving daily",
          expected_impact: "high",
          timeline: "1-2 weeks"
        }
      ]
    },
    recommendations: [
      {
        content_id: "demo_1",
        title: "Calculus Practice Problems",
        type: "quiz",
        subject: "mathematics",
        difficulty: "medium",
        estimated_time: "20 minutes",
        relevance_score: 0.9,
        why_recommended: "Based on your performance in mathematics"
      }
    ]
  })

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="h-4 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!insights) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
        <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">AI Insights Unavailable</h3>
        <p className="text-gray-500 mb-4">Unable to load AI insights at this time.</p>
        <button
          onClick={loadAIInsights}
          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors mx-auto"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Brain className="h-6 w-6 text-indigo-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">AI Insights</h2>
          </div>
          <button
            onClick={loadAIInsights}
            className="flex items-center px-3 py-1 text-sm text-indigo-600 hover:text-indigo-500 transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </button>
        </div>
        
        {/* Tabs */}
        <div className="flex space-x-6 mt-4">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'predictions', label: 'Predictions', icon: TrendingUp },
            { id: 'weaknesses', label: 'Weaknesses', icon: AlertTriangle },
            { id: 'recommendations', label: 'Recommendations', icon: Lightbulb }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
            >
              <tab.icon className="h-4 w-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && <OverviewTab insights={insights} />}
        {activeTab === 'predictions' && <PredictionsTab insights={insights} />}
        {activeTab === 'weaknesses' && <WeaknessesTab insights={insights} />}
        {activeTab === 'recommendations' && <RecommendationsTab insights={insights} />}
      </div>
    </div>
  )
}

const OverviewTab = ({ insights }) => {
  const predictions = insights.predictions?.overall_predictions || {}
  const weaknesses = insights.weaknesses?.overall_weaknesses?.primary_weaknesses || []
  const recommendations = insights.recommendations || []

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">Expected Improvement</p>
              <p className="text-2xl font-bold text-green-900">
                +{predictions.expected_score_improvement || 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-blue-800">Success Probability</p>
              <p className="text-2xl font-bold text-blue-900">
                {Math.round((predictions.success_probability || 0) * 100)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center">
            <Lightbulb className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-purple-800">Recommendations</p>
              <p className="text-2xl font-bold text-purple-900">
                {recommendations.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Trend */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-3">Performance Trend</h3>
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Short-term: Improving</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Medium-term: Improving</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="text-sm text-gray-600">Long-term: Improving</span>
          </div>
        </div>
      </div>

      {/* Key Factors */}
      {predictions.key_factors && predictions.key_factors.length > 0 && (
        <div className="bg-indigo-50 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Key Success Factors</h3>
          <div className="flex flex-wrap gap-2">
            {predictions.key_factors.map((factor, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-indigo-100 text-indigo-800 text-sm rounded-full"
              >
                {factor}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

const PredictionsTab = ({ insights }) => {
  const predictions = insights.predictions || {}

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Predictions</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Expected Improvement</h4>
            <div className="text-3xl font-bold text-blue-600 mb-2">
              +{predictions.overall_predictions?.expected_score_improvement || 0}%
            </div>
            <p className="text-sm text-gray-600">
              Confidence: {Math.round((predictions.overall_predictions?.confidence_level || 0) * 100)}%
            </p>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Success Probability</h4>
            <div className="text-3xl font-bold text-green-600 mb-2">
              {Math.round((predictions.overall_predictions?.success_probability || 0) * 100)}%
            </div>
            <p className="text-sm text-gray-600">Based on current performance</p>
          </div>
        </div>
      </div>

      {/* Subject Predictions */}
      {predictions.subject_predictions && predictions.subject_predictions.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Subject Predictions</h3>
          <div className="space-y-4">
            {predictions.subject_predictions.map((subject, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900 capitalize">{subject.subject}</h4>
                  <p className="text-sm text-gray-600">
                    {subject.current_level} → {subject.predicted_level}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-gray-900">
                    {subject.predicted_score_range}
                  </div>
                  <p className="text-sm text-gray-600">
                    {subject.improvement_timeline}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

const WeaknessesTab = ({ insights }) => {
  const weaknesses = insights.weaknesses || {}
  const primaryWeaknesses = weaknesses.overall_weaknesses?.primary_weaknesses || []
  const recommendations = weaknesses.recommendations || []

  return (
    <div className="space-y-6">
      {/* Primary Weaknesses */}
      {primaryWeaknesses.length > 0 && (
        <div className="bg-red-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Primary Weaknesses</h3>
          <div className="space-y-4">
            {primaryWeaknesses.map((weakness, index) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-red-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">{weakness.weakness}</h4>
                    <p className="text-sm text-gray-600 mb-2">{weakness.impact}</p>
                    <div className="flex items-center space-x-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        weakness.severity === 'high' ? 'bg-red-100 text-red-800' :
                        weakness.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {weakness.severity} severity
                      </span>
                      <span className="text-xs text-gray-500">
                        {weakness.frequency} occurrence
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Improvement Recommendations</h3>
          <div className="space-y-4">
            {recommendations.map((rec, index) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-blue-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full mr-2 ${
                        rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                        rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {rec.priority} priority
                      </span>
                      <span className="text-xs text-gray-500">
                        {rec.timeline}
                      </span>
                    </div>
                    <h4 className="font-medium text-gray-900 mb-1">{rec.recommendation}</h4>
                    <p className="text-sm text-gray-600">
                      Expected impact: {rec.expected_impact}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {primaryWeaknesses.length === 0 && recommendations.length === 0 && (
        <div className="text-center py-8">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Major Weaknesses Detected</h3>
          <p className="text-gray-600">Keep up the great work! Continue with your current learning approach.</p>
        </div>
      )}
    </div>
  )
}

const RecommendationsTab = ({ insights }) => {
  const recommendations = insights.recommendations || []

  return (
    <div className="space-y-6">
      {recommendations.length > 0 ? (
        <div className="space-y-4">
          {recommendations.map((rec, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <span className="px-2 py-1 text-xs font-medium bg-indigo-100 text-indigo-800 rounded-full mr-2">
                      {rec.type}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full mr-2">
                      {rec.difficulty}
                    </span>
                    <span className="text-xs text-gray-500">
                      {rec.estimated_time}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{rec.title}</h3>
                  <p className="text-gray-600 mb-3">{rec.why_recommended}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-sm text-gray-500">
                      <Clock className="h-4 w-4 mr-1" />
                      {rec.estimated_time}
                    </div>
                    <div className="flex items-center">
                      <span className="text-sm text-gray-500 mr-2">
                        Relevance: {Math.round((rec.relevance_score || 0) * 100)}%
                      </span>
                      <button className="flex items-center px-3 py-1 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 transition-colors">
                        Start
                        <ArrowRight className="h-4 w-4 ml-1" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Recommendations Available</h3>
          <p className="text-gray-600">Complete some quizzes to get personalized recommendations.</p>
        </div>
      )}
    </div>
  )
}

export default AIInsights
