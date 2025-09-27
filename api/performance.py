"""
Vercel serverless function to handle performance tracking and analytics
"""

import os
import json
from http.server import BaseHTTPRequestHandler
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
else:
    supabase = None

def get_performance_data(user_id):
    """Get performance data for a user"""
    if not supabase:
        # Return mock data for development
        return {
            "overall_score": 75,
            "topics_studied": 5,
            "total_time": 3600,
            "quizzes_completed": 24,
            "topics_mastered": 8,
            "active_paths": 2,
            "recent_activities": [
                {
                    "id": 1,
                    "type": "quiz_attempt",
                    "title": "Algebra Quiz",
                    "topic": "Basic Algebra",
                    "score": 85,
                    "timestamp": "2024-01-15T10:30:00Z",
                    "status": "passed"
                }
            ],
            "weaknesses": [
                {
                    "id": 1,
                    "topic_id": 1,
                    "severity": "medium",
                    "description": "Struggling with algebraic equations",
                    "confidence_score": 0.8
                }
            ],
            "strengths": [
                {
                    "topic_id": 2,
                    "score": 85,
                    "mastery_level": "intermediate"
                }
            ]
        }
    
    try:
        # Get performance data from Supabase
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).execute()
        quiz_attempts_response = supabase.table('quiz_attempts').select('*').eq('user_id', user_id).execute()
        
        # Calculate overall metrics
        performances = performance_response.data
        quiz_attempts = quiz_attempts_response.data
        
        overall_score = sum(p.get('overall_score', 0) for p in performances) / len(performances) if performances else 0
        total_time = sum(p.get('time_spent', 0) for p in performances)
        topics_studied = len(performances)
        quizzes_completed = len(quiz_attempts)
        
        return {
            "overall_score": overall_score,
            "topics_studied": topics_studied,
            "total_time": total_time,
            "quizzes_completed": quizzes_completed,
            "topics_mastered": len([p for p in performances if p.get('mastery_level') == 'expert']),
            "active_paths": 2,  # Mock data
            "recent_activities": quiz_attempts[-5:] if quiz_attempts else [],
            "weaknesses": [],  # Would be calculated from performance data
            "strengths": []    # Would be calculated from performance data
        }
        
    except Exception as e:
        print(f"Error getting performance data: {e}")
        return None

def save_quiz_result(user_id, quiz_id, responses, time_taken):
    """Save quiz results to database"""
    if not supabase:
        # Mock response for development
        return {
            "success": True,
            "score": 75,
            "percentage": 75,
            "is_passed": True
        }
    
    try:
        # Calculate score (mock calculation)
        correct_answers = len([r for r in responses if r.get('answer') == 'correct'])  # Simplified
        total_questions = len(responses)
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Save quiz attempt
        quiz_attempt = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "score": score,
            "percentage": score,
            "time_taken": time_taken,
            "responses": responses,
            "is_completed": True,
            "is_passed": score >= 70
        }
        
        result = supabase.table('quiz_attempts').insert(quiz_attempt).execute()
        
        return {
            "success": True,
            "score": score,
            "percentage": score,
            "is_passed": score >= 70,
            "attempt_id": result.data[0]['id'] if result.data else None
        }
        
    except Exception as e:
        print(f"Error saving quiz result: {e}")
        return {
            "success": False,
            "error": str(e)
        }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get user ID from query parameters or headers
            user_id = self.headers.get('X-User-ID', 'demo-user')
            
            # Get performance data
            performance_data = get_performance_data(user_id)
            
            if performance_data is None:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    "success": False,
                    "error": "Failed to get performance data"
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(performance_data).encode('utf-8'))
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "success": False,
                "error": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            user_id = data.get('user_id', 'demo-user')
            quiz_id = data.get('quiz_id', 1)
            responses = data.get('responses', [])
            time_taken = data.get('time_taken', 0)
            
            # Save quiz result
            result = save_quiz_result(user_id, quiz_id, responses, time_taken)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-User-ID')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "success": False,
                "error": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-User-ID')
        self.end_headers()
