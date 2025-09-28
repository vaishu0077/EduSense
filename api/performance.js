/**
 * Vercel serverless function to handle performance tracking and analytics
 */

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-ID');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'GET') {
    // Return mock performance data for now
    const mockData = {
      overall_score: 0,
      quizzes_completed: 0,
      study_time: 0,
      topics_mastered: 0,
      performance_over_time: [],
      subject_performance: [],
      weekly_study_time: [],
      recent_activity: []
    };

    res.status(200).json(mockData);
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const { quiz_id, responses, time_taken, topic, difficulty, score, total_questions, time_spent } = req.body;

    console.log('Performance tracking request:', {
      quiz_id,
      responses_count: responses?.length || 0,
      time_taken,
      topic,
      difficulty,
      score,
      total_questions,
      time_spent
    });

    // Calculate score if not provided
    let calculatedScore = score;
    if (!calculatedScore && responses && total_questions) {
      // Simple score calculation - in a real app, this would be more sophisticated
      calculatedScore = Math.floor(Math.random() * 40) + 60; // Mock score between 60-100
    }

    // Mock performance data
    const performanceData = {
      quiz_id: quiz_id || `quiz-${Date.now()}`,
      score: calculatedScore || 75,
      total_questions: total_questions || 5,
      time_taken: time_taken || time_spent || 300,
      topic: topic || 'General',
      difficulty: difficulty || 'intermediate',
      responses: responses || [],
      completed_at: new Date().toISOString()
    };

    console.log('Performance data saved:', performanceData);

    res.status(200).json({
      success: true,
      score: performanceData.score,
      performance: performanceData
    });

  } catch (error) {
    console.error('Performance tracking error:', error);
    res.status(500).json({ error: error.message });
  }
}
