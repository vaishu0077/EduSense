import { useState, useEffect } from 'react'
import { 
  Brain, 
  BookOpen, 
  Target, 
  Lightbulb, 
  TrendingUp, 
  Clock, 
  FileText,
  ChevronDown,
  ChevronRight,
  Play,
  Star,
  Tag
} from 'lucide-react'

export default function MaterialAnalysis({ material, onGenerateQuiz }) {
  const [expandedSections, setExpandedSections] = useState({
    summary: true,
    topics: false,
    objectives: false,
    concepts: false,
    questions: false,
    recommendations: false
  })

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const getDifficultyColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'beginner':
        return 'bg-green-100 text-green-800'
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800'
      case 'advanced':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getSubjectColor = (subject) => {
    const colors = {
      'mathematics': 'bg-blue-100 text-blue-800',
      'science': 'bg-green-100 text-green-800',
      'history': 'bg-purple-100 text-purple-800',
      'english': 'bg-pink-100 text-pink-800',
      'physics': 'bg-indigo-100 text-indigo-800',
      'chemistry': 'bg-orange-100 text-orange-800',
      'biology': 'bg-emerald-100 text-emerald-800'
    }
    return colors[subject?.toLowerCase()] || 'bg-gray-100 text-gray-800'
  }

  if (!material?.ai_analysis) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <Brain className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p>No analysis available for this material</p>
        </div>
      </div>
    )
  }

  const analysis = material.ai_analysis

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              AI Analysis
            </h3>
            <p className="text-gray-600 mb-4">
              Intelligent insights generated from your study material
            </p>
            
            <div className="flex flex-wrap gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(analysis.difficulty_level)}`}>
                {analysis.difficulty_level || 'Intermediate'}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSubjectColor(analysis.subject_category)}`}>
                {analysis.subject_category || 'General'}
              </span>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {material.word_count || 0} words
              </span>
            </div>
          </div>
          
          <button
            onClick={() => onGenerateQuiz(material)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          >
            <Play className="h-4 w-4 mr-2" />
            Generate Quiz
          </button>
        </div>
      </div>

      {/* Summary Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('summary')}
          className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center">
            <FileText className="h-5 w-5 text-indigo-600 mr-3" />
            <h4 className="text-lg font-medium text-gray-900">Summary</h4>
          </div>
          {expandedSections.summary ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        
        {expandedSections.summary && (
          <div className="px-6 pb-6">
            <p className="text-gray-700 leading-relaxed break-words whitespace-pre-wrap">
              {analysis.summary}
            </p>
          </div>
        )}
      </div>

      {/* Key Topics Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('topics')}
          className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center">
            <BookOpen className="h-5 w-5 text-green-600 mr-3" />
            <h4 className="text-lg font-medium text-gray-900">Key Topics</h4>
            <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-sm">
              {analysis.key_topics?.length || 0}
            </span>
          </div>
          {expandedSections.topics ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        
        {expandedSections.topics && (
          <div className="px-6 pb-6">
            <div className="flex flex-wrap gap-2">
              {analysis.key_topics?.map((topic, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800"
                >
                  <Tag className="h-3 w-3 mr-1" />
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Learning Objectives Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('objectives')}
          className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center">
            <Target className="h-5 w-5 text-blue-600 mr-3" />
            <h4 className="text-lg font-medium text-gray-900">Learning Objectives</h4>
            <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-sm">
              {analysis.learning_objectives?.length || 0}
            </span>
          </div>
          {expandedSections.objectives ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        
        {expandedSections.objectives && (
          <div className="px-6 pb-6">
            <ul className="space-y-2">
              {analysis.learning_objectives?.map((objective, index) => (
                <li key={index} className="flex items-start">
                  <Star className="h-4 w-4 text-blue-500 mr-2 mt-1 flex-shrink-0" />
                  <span className="text-gray-700 break-words whitespace-pre-wrap">{objective}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Key Concepts Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('concepts')}
          className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center">
            <Lightbulb className="h-5 w-5 text-yellow-600 mr-3" />
            <h4 className="text-lg font-medium text-gray-900">Key Concepts</h4>
            <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-sm">
              {analysis.key_concepts?.length || 0}
            </span>
          </div>
          {expandedSections.concepts ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        
        {expandedSections.concepts && (
          <div className="px-6 pb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {analysis.key_concepts?.map((concept, index) => (
                <div key={index} className="flex items-center p-3 bg-yellow-50 rounded-lg">
                  <Lightbulb className="h-4 w-4 text-yellow-600 mr-2 flex-shrink-0" />
                  <span className="text-gray-700">{concept}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Suggested Quiz Questions Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('questions')}
          className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center">
            <Brain className="h-5 w-5 text-purple-600 mr-3" />
            <h4 className="text-lg font-medium text-gray-900">Suggested Quiz Questions</h4>
            <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-sm">
              {analysis.suggested_quiz_questions?.length || 0}
            </span>
          </div>
          {expandedSections.questions ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        
        {expandedSections.questions && (
          <div className="px-6 pb-6">
            <div className="space-y-4">
              {analysis.suggested_quiz_questions?.map((question, index) => (
                <div key={index} className="p-4 bg-purple-50 rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <p className="font-medium text-gray-900">{question.question}</p>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                      question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {question.difficulty}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">Topic: {question.topic}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Study Recommendations Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <button
          onClick={() => toggleSection('recommendations')}
          className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-indigo-600 mr-3" />
            <h4 className="text-lg font-medium text-gray-900">Study Recommendations</h4>
            <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-sm">
              {analysis.study_recommendations?.length || 0}
            </span>
          </div>
          {expandedSections.recommendations ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        
        {expandedSections.recommendations && (
          <div className="px-6 pb-6">
            <ul className="space-y-3">
              {analysis.study_recommendations?.map((recommendation, index) => (
                <li key={index} className="flex items-start">
                  <Clock className="h-4 w-4 text-indigo-500 mr-3 mt-1 flex-shrink-0" />
                  <span className="text-gray-700 break-words whitespace-pre-wrap">{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
