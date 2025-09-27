"""
Vercel serverless function to handle performance tracking and analytics
"""

import os
import json
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
        # Return empty data structure when Supabase is not configured
        return {
            "overall_score": 0,
            "topics_studied": 0,
            "total_time": 0,
            "quizzes_completed": 0,
            "topics_mastered": 0,
            "active_paths": 0,
            "recent_activities": [],
            "weaknesses": [],
            "strengths": [],
            "performance_over_time": [],
            "subject_performance": [],
            "topic_mastery": [],
            "weekly_activity": [],
            "recent_topics": []
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
        # Return error when Supabase is not configured
        return {
            "success": False,
            "error": "Database not configured. Please set up Supabase environment variables.",
            "score": 0,
            "percentage": 0,
            "is_passed": False
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

def handler(request):
    """Main handler function for Vercel"""
    try:
        # Handle CORS
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, X-User-ID',
                },
                'body': ''
            }
        
        if request.method == 'GET':
            # Get user ID from query parameters or headers
            user_id = request.headers.get('X-User-ID', 'demo-user')
            
            # Get performance data
            performance_data = get_performance_data(user_id)
            
            if performance_data is None:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({
                        "success": False,
                        "error": "Failed to get performance data"
                    })
                }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(performance_data)
            }
        
        elif request.method == 'POST':
            # Parse request body
            data = json.loads(request.body)
            
            # Extract parameters
            user_id = data.get('user_id', 'demo-user')
            quiz_id = data.get('quiz_id', 1)
            responses = data.get('responses', [])
            time_taken = data.get('time_taken', 0)
            
            # Save quiz result
            result = save_quiz_result(user_id, quiz_id, responses, time_taken)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(result)
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                "success": False,
                "error": str(e)
            })
        }
