// Test script to check quiz API
const testQuizAPI = async () => {
  try {
    console.log('Testing quiz API...')
    
    const response = await fetch('/api/generate_quiz', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic: 'Mathematics',
        difficulty: 'medium',
        num_questions: 3,
        time_limit: 30
      })
    })
    
    console.log('Response status:', response.status)
    console.log('Response ok:', response.ok)
    
    const data = await response.json()
    console.log('Response data:', data)
    
    if (data.success && data.questions) {
      console.log('✅ Quiz API working! Questions:', data.questions.length)
      data.questions.forEach((q, i) => {
        console.log(`Question ${i+1}:`, q.question)
        console.log(`Options:`, q.options)
      })
    } else {
      console.log('❌ Quiz API failed:', data)
    }
    
  } catch (error) {
    console.error('❌ Quiz API error:', error)
  }
}

// Run test
testQuizAPI()
