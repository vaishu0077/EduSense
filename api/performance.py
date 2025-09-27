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

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-ID')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for performance data"""
        try:
            # Get user ID from headers
            user_id = self.headers.get('X-User-ID', 'demo-user')
            
            # Get performance data
            performance_data = get_performance_data(user_id)
            
            # Always return data, even if empty
            if performance_data is None:
                performance_data = get_empty_performance_data()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(performance_data).encode('utf-8'))
            
        except Exception as e:
            print(f"Performance GET error: {e}")
            # Return empty data instead of error
            empty_data = get_empty_performance_data()
            empty_data["error"] = f"API Error: {str(e)}"
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(empty_data).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests for saving quiz results"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8')) if post_data else {}
            except:
                data = {}
            
            # Extract user ID from headers or data
            user_id = self.headers.get('X-User-ID', data.get('user_id', 'demo-user'))
            
            # Save quiz result
            result = save_quiz_result(user_id, data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Performance POST error: {e}")
            error_result = {
                "success": False,
                "error": str(e)
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def get_empty_performance_data():
    """Return empty performance data structure"""
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
        "recent_topics": [],
        "stats": {
            "completed_quizzes": 0,
            "average_score": 0,
            "study_streak": 0,
            "total_study_time": 0
        }
    }

def get_performance_data(user_id):
    """Get performance data for a user"""
    if not supabase:
        # Return empty data structure when Supabase is not configured
        return get_empty_performance_data()
    
    try:
        # Get performance data from Supabase
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        
        performances = performance_response.data
        
        if not performances:
            return get_empty_performance_data()
        
        # Calculate metrics
        total_score = sum(p.get('score', 0) for p in performances)
        total_questions = sum(p.get('total_questions', 0) for p in performances)
        overall_score = round((total_score / total_questions * 100)) if total_questions > 0 else 0
        total_time = sum(p.get('time_spent', 0) for p in performances)
        quizzes_completed = len(performances)
        
        # Group by topic for subject performance
        topic_stats = {}
        for p in performances:
            topic = p.get('topic', 'Unknown')
            if topic not in topic_stats:
                topic_stats[topic] = {'scores': [], 'count': 0, 'total_questions': 0}
            
            score_percentage = (p.get('score', 0) / p.get('total_questions', 1)) * 100
            topic_stats[topic]['scores'].append(score_percentage)
            topic_stats[topic]['count'] += 1
            topic_stats[topic]['total_questions'] += p.get('total_questions', 0)
        
        # Create subject performance data
        subject_performance = []
        topic_mastery = []
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#F97316']
        
        for i, (topic, stats) in enumerate(topic_stats.items()):
            avg_score = round(sum(stats['scores']) / len(stats['scores'])) if stats['scores'] else 0
            subject_performance.append({
                'subject': topic,
                'score': avg_score,
                'attempts': stats['count']
            })
            topic_mastery.append({
                'name': topic,
                'value': avg_score,
                'color': colors[i % len(colors)]
            })
        
        # Create performance over time (last 6 data points)
        performance_over_time = []
        recent_performances = performances[-6:] if len(performances) >= 6 else performances
        for i, p in enumerate(recent_performances):
            score_percentage = (p.get('score', 0) / p.get('total_questions', 1)) * 100
            performance_over_time.append({
                'name': f'Quiz {i + 1}',
                'score': round(score_percentage),
                'time': p.get('time_spent', 0)
            })
        
        # Create recent topics
        recent_topics = []
        topic_progress = {}
        for p in performances[-5:]:  # Last 5 performances
            topic = p.get('topic', 'Unknown')
            score_percentage = (p.get('score', 0) / p.get('total_questions', 1)) * 100
            topic_progress[topic] = {
                'name': topic,
                'progress': round(score_percentage),
                'lastStudied': p.get('created_at', 'Recently')
            }
        
        recent_topics = list(topic_progress.values())
        
        # Calculate study streak (simplified)
        study_streak = min(quizzes_completed, 7)  # Cap at 7 days
        
        return {
            "overall_score": overall_score,
            "topics_studied": len(topic_stats),
            "total_time": total_time,
            "quizzes_completed": quizzes_completed,
            "topics_mastered": len([t for t in topic_stats.values() if sum(t['scores'])/len(t['scores']) >= 80]),
            "active_paths": len(topic_stats),
            "recent_activities": performances[-5:] if performances else [],
            "weaknesses": [topic for topic, stats in topic_stats.items() if sum(stats['scores'])/len(stats['scores']) < 60],
            "strengths": [topic for topic, stats in topic_stats.items() if sum(stats['scores'])/len(stats['scores']) >= 80],
            "performance_over_time": performance_over_time,
            "subject_performance": subject_performance,
            "topic_mastery": topic_mastery,
            "weekly_activity": [],  # Would need date-based grouping
            "recent_topics": recent_topics,
            "stats": {
                "completed_quizzes": quizzes_completed,
                "average_score": overall_score,
                "study_streak": study_streak,
                "total_study_time": round(total_time / 3600, 1)  # Convert to hours
            }
        }
        
    except Exception as e:
        print(f"Error getting performance data: {e}")
        return get_empty_performance_data()

def save_quiz_result(user_id, data):
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
        # Extract quiz data from request
        topic = data.get('topic', 'Unknown')
        difficulty = data.get('difficulty', 'medium')
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        time_spent = data.get('time_spent', 0)
        
        # Calculate percentage
        percentage = round((score / total_questions) * 100) if total_questions > 0 else 0
        
        # Save performance record
        performance_record = {
            "user_id": user_id,
            "topic": topic,
            "difficulty": difficulty,
            "score": score,
            "total_questions": total_questions,
            "time_spent": time_spent,
            "created_at": "now()"
        }
        
        result = supabase.table('performance').insert(performance_record).execute()
        
        return {
            "success": True,
            "score": score,
            "percentage": percentage,
            "is_passed": percentage >= 70,
            "record_id": result.data[0]['id'] if result.data else None
        }
        
    except Exception as e:
        print(f"Error saving quiz result: {e}")
        return {
            "success": False,
            "error": str(e)
        }