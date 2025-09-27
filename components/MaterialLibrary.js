import { useState, useEffect } from 'react'
import { 
  Search, 
  Filter, 
  Grid, 
  List, 
  SortAsc, 
  SortDesc,
  BookOpen,
  FileText,
  Calendar,
  Tag,
  MoreVertical,
  Edit,
  Trash2,
  Download,
  Eye,
  Star,
  StarOff,
  Folder,
  FolderOpen
} from 'lucide-react'

export default function MaterialLibrary({ materials, onMaterialSelect, onMaterialDelete, onMaterialEdit }) {
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('date') // 'date', 'name', 'subject', 'difficulty'
  const [sortOrder, setSortOrder] = useState('desc') // 'asc' or 'desc'
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({
    subject: '',
    difficulty: '',
    starred: false
  })
  const [selectedMaterials, setSelectedMaterials] = useState([])
  const [showFilters, setShowFilters] = useState(false)

  // Filter and sort materials
  const filteredMaterials = materials
    .filter(material => {
      const matchesSearch = material.filename?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           material.ai_analysis?.summary?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           material.ai_analysis?.key_topics?.some(topic => 
                             topic.toLowerCase().includes(searchQuery.toLowerCase())
                           )
      
      const matchesSubject = !filters.subject || 
                            material.ai_analysis?.subject_category?.toLowerCase() === filters.subject.toLowerCase()
      
      const matchesDifficulty = !filters.difficulty || 
                               material.ai_analysis?.difficulty_level?.toLowerCase() === filters.difficulty.toLowerCase()
      
      const matchesStarred = !filters.starred || material.starred
      
      return matchesSearch && matchesSubject && matchesDifficulty && matchesStarred
    })
    .sort((a, b) => {
      let aValue, bValue
      
      switch (sortBy) {
        case 'name':
          aValue = a.filename || ''
          bValue = b.filename || ''
          break
        case 'subject':
          aValue = a.ai_analysis?.subject_category || ''
          bValue = b.ai_analysis?.subject_category || ''
          break
        case 'difficulty':
          const difficultyOrder = { 'beginner': 1, 'intermediate': 2, 'advanced': 3 }
          aValue = difficultyOrder[a.ai_analysis?.difficulty_level?.toLowerCase()] || 2
          bValue = difficultyOrder[b.ai_analysis?.difficulty_level?.toLowerCase()] || 2
          break
        case 'date':
        default:
          aValue = new Date(a.created_at || 0)
          bValue = new Date(b.created_at || 0)
          break
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

  const handleMaterialClick = (material) => {
    onMaterialSelect(material)
  }

  const handleStarToggle = (materialId, e) => {
    e.stopPropagation()
    // Toggle star status - this would typically update the database
    console.log('Toggle star for material:', materialId)
  }

  const handleMaterialAction = (material, action, e) => {
    e.stopPropagation()
    
    switch (action) {
      case 'edit':
        onMaterialEdit(material)
        break
      case 'delete':
        onMaterialDelete(material)
        break
      case 'download':
        // Implement download functionality
        console.log('Download material:', material.filename)
        break
      case 'view':
        onMaterialSelect(material)
        break
    }
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Study Materials</h2>
          <p className="text-gray-600">
            {filteredMaterials.length} of {materials.length} materials
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-md ${viewMode === 'grid' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <Grid className="h-5 w-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-md ${viewMode === 'list' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <List className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search materials..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Sort */}
          <div className="flex items-center space-x-2">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="date">Date</option>
              <option value="name">Name</option>
              <option value="subject">Subject</option>
              <option value="difficulty">Difficulty</option>
            </select>
            
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="p-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              {sortOrder === 'asc' ? (
                <SortAsc className="h-4 w-4" />
              ) : (
                <SortDesc className="h-4 w-4" />
              )}
            </button>
          </div>

          {/* Filters */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </button>
        </div>

        {/* Filter Options */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <select
                  value={filters.subject}
                  onChange={(e) => setFilters(prev => ({ ...prev, subject: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="">All Subjects</option>
                  <option value="mathematics">Mathematics</option>
                  <option value="science">Science</option>
                  <option value="history">History</option>
                  <option value="english">English</option>
                  <option value="physics">Physics</option>
                  <option value="chemistry">Chemistry</option>
                  <option value="biology">Biology</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
                <select
                  value={filters.difficulty}
                  onChange={(e) => setFilters(prev => ({ ...prev, difficulty: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="">All Levels</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
              
              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.starred}
                    onChange={(e) => setFilters(prev => ({ ...prev, starred: e.target.checked }))}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Starred only</span>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Materials Grid/List */}
      {filteredMaterials.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No materials found</h3>
          <p className="text-gray-500">
            {searchQuery || Object.values(filters).some(f => f) 
              ? 'Try adjusting your search or filters'
              : 'Upload your first study material to get started'
            }
          </p>
        </div>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
          : 'space-y-4'
        }>
          {filteredMaterials.map((material) => (
            <div
              key={material.id}
              onClick={() => handleMaterialClick(material)}
              className={`bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer ${
                viewMode === 'list' ? 'p-4' : 'p-6'
              }`}
            >
              {viewMode === 'grid' ? (
                // Grid View
                <>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center">
                      <FileText className="h-8 w-8 text-indigo-600 mr-3" />
                      <div>
                        <h3 className="font-medium text-gray-900 truncate">
                          {material.filename}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {formatDate(material.created_at)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={(e) => handleStarToggle(material.id, e)}
                        className="p-1 hover:bg-gray-100 rounded"
                      >
                        {material.starred ? (
                          <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        ) : (
                          <StarOff className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                      
                      <div className="relative">
                        <button
                          onClick={(e) => handleMaterialAction(material, 'menu', e)}
                          className="p-1 hover:bg-gray-100 rounded"
                        >
                          <MoreVertical className="h-4 w-4 text-gray-400" />
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {material.ai_analysis?.summary || 'No summary available'}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(material.ai_analysis?.difficulty_level)}`}>
                      {material.ai_analysis?.difficulty_level || 'Intermediate'}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSubjectColor(material.ai_analysis?.subject_category)}`}>
                      {material.ai_analysis?.subject_category || 'General'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{material.word_count || 0} words</span>
                    <span>{formatFileSize(material.file_size)}</span>
                  </div>
                </>
              ) : (
                // List View
                <div className="flex items-center justify-between">
                  <div className="flex items-center flex-1">
                    <FileText className="h-8 w-8 text-indigo-600 mr-4" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium text-gray-900">
                          {material.filename}
                        </h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(material.ai_analysis?.difficulty_level)}`}>
                            {material.ai_analysis?.difficulty_level || 'Intermediate'}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSubjectColor(material.ai_analysis?.subject_category)}`}>
                            {material.ai_analysis?.subject_category || 'General'}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {material.ai_analysis?.summary || 'No summary available'}
                      </p>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <span>{formatDate(material.created_at)}</span>
                        <span>{material.word_count || 0} words</span>
                        <span>{formatFileSize(material.file_size)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => handleStarToggle(material.id, e)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      {material.starred ? (
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                      ) : (
                        <StarOff className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                    
                    <button
                      onClick={(e) => handleMaterialAction(material, 'view', e)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <Eye className="h-4 w-4 text-gray-400" />
                    </button>
                    
                    <button
                      onClick={(e) => handleMaterialAction(material, 'download', e)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <Download className="h-4 w-4 text-gray-400" />
                    </button>
                    
                    <button
                      onClick={(e) => handleMaterialAction(material, 'edit', e)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <Edit className="h-4 w-4 text-gray-400" />
                    </button>
                    
                    <button
                      onClick={(e) => handleMaterialAction(material, 'delete', e)}
                      className="p-1 hover:bg-gray-100 rounded text-red-500"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
