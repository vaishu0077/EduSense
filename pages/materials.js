import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useRouter } from 'next/router'
import { 
  BookOpen, 
  Upload, 
  FileText, 
  Brain, 
  Plus,
  Search,
  Filter,
  Grid,
  List
} from 'lucide-react'
import FileUpload from '../components/FileUpload'
import MaterialLibrary from '../components/MaterialLibrary'
import MaterialAnalysis from '../components/MaterialAnalysis'
import toast from 'react-hot-toast'

export default function Materials() {
  const { user, loading } = useAuth()
  const router = useRouter()
  
  const [materials, setMaterials] = useState([])
  const [selectedMaterial, setSelectedMaterial] = useState(null)
  const [showUpload, setShowUpload] = useState(false)
  const [loadingMaterials, setLoadingMaterials] = useState(true)

  useEffect(() => {
    if (user) {
      loadMaterials()
    }
  }, [user])

  const loadMaterials = async () => {
    try {
      setLoadingMaterials(true)
      const response = await fetch('/api/materials-services?service=search')
      const data = await response.json()
      
      if (data.success) {
        setMaterials(data.materials || [])
      } else {
        console.error('Failed to load materials:', data.error)
        // Use demo data if API fails
        setMaterials(getDemoMaterials())
      }
    } catch (error) {
      console.error('Error loading materials:', error)
      setMaterials(getDemoMaterials())
    } finally {
      setLoadingMaterials(false)
    }
  }

  const getDemoMaterials = () => [
    {
      id: 'demo-1',
      filename: 'Calculus Fundamentals.pdf',
      content: 'Calculus is the mathematical study of continuous change...',
      ai_analysis: {
        summary: 'Introduction to calculus concepts including derivatives and integrals',
        key_topics: ['derivatives', 'integrals', 'limits'],
        subject_category: 'mathematics',
        difficulty_level: 'intermediate',
        learning_objectives: ['Understand derivatives', 'Master integration techniques'],
        key_concepts: ['Rate of change', 'Area under curve', 'Fundamental theorem'],
        suggested_quiz_questions: [
          {
            question: 'What is the derivative of x²?',
            difficulty: 'easy',
            topic: 'derivatives'
          }
        ],
        study_recommendations: ['Practice derivative rules', 'Work through integration examples']
      },
      word_count: 1500,
      created_at: '2024-01-15T10:00:00Z'
    },
    {
      id: 'demo-2',
      filename: 'World War II History.docx',
      content: 'World War II was a global war that lasted from 1939 to 1945...',
      ai_analysis: {
        summary: 'Comprehensive overview of World War II events and impact',
        key_topics: ['battles', 'politics', 'economics'],
        subject_category: 'history',
        difficulty_level: 'intermediate',
        learning_objectives: ['Understand war causes', 'Analyze war impact'],
        key_concepts: ['Alliance systems', 'Economic factors', 'Political ideologies'],
        suggested_quiz_questions: [
          {
            question: 'When did World War II begin?',
            difficulty: 'easy',
            topic: 'timeline'
          }
        ],
        study_recommendations: ['Study timeline of events', 'Analyze causes and effects']
      },
      word_count: 2000,
      created_at: '2024-01-14T15:30:00Z'
    }
  ]

  const handleFileUpload = (uploadResult) => {
    console.log('File uploaded:', uploadResult)
    toast.success('Material uploaded and analyzed successfully!')
    
    // Add the new material to the list immediately
    if (uploadResult.success) {
      const newMaterial = {
        id: uploadResult.material_id,
        filename: uploadResult.filename,
        file_type: uploadResult.file_type,
        content: uploadResult.content_preview,
        ai_analysis: uploadResult.ai_analysis,
        word_count: uploadResult.word_count,
        char_count: uploadResult.char_count,
        starred: false,
        tags: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      setMaterials(prev => [newMaterial, ...prev])
    }
    
    loadMaterials() // Reload materials
    setShowUpload(false)
  }

  const handleMaterialSelect = (material) => {
    setSelectedMaterial(material)
  }

  const handleMaterialDelete = (material) => {
    if (confirm(`Are you sure you want to delete "${material.filename}"?`)) {
      setMaterials(prev => prev.filter(m => m.id !== material.id))
      if (selectedMaterial?.id === material.id) {
        setSelectedMaterial(null)
      }
      toast.success('Material deleted successfully')
    }
  }

  const handleMaterialEdit = (material) => {
    // Implement material editing
    console.log('Edit material:', material)
    toast.info('Material editing feature coming soon!')
  }

  const handleGenerateQuiz = async (material) => {
    try {
      const response = await fetch('/api/generate-quiz-from-material', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: material.content,
          ai_analysis: material.ai_analysis,
          num_questions: 5,
          difficulty: 'medium'
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate quiz')
      }

      const data = await response.json()
      
      if (data.success) {
        // Store quiz data and redirect to quiz page
        localStorage.setItem('materialQuiz', JSON.stringify({
          title: data.quiz_title,
          description: data.quiz_description,
          questions: data.questions,
          material_based: true,
          source_material: data.source_material
        }))
        
        router.push('/quiz')
        toast.success('Quiz generated from material!')
      } else {
        throw new Error(data.error || 'Failed to generate quiz')
      }
    } catch (error) {
      console.error('Error generating quiz:', error)
      toast.error('Failed to generate quiz from material')
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
    router.push('/auth')
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-indigo-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">Study Materials</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowUpload(!showUpload)}
                className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
              >
                <Plus className="h-4 w-4 mr-2" />
                Upload Material
              </button>
              <button
                onClick={() => router.push('/')}
                className="text-indigo-600 hover:text-indigo-500 font-medium"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {showUpload ? (
          /* Upload Section */
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload New Material</h2>
              <FileUpload onFileUpload={handleFileUpload} />
            </div>
            
            <button
              onClick={() => setShowUpload(false)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← Back to Materials Library
            </button>
          </div>
        ) : (
          /* Main Content */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Materials Library */}
            <div className="lg:col-span-2">
              {loadingMaterials ? (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading materials...</p>
                </div>
              ) : (
                <MaterialLibrary
                  materials={materials}
                  onMaterialSelect={handleMaterialSelect}
                  onMaterialDelete={handleMaterialDelete}
                  onMaterialEdit={handleMaterialEdit}
                />
              )}
            </div>

            {/* Material Analysis */}
            <div className="lg:col-span-1">
              {selectedMaterial ? (
                <MaterialAnalysis
                  material={selectedMaterial}
                  onGenerateQuiz={handleGenerateQuiz}
                />
              ) : (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
                  <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Material</h3>
                  <p className="text-gray-500">
                    Choose a material from the library to view its AI analysis and generate quizzes
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
