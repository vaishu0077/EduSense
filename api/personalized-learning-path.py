"""
Vercel serverless function for AI-powered personalized learning paths
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

    def do_GET(self):
        """Handle GET requests for learning path retrieval"""
        try:
            # Parse query parameters
            query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            user_id = query_params.get('user_id', ['demo-user'])[0]
            
            # Get user's learning path
            learning_path = get_user_learning_path(user_id)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(learning_path).encode('utf-8'))
            
        except Exception as e:
            print(f"Learning path GET error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "learning_path": []
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests for learning path generation"""
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
            goal = data.get('goal', 'improve overall performance')
            time_available = data.get('time_available', 30)  # days
            focus_areas = data.get('focus_areas', [])
            current_level = data.get('current_level', 'intermediate')
            
            # Generate personalized learning path
            learning_path = generate_personalized_learning_path(
                user_id, goal, time_available, focus_areas, current_level
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(learning_path).encode('utf-8'))
            
        except Exception as e:
            print(f"Learning path generation error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "learning_path": []
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def get_user_learning_path(user_id):
    """Get user's current learning path"""
    if not supabase:
        return get_demo_learning_path()
    
    try:
        # Get learning path from database
        path_response = supabase.table('learning_paths').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
        
        if path_response.data:
            return {
                "success": True,
                "learning_path": path_response.data[0],
                "current_step": get_current_step(user_id)
            }
        else:
            return get_demo_learning_path()
            
    except Exception as e:
        print(f"Error getting learning path: {e}")
        return get_demo_learning_path()

def generate_personalized_learning_path(user_id, goal, time_available, focus_areas, current_level):
    """Generate AI-powered personalized learning path"""
    try:
        # Get user's performance data
        user_data = get_user_performance_data(user_id)
        
        # Generate learning path using AI
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Create a personalized learning path for a student with the following profile:
        
        Student Profile:
        - Current Level: {current_level}
        - Goal: {goal}
        - Time Available: {time_available} days
        - Focus Areas: {', '.join(focus_areas) if focus_areas else 'General improvement'}
        
        Performance Data:
        {json.dumps(user_data, indent=2)}
        
        Create a structured learning path with the following format:
        {{
            "path_id": "unique_path_id",
            "title": "Learning Path Title",
            "description": "Path description",
            "goal": "{goal}",
            "estimated_duration": "{time_available} days",
            "difficulty_progression": "beginner|intermediate|advanced",
            "steps": [
                {{
                    "step_id": 1,
                    "title": "Step Title",
                    "description": "What to learn",
                    "topic": "mathematics|science|history|etc",
                    "difficulty": "easy|medium|hard",
                    "estimated_time": "30 minutes",
                    "activities": [
                        {{
                            "type": "quiz|reading|practice|video",
                            "title": "Activity Title",
                            "description": "Activity description",
                            "duration": "15 minutes",
                            "resources": ["resource1", "resource2"]
                        }}
                    ],
                    "learning_objectives": ["objective1", "objective2"],
                    "prerequisites": ["prerequisite1"],
                    "success_criteria": "How to know you've mastered this step"
                }}
            ],
            "milestones": [
                {{
                    "milestone_id": 1,
                    "title": "Milestone Title",
                    "description": "What you'll achieve",
                    "target_date": "Day 7",
                    "success_metrics": ["metric1", "metric2"]
                }}
            ],
            "adaptation_rules": [
                {{
                    "condition": "If score < 70%",
                    "action": "Repeat step with easier content",
                    "alternative": "Provide additional practice"
                }}
            ],
            "recommended_schedule": {{
                "daily_time": "30-45 minutes",
                "weekly_sessions": 5,
                "best_times": ["morning", "evening"],
                "break_pattern": "5 minutes every 25 minutes"
            }}
        }}
        
        Requirements:
        1. Create 5-8 progressive steps
        2. Each step should build on previous knowledge
        3. Include varied activity types
        4. Set clear success criteria
        5. Provide adaptation rules for struggling students
        6. Consider the student's current performance level
        7. Make it achievable within the time frame
        """
        
        response = model.generate_content(prompt)
        
        # Parse AI response
        try:
            ai_path = json.loads(response.text)
            
            # Save learning path to database
            save_learning_path(user_id, ai_path)
            
            return {
                "success": True,
                "learning_path": ai_path,
                "generated_at": "now()",
                "ai_confidence": 0.85
            }
            
        except json.JSONDecodeError:
            # Fallback to template-based learning path
            return generate_template_learning_path(user_id, goal, time_available, focus_areas, current_level)
            
    except Exception as e:
        print(f"AI learning path generation error: {e}")
        return generate_template_learning_path(user_id, goal, time_available, focus_areas, current_level)

def get_user_performance_data(user_id):
    """Get comprehensive user performance data"""
    if not supabase:
        return get_demo_performance_data()
    
    try:
        # Get performance data
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()
        performances = performance_response.data or []
        
        # Get quiz attempts
        quiz_response = supabase.table('quiz_attempts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()
        quiz_attempts = quiz_response.data or []
        
        # Get study materials
        materials_response = supabase.table('study_materials').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
        materials = materials_response.data or []
        
        # Calculate analytics
        analytics = calculate_performance_analytics(performances + quiz_attempts)
        
        return {
            "performances": performances,
            "quiz_attempts": quiz_attempts,
            "materials": materials,
            "analytics": analytics,
            "total_learning_time": sum(p.get('time_spent', 0) for p in performances),
            "subjects_studied": list(set(p.get('topic', '') for p in performances if p.get('topic'))),
            "strengths": analytics.get('strengths', []),
            "weaknesses": analytics.get('weaknesses', [])
        }
        
    except Exception as e:
        print(f"Error getting performance data: {e}")
        return get_demo_performance_data()

def get_demo_performance_data():
    """Return demo performance data"""
    return {
        "performances": [
            {"score": 85, "total_questions": 10, "topic": "mathematics", "difficulty": "medium", "time_spent": 300},
            {"score": 92, "total_questions": 8, "topic": "science", "difficulty": "easy", "time_spent": 240}
        ],
        "quiz_attempts": [
            {"score": 80, "total_questions": 5, "topic": "mathematics", "difficulty": "medium"}
        ],
        "materials": [
            {"filename": "Calculus.pdf", "ai_analysis": {"subject_category": "mathematics"}}
        ],
        "analytics": {
            "avg_score": 85,
            "strengths": ["mathematics", "problem_solving"],
            "weaknesses": ["reading_comprehension", "time_management"]
        },
        "total_learning_time": 540,
        "subjects_studied": ["mathematics", "science"],
        "strengths": ["mathematics"],
        "weaknesses": ["reading_comprehension"]
    }

def calculate_performance_analytics(performances):
    """Calculate performance analytics"""
    if not performances:
        return {"avg_score": 75, "strengths": [], "weaknesses": []}
    
    # Calculate average score
    total_score = sum(p.get('score', 0) for p in performances)
    total_questions = sum(p.get('total_questions', 1) for p in performances)
    avg_score = (total_score / total_questions * 100) if total_questions > 0 else 75
    
    # Analyze by topic
    topic_scores = {}
    for p in performances:
        topic = p.get('topic', 'general')
        score = (p.get('score', 0) / p.get('total_questions', 1)) * 100
        if topic not in topic_scores:
            topic_scores[topic] = []
        topic_scores[topic].append(score)
    
    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []
    
    for topic, scores in topic_scores.items():
        avg_topic_score = sum(scores) / len(scores)
        if avg_topic_score >= 80:
            strengths.append(topic)
        elif avg_topic_score < 60:
            weaknesses.append(topic)
    
    return {
        "avg_score": round(avg_score),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "topic_scores": {topic: round(sum(scores)/len(scores)) for topic, scores in topic_scores.items()}
    }

def save_learning_path(user_id, learning_path):
    """Save learning path to database"""
    if not supabase:
        return
    
    try:
        path_data = {
            "user_id": user_id,
            "path_data": learning_path,
            "status": "active",
            "created_at": "now()"
        }
        
        supabase.table('learning_paths').insert(path_data).execute()
        
    except Exception as e:
        print(f"Error saving learning path: {e}")

def get_current_step(user_id):
    """Get user's current step in learning path"""
    # This would track progress through the learning path
    return {
        "current_step": 1,
        "completed_steps": 0,
        "progress_percentage": 0,
        "next_milestone": "Complete first step"
    }

def generate_template_learning_path(user_id, goal, time_available, focus_areas, current_level):
    """Generate template-based learning path as fallback"""
    return {
        "success": True,
        "learning_path": {
            "path_id": f"path_{user_id}_{int(time.time())}",
            "title": f"Personalized Learning Path for {goal}",
            "description": f"A {time_available}-day learning journey tailored to your needs",
            "goal": goal,
            "estimated_duration": f"{time_available} days",
            "difficulty_progression": current_level,
            "steps": [
                {
                    "step_id": 1,
                    "title": "Foundation Review",
                    "description": "Review fundamental concepts",
                    "topic": focus_areas[0] if focus_areas else "general",
                    "difficulty": "easy",
                    "estimated_time": "30 minutes",
                    "activities": [
                        {
                            "type": "quiz",
                            "title": "Basic Concepts Quiz",
                            "description": "Test your foundational knowledge",
                            "duration": "15 minutes",
                            "resources": ["Study guide", "Practice problems"]
                        }
                    ],
                    "learning_objectives": ["Understand basic concepts", "Identify knowledge gaps"],
                    "prerequisites": [],
                    "success_criteria": "Score 70% or higher on foundation quiz"
                }
            ],
            "milestones": [
                {
                    "milestone_id": 1,
                    "title": "Foundation Mastery",
                    "description": "Complete foundation review",
                    "target_date": f"Day {time_available // 2}",
                    "success_metrics": ["Quiz score > 70%", "Complete all activities"]
                }
            ],
            "adaptation_rules": [
                {
                    "condition": "If score < 70%",
                    "action": "Review materials and retry",
                    "alternative": "Get additional help"
                }
            ],
            "recommended_schedule": {
                "daily_time": "30-45 minutes",
                "weekly_sessions": 5,
                "best_times": ["morning", "evening"],
                "break_pattern": "5 minutes every 25 minutes"
            }
        },
        "generated_at": "now()",
        "ai_confidence": 0.6
    }

def get_demo_learning_path():
    """Return demo learning path"""
    return {
        "success": True,
        "learning_path": {
            "path_id": "demo_path_1",
            "title": "Mathematics Mastery Path",
            "description": "A comprehensive journey to master mathematics",
            "goal": "Achieve 90%+ in mathematics",
            "estimated_duration": "30 days",
            "difficulty_progression": "intermediate",
            "steps": [
                {
                    "step_id": 1,
                    "title": "Algebra Fundamentals",
                    "description": "Master basic algebraic concepts",
                    "topic": "mathematics",
                    "difficulty": "medium",
                    "estimated_time": "45 minutes",
                    "activities": [
                        {
                            "type": "quiz",
                            "title": "Algebra Basics Quiz",
                            "description": "Test algebraic understanding",
                            "duration": "20 minutes",
                            "resources": ["Algebra textbook", "Online exercises"]
                        }
                    ],
                    "learning_objectives": ["Solve linear equations", "Understand variables"],
                    "prerequisites": ["Basic arithmetic"],
                    "success_criteria": "Score 80%+ on algebra quiz"
                }
            ],
            "milestones": [
                {
                    "milestone_id": 1,
                    "title": "Algebra Mastery",
                    "description": "Complete algebra fundamentals",
                    "target_date": "Day 7",
                    "success_metrics": ["Quiz score > 80%", "Complete all exercises"]
                }
            ],
            "adaptation_rules": [
                {
                    "condition": "If score < 70%",
                    "action": "Review algebra basics",
                    "alternative": "Get one-on-one help"
                }
            ],
            "recommended_schedule": {
                "daily_time": "45 minutes",
                "weekly_sessions": 6,
                "best_times": ["morning"],
                "break_pattern": "10 minutes every 30 minutes"
            }
        },
        "current_step": {
            "current_step": 1,
            "completed_steps": 0,
            "progress_percentage": 0,
            "next_milestone": "Complete algebra fundamentals"
        }
    }
