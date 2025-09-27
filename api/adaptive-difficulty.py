"""
Vercel serverless function for adaptive difficulty adjustment using AI
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from supabase import create_client, Client

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# Initialize Supabase client
supabase_url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
else:
    supabase = None

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for adaptive difficulty adjustment"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8')) if post_data else {}
            except:
                data = {}
            
            # Extract parameters
            user_id = data.get('user_id', 'demo-user')
            current_performance = data.get('current_performance', {})
            topic = data.get('topic', 'general')
            current_difficulty = data.get('current_difficulty', 'medium')
            
            # Get user's learning history
            learning_history = get_user_learning_history(user_id)
            
            # Calculate adaptive difficulty
            result = calculate_adaptive_difficulty(
                user_id,
                current_performance,
                learning_history,
                topic,
                current_difficulty
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Adaptive difficulty error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "recommended_difficulty": "medium",
                "confidence": 0.5
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def get_user_learning_history(user_id):
    """Get user's learning history and performance data"""
    if not supabase:
        return get_demo_learning_history()
    
    try:
        # Get performance data
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        performances = performance_response.data or []
        
        # Get quiz attempts
        quiz_response = supabase.table('quiz_attempts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(30).execute()
        quiz_attempts = quiz_response.data or []
        
        return {
            "performances": performances,
            "quiz_attempts": quiz_attempts,
            "total_attempts": len(performances) + len(quiz_attempts)
        }
        
    except Exception as e:
        print(f"Error getting learning history: {e}")
        return get_demo_learning_history()

def get_demo_learning_history():
    """Return demo learning history when database is not available"""
    return {
        "performances": [
            {"score": 85, "total_questions": 10, "topic": "mathematics", "difficulty": "medium", "time_spent": 300},
            {"score": 92, "total_questions": 8, "topic": "mathematics", "difficulty": "easy", "time_spent": 240},
            {"score": 78, "total_questions": 12, "topic": "science", "difficulty": "hard", "time_spent": 450}
        ],
        "quiz_attempts": [
            {"score": 80, "total_questions": 5, "topic": "mathematics", "difficulty": "medium"},
            {"score": 90, "total_questions": 5, "topic": "science", "difficulty": "easy"}
        ],
        "total_attempts": 5
    }

def calculate_adaptive_difficulty(user_id, current_performance, learning_history, topic, current_difficulty):
    """Calculate adaptive difficulty using AI and performance data"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare learning data for AI analysis
        recent_performances = learning_history.get('performances', [])[:10]
        recent_quizzes = learning_history.get('quiz_attempts', [])[:10]
        
        # Calculate performance metrics
        avg_score = calculate_average_score(recent_performances + recent_quizzes)
        topic_performance = calculate_topic_performance(recent_performances + recent_quizzes, topic)
        difficulty_trend = analyze_difficulty_trend(recent_performances + recent_quizzes)
        time_efficiency = calculate_time_efficiency(recent_performances + recent_quizzes)
        
        # Create AI prompt for difficulty adjustment
        prompt = f"""
        Analyze this student's learning performance and recommend the optimal difficulty level.
        
        Student Performance Data:
        - Current Topic: {topic}
        - Current Difficulty: {current_difficulty}
        - Average Score: {avg_score}%
        - Topic Performance: {topic_performance}%
        - Difficulty Trend: {difficulty_trend}
        - Time Efficiency: {time_efficiency}
        
        Recent Performance History:
        {json.dumps(recent_performances[:5], indent=2)}
        
        Current Performance:
        {json.dumps(current_performance, indent=2)}
        
        Based on this data, recommend the next difficulty level and provide reasoning.
        
        Return JSON format:
        {{
            "recommended_difficulty": "easy|medium|hard",
            "confidence": 0.0-1.0,
            "reasoning": "Explanation of the recommendation",
            "performance_insights": {{
                "strengths": ["strength1", "strength2"],
                "weaknesses": ["weakness1", "weakness2"],
                "improvement_areas": ["area1", "area2"]
            }},
            "next_steps": [
                "specific recommendation 1",
                "specific recommendation 2"
            ],
            "difficulty_adjustment": {{
                "current": "{current_difficulty}",
                "recommended": "easy|medium|hard",
                "change_reason": "Why this change is needed"
            }}
        }}
        
        Consider:
        1. Performance consistency
        2. Topic mastery level
        3. Time efficiency
        4. Learning curve progression
        5. Engagement and motivation factors
        """
        
        response = model.generate_content(prompt)
        
        # Parse AI response
        try:
            ai_result = json.loads(response.text)
            
            # Validate and enhance the result
            result = {
                "success": True,
                "recommended_difficulty": ai_result.get('recommended_difficulty', 'medium'),
                "confidence": ai_result.get('confidence', 0.7),
                "reasoning": ai_result.get('reasoning', 'AI analysis completed'),
                "performance_insights": ai_result.get('performance_insights', {}),
                "next_steps": ai_result.get('next_steps', []),
                "difficulty_adjustment": ai_result.get('difficulty_adjustment', {}),
                "analytics": {
                    "avg_score": avg_score,
                    "topic_performance": topic_performance,
                    "difficulty_trend": difficulty_trend,
                    "time_efficiency": time_efficiency,
                    "total_attempts": learning_history.get('total_attempts', 0)
                }
            }
            
            return result
            
        except json.JSONDecodeError:
            # Fallback to rule-based difficulty adjustment
            return get_rule_based_difficulty(current_performance, topic_performance, avg_score)
            
    except Exception as e:
        print(f"AI difficulty calculation error: {e}")
        return get_rule_based_difficulty(current_performance, topic_performance, avg_score)

def calculate_average_score(performances):
    """Calculate average score from performance data"""
    if not performances:
        return 75  # Default score
    
    total_score = sum(p.get('score', 0) for p in performances)
    total_questions = sum(p.get('total_questions', 1) for p in performances)
    
    if total_questions == 0:
        return 75
    
    return round((total_score / total_questions) * 100)

def calculate_topic_performance(performances, topic):
    """Calculate performance for specific topic"""
    topic_performances = [p for p in performances if p.get('topic', '').lower() == topic.lower()]
    
    if not topic_performances:
        return 75  # Default if no topic data
    
    return calculate_average_score(topic_performances)

def analyze_difficulty_trend(performances):
    """Analyze difficulty progression trend"""
    if len(performances) < 3:
        return "stable"
    
    recent_scores = []
    for p in performances[:5]:
        score_pct = (p.get('score', 0) / p.get('total_questions', 1)) * 100
        recent_scores.append(score_pct)
    
    if len(recent_scores) < 2:
        return "stable"
    
    # Calculate trend
    first_half = recent_scores[:len(recent_scores)//2]
    second_half = recent_scores[len(recent_scores)//2:]
    
    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)
    
    if second_avg > first_avg + 5:
        return "improving"
    elif second_avg < first_avg - 5:
        return "declining"
    else:
        return "stable"

def calculate_time_efficiency(performances):
    """Calculate time efficiency score"""
    if not performances:
        return 0.5
    
    total_time = sum(p.get('time_spent', 0) for p in performances)
    total_questions = sum(p.get('total_questions', 1) for p in performances)
    
    if total_time == 0 or total_questions == 0:
        return 0.5
    
    avg_time_per_question = total_time / total_questions
    
    # Efficiency score (lower time per question = higher efficiency)
    if avg_time_per_question < 30:  # Less than 30 seconds per question
        return 0.9
    elif avg_time_per_question < 60:  # Less than 1 minute per question
        return 0.7
    elif avg_time_per_question < 120:  # Less than 2 minutes per question
        return 0.5
    else:
        return 0.3

def get_rule_based_difficulty(current_performance, topic_performance, avg_score):
    """Fallback rule-based difficulty adjustment"""
    # Simple rule-based logic
    if avg_score >= 90:
        recommended = "hard"
        confidence = 0.8
    elif avg_score >= 75:
        recommended = "medium"
        confidence = 0.7
    else:
        recommended = "easy"
        confidence = 0.6
    
    return {
        "success": True,
        "recommended_difficulty": recommended,
        "confidence": confidence,
        "reasoning": f"Based on average score of {avg_score}%",
        "performance_insights": {
            "strengths": ["Consistent performance"] if avg_score >= 80 else [],
            "weaknesses": ["Needs more practice"] if avg_score < 70 else [],
            "improvement_areas": ["Focus on weak topics"] if avg_score < 80 else []
        },
        "next_steps": [
            f"Continue with {recommended} difficulty",
            "Monitor performance closely"
        ],
        "difficulty_adjustment": {
            "current": "medium",
            "recommended": recommended,
            "change_reason": f"Score-based adjustment ({avg_score}%)"
        },
        "analytics": {
            "avg_score": avg_score,
            "topic_performance": topic_performance,
            "difficulty_trend": "stable",
            "time_efficiency": 0.5,
            "total_attempts": 0
        }
    }
