// Test Database Connection
// Run this in your browser console on your deployed app

async function testDatabase() {
  console.log('🧪 Testing database connection...')
  
  try {
    // Test performance API
    const response = await fetch('/api/performance', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    const data = await response.json()
    console.log('✅ Performance API Response:', data)
    
    // Test quiz generation
    const quizResponse = await fetch('/api/generate_quiz', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic: 'Mathematics',
        difficulty: 'easy',
        num_questions: 2
      })
    })
    
    const quizData = await quizResponse.json()
    console.log('✅ Quiz Generation Response:', quizData)
    
    console.log('🎉 Database tests completed!')
    
  } catch (error) {
    console.error('❌ Database test failed:', error)
  }
}

// Run the test
testDatabase()
