import { useState, useRef, useCallback } from 'react'
import { Upload, File, X, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import toast from 'react-hot-toast'

export default function FileUpload({ onFileUpload, maxFiles = 5, acceptedTypes = ['.pdf', '.doc', '.docx', '.txt'] }) {
  const [files, setFiles] = useState([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef(null)

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    handleFiles(droppedFiles)
  }, [])

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files)
    handleFiles(selectedFiles)
  }

    const handleFiles = (newFiles) => {
      const maxFileSize = 1 * 1024 * 1024 // 1MB limit for PDFs
    
    const validFiles = newFiles.filter(file => {
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
      const isAcceptedType = acceptedTypes.includes(fileExtension)
      const isWithinSizeLimit = file.size <= maxFileSize
      
      if (!isAcceptedType) {
        toast.error(`${file.name}: Unsupported file type`)
      }
        if (!isWithinSizeLimit) {
          toast.error(`${file.name}: File too large (max 1MB)`)
        }
      
      return isAcceptedType && isWithinSizeLimit
    })

    if (validFiles.length !== newFiles.length) {
      toast.error('Some files were rejected. Check file types and sizes.')
    }

    if (validFiles.length + files.length > maxFiles) {
      toast.error(`Maximum ${maxFiles} files allowed`)
      return
    }

    const filesWithStatus = validFiles.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0,
      error: null
    }))

    setFiles(prev => [...prev, ...filesWithStatus])
  }

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const uploadFile = async (fileItem) => {
    try {
      setUploading(true)
      
      // Read file content as text (for text-based files)
      const content = await readFileAsText(fileItem.file)
      
      // Prepare data for API
      const uploadData = {
        filename: fileItem.name,
        content: content,
        type: fileItem.type,
        user_id: 'demo-user' // This should come from auth context
      }

      const response = await fetch('/api/upload-material', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(uploadData)
      })

      if (!response.ok) {
        let errorMessage = 'Upload failed'
        try {
          const errorData = await response.json()
          errorMessage = errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`
        } catch (jsonError) {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      let result
      try {
        result = await response.json()
      } catch (jsonError) {
        console.error('JSON parsing error:', jsonError)
        throw new Error('Invalid response from server')
      }
      
      // Update file status
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'completed', progress: 100, result }
          : f
      ))

      // Store uploaded material in localStorage
      const uploadedMaterial = {
        id: result.material_id || `material-${Date.now()}`,
        filename: fileItem.name,
        file_type: fileItem.type,
        file_size: fileItem.size,
        content: result.content_preview || content.substring(0, 500) + '...',
        ai_analysis: result.ai_analysis || {
          summary: "AI analysis in progress...",
          key_topics: [],
          subject_category: "general",
          difficulty_level: "intermediate",
          learning_objectives: [],
          study_recommendations: []
        },
        word_count: result.word_count || Math.floor(content.split(' ').length),
        char_count: result.char_count || content.length,
        starred: false,
        tags: result.tags || [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }

      // Store in localStorage
      const existingMaterials = JSON.parse(localStorage.getItem('uploadedMaterials') || '[]')
      existingMaterials.unshift(uploadedMaterial) // Add to beginning
      localStorage.setItem('uploadedMaterials', JSON.stringify(existingMaterials))

      toast.success(`${fileItem.name} uploaded successfully`)
      
      if (onFileUpload) {
        onFileUpload(result)
      }

    } catch (error) {
      console.error('Upload error:', error)
      
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'error', error: error.message }
          : f
      ))

      toast.error(`Failed to upload ${fileItem.name}: ${error.message}`)
    } finally {
      setUploading(false)
    }
  }

  const readFileAsText = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target.result)
      reader.onerror = (e) => reject(e)
      reader.readAsText(file)
    })
  }

  const uploadAllFiles = async () => {
    const pendingFiles = files.filter(f => f.status === 'pending')
    
    for (const fileItem of pendingFiles) {
      // Update status to uploading
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      ))
      
      await uploadFile(fileItem)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileIcon = (fileType) => {
    if (fileType.includes('pdf')) return '📄'
    if (fileType.includes('word') || fileType.includes('document')) return '📝'
    if (fileType.includes('text')) return '📃'
    return '📁'
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'uploading':
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />
      default:
        return <File className="h-5 w-5 text-gray-400" />
    }
  }

  return (
    <div className="w-full">
      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Upload Study Materials
        </h3>
        <p className="text-gray-600 mb-4">
          Drag and drop files here, or click to select files
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Supported formats: PDF, DOC, DOCX, TXT (Max {maxFiles} files, 4MB each)
        </p>
        
        <button
          onClick={() => fileInputRef.current?.click()}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Choose Files
        </button>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-lg font-medium text-gray-900">
              Files ({files.length})
            </h4>
            {files.some(f => f.status === 'pending') && (
              <button
                onClick={uploadAllFiles}
                disabled={uploading}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {uploading ? 'Uploading...' : 'Upload All'}
              </button>
            )}
          </div>

          <div className="space-y-3">
            {files.map((fileItem) => (
              <div
                key={fileItem.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{getFileIcon(fileItem.type)}</span>
                  <div>
                    <p className="font-medium text-gray-900">{fileItem.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(fileItem.size)}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {fileItem.status === 'uploading' && (
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${fileItem.progress}%` }}
                      />
                    </div>
                  )}
                  
                  {getStatusIcon(fileItem.status)}
                  
                  {fileItem.status === 'error' && (
                    <span className="text-sm text-red-500">{fileItem.error}</span>
                  )}
                  
                  <button
                    onClick={() => removeFile(fileItem.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
