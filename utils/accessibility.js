/**
 * Accessibility utilities for Text-to-Speech and Speech-to-Text
 */

// Text-to-Speech functionality
export const textToSpeech = (text, options = {}) => {
  if ('speechSynthesis' in window) {
    // Cancel any ongoing speech
    speechSynthesis.cancel()
    
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = options.rate || 1
    utterance.pitch = options.pitch || 1
    utterance.volume = options.volume || 1
    utterance.lang = options.lang || 'en-US'
    
    if (options.voice) {
      utterance.voice = options.voice
    }
    
    // Add event listeners
    utterance.onstart = () => {
      if (options.onStart) options.onStart()
    }
    
    utterance.onend = () => {
      if (options.onEnd) options.onEnd()
    }
    
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error)
      if (options.onError) options.onError(event.error)
    }
    
    speechSynthesis.speak(utterance)
    return utterance
  } else {
    console.warn('Speech synthesis not supported')
    return null
  }
}

// Speech-to-Text functionality
export const speechToText = (options = {}) => {
  return new Promise((resolve, reject) => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      
      recognition.continuous = options.continuous || false
      recognition.interimResults = options.interimResults || false
      recognition.lang = options.lang || 'en-US'
      recognition.maxAlternatives = options.maxAlternatives || 1
      
      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0])
          .map(result => result.transcript)
          .join('')
        resolve(transcript)
      }
      
      recognition.onerror = (event) => {
        reject(new Error(`Speech recognition error: ${event.error}`))
      }
      
      recognition.onend = () => {
        if (options.onEnd) options.onEnd()
      }
      
      recognition.onstart = () => {
        if (options.onStart) options.onStart()
      }
      
      recognition.start()
    } else {
      reject(new Error('Speech recognition not supported'))
    }
  })
}

// Get available voices for TTS
export const getAvailableVoices = () => {
  if ('speechSynthesis' in window) {
    return speechSynthesis.getVoices()
  }
  return []
}

// Stop current speech
export const stopSpeech = () => {
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel()
  }
}

// Pause current speech
export const pauseSpeech = () => {
  if ('speechSynthesis' in window) {
    speechSynthesis.pause()
  }
}

// Resume paused speech
export const resumeSpeech = () => {
  if ('speechSynthesis' in window) {
    speechSynthesis.resume()
  }
}

// Check if speech synthesis is supported
export const isSpeechSynthesisSupported = () => {
  return 'speechSynthesis' in window
}

// Check if speech recognition is supported
export const isSpeechRecognitionSupported = () => {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
}

// Enhanced TTS with better error handling
export const enhancedTextToSpeech = async (text, options = {}) => {
  if (!isSpeechSynthesisSupported()) {
    throw new Error('Speech synthesis not supported in this browser')
  }

  return new Promise((resolve, reject) => {
    const utterance = new SpeechSynthesisUtterance(text)
    
    // Set options
    utterance.rate = options.rate || 1
    utterance.pitch = options.pitch || 1
    utterance.volume = options.volume || 1
    utterance.lang = options.lang || 'en-US'
    
    // Set voice if specified
    if (options.voice) {
      utterance.voice = options.voice
    }
    
    // Event handlers
    utterance.onstart = () => {
      if (options.onStart) options.onStart()
    }
    
    utterance.onend = () => {
      if (options.onEnd) options.onEnd()
      resolve()
    }
    
    utterance.onerror = (event) => {
      reject(new Error(`Speech synthesis error: ${event.error}`))
    }
    
    // Start speaking
    speechSynthesis.speak(utterance)
  })
}

// Enhanced STT with better error handling
export const enhancedSpeechToText = (options = {}) => {
  if (!isSpeechRecognitionSupported()) {
    return Promise.reject(new Error('Speech recognition not supported in this browser'))
  }

  return new Promise((resolve, reject) => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    
    // Set options
    recognition.continuous = options.continuous || false
    recognition.interimResults = options.interimResults || false
    recognition.lang = options.lang || 'en-US'
    recognition.maxAlternatives = options.maxAlternatives || 1
    
    // Timeout handling
    let timeoutId
    if (options.timeout) {
      timeoutId = setTimeout(() => {
        recognition.stop()
        reject(new Error('Speech recognition timeout'))
      }, options.timeout)
    }
    
    recognition.onresult = (event) => {
      if (timeoutId) clearTimeout(timeoutId)
      
      const transcript = Array.from(event.results)
        .map(result => result[0])
        .map(result => result.transcript)
        .join('')
      
      resolve(transcript)
    }
    
    recognition.onerror = (event) => {
      if (timeoutId) clearTimeout(timeoutId)
      reject(new Error(`Speech recognition error: ${event.error}`))
    }
    
    recognition.onend = () => {
      if (timeoutId) clearTimeout(timeoutId)
      if (options.onEnd) options.onEnd()
    }
    
    recognition.onstart = () => {
      if (options.onStart) options.onStart()
    }
    
    recognition.start()
  })
}

// Utility to speak quiz questions with proper formatting
export const speakQuizQuestion = (question, options = {}) => {
  const formattedText = `Question: ${question.question_text}. ${
    question.options ? `Options: ${question.options.join(', ')}` : ''
  }`
  
  return textToSpeech(formattedText, {
    rate: 0.8, // Slightly slower for better comprehension
    ...options
  })
}

// Utility to speak quiz results
export const speakQuizResults = (score, totalQuestions, options = {}) => {
  const percentage = Math.round((score / totalQuestions) * 100)
  const text = `Quiz completed. You scored ${score} out of ${totalQuestions} questions. That's ${percentage} percent. ${
    percentage >= 80 ? 'Excellent work!' : 
    percentage >= 60 ? 'Good job!' : 
    'Keep practicing to improve your score.'
  }`
  
  return textToSpeech(text, {
    rate: 0.9,
    ...options
  })
}

// Utility to speak progress updates
export const speakProgressUpdate = (progressData, options = {}) => {
  const text = `Your current performance is ${progressData.overall_score} percent. ${
    progressData.topics_studied
  } topics studied. Total study time: ${Math.round(progressData.total_time / 3600)} hours.`
  
  return textToSpeech(text, {
    rate: 0.9,
    ...options
  })
}
