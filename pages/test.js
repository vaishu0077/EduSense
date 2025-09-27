import { useState } from 'react'

export default function Test() {
  const [apiResult, setApiResult] = useState(null)

  const testAPI = async () => {
    try {
      const response = await fetch('/api/hello')
      const data = await response.json()
      setApiResult(data)
    } catch (error) {
      setApiResult({ error: error.message })
    }
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>EduSense Test Page</h1>
      <p>This is a simple test page to verify the deployment is working.</p>
      
      <div style={{ marginTop: '20px' }}>
        <button 
          onClick={testAPI}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#0070f3', 
            color: 'white', 
            border: 'none', 
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Test API
        </button>
      </div>

      {apiResult && (
        <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
          <h3>API Response:</h3>
          <pre>{JSON.stringify(apiResult, null, 2)}</pre>
        </div>
      )}
      
      <div style={{ marginTop: '20px' }}>
        <a href="/" style={{ color: 'blue', textDecoration: 'underline' }}>
          Go to Home Page
        </a>
      </div>
    </div>
  )
}
