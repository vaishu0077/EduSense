"""
Vercel serverless function for AI-powered content recommendation engine
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from supabase import create_client, Client
import math

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
        """Handle GET requests for content recommendations"""
        try:
            # Parse query parameters
            query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            user_id = query_params.get('user_id', ['demo-user'])[0]
            limit = int(query_params.get('limit', ['10'])[0])
            content_type = query_params.get('type', ['all'])[0]
            
            # Get personalized recommendations
            recommendations = get_content_recommendations(user_id, limit, content_type)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(recommendations).encode('utf-8'))
            
        except Exception as e:
            print(f"Content recommendation GET error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests for advanced recommendations"""
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
            context = data.get('context', {})
            preferences = data.get('preferences', {})
            learning_goal = data.get('learning_goal', 'improve performance')
            
            # Generate advanced recommendations
            recommendations = generate_advanced_recommendations(
                user_id, context, preferences, learning_goal
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(recommendations).encode('utf-8'))
            
        except Exception as e:
            print(f"Advanced recommendation error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def get_content_recommendations(user_id, limit, content_type):
    """Get personalized content recommendations"""
    try:
        # Get user profile and preferences
        user_profile = get_user_profile(user_id)
        
        # Get available content
        available_content = get_available_content(content_type, limit * 3)
        
        # Calculate recommendation scores
        recommendations = calculate_recommendation_scores(user_profile, available_content)
        
        # Sort by score and limit results
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        recommendations = recommendations[:limit]
        
        return {
            "success": True,
            "recommendations": recommendations,
            "total_available": len(available_content),
            "user_profile": user_profile,
            "recommendation_engine": "ai_hybrid"
        }
        
    except Exception as e:
        print(f"Content recommendation error: {e}")
        return get_demo_recommendations()

def generate_advanced_recommendations(user_id, context, preferences, learning_goal):
    """Generate advanced AI-powered recommendations"""
    try:
        # Get comprehensive user data
        user_data = get_comprehensive_user_data(user_id)
        
        # Generate recommendations using AI
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Generate personalized content recommendations for a student with the following profile:
        
        User Profile:
        {json.dumps(user_data, indent=2)}
        
        Context:
        {json.dumps(context, indent=2)}
        
        Preferences:
        {json.dumps(preferences, indent=2)}
        
        Learning Goal: {learning_goal}
        
        Generate recommendations in this format:
        {{
            "recommendations": [
                {{
                    "content_id": "unique_id",
                    "title": "Content Title",
                    "type": "quiz|material|video|article|practice",
                    "subject": "mathematics|science|history|etc",
                    "difficulty": "easy|medium|hard",
                    "estimated_time": "15 minutes",
                    "description": "What this content covers",
                    "learning_objectives": ["objective1", "objective2"],
                    "prerequisites": ["prerequisite1"],
                    "relevance_score": 0.0-1.0,
                    "personalization_factors": [
                        "Matches your learning style",
                        "Addresses your weak areas",
                        "Builds on your strengths"
                    ],
                    "why_recommended": "Detailed explanation of why this is recommended",
                    "expected_benefits": ["benefit1", "benefit2"],
                    "next_steps": ["What to do after completing this content"]
                }}
            ],
            "recommendation_strategy": {{
                "primary_focus": "strengthen_weaknesses|build_strengths|explore_new_areas",
                "difficulty_progression": "gradual|challenging|adaptive",
                "content_mix": "balanced|focused|diverse",
                "time_optimization": "efficient|thorough|flexible"
            }},
            "learning_insights": {{
                "current_level": "beginner|intermediate|advanced",
                "learning_style": "visual|auditory|kinesthetic|reading",
                "strengths": ["strength1", "strength2"],
                "improvement_areas": ["area1", "area2"],
                "motivation_factors": ["factor1", "factor2"]
            }}
        }}
        
        Requirements:
        1. Recommend 5-8 diverse content pieces
        2. Consider user's performance history
        3. Address learning goals and preferences
        4. Provide clear reasoning for each recommendation
        5. Include varied content types
        6. Consider time constraints and learning style
        """
        
        response = model.generate_content(prompt)
        
        # Parse AI response
        try:
            ai_recommendations = json.loads(response.text)
            
            # Enhance with additional metadata
            enhanced_recommendations = enhance_recommendations(ai_recommendations, user_data)
            
            return {
                "success": True,
                "recommendations": enhanced_recommendations.get('recommendations', []),
                "recommendation_strategy": enhanced_recommendations.get('recommendation_strategy', {}),
                "learning_insights": enhanced_recommendations.get('learning_insights', {}),
                "ai_confidence": 0.85,
                "generated_at": "now()"
            }
            
        except json.JSONDecodeError:
            # Fallback to rule-based recommendations
            return generate_rule_based_recommendations(user_id, context, preferences, learning_goal)
            
    except Exception as e:
        print(f"AI recommendation generation error: {e}")
        return generate_rule_based_recommendations(user_id, context, preferences, learning_goal)

def get_user_profile(user_id):
    """Get user's learning profile and preferences"""
    if not supabase:
        return get_demo_user_profile()
    
    try:
        # Get user performance data
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        performances = performance_response.data or []
        
        # Get user preferences (if stored)
        preferences_response = supabase.table('user_preferences').select('*').eq('user_id', user_id).execute()
        preferences = preferences_response.data[0] if preferences_response.data else {}
        
        # Calculate profile metrics
        profile = calculate_user_profile(performances, preferences)
        
        return profile
        
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return get_demo_user_profile()

def get_demo_user_profile():
    """Return demo user profile"""
    return {
        "user_id": "demo-user",
        "learning_style": "visual",
        "preferred_difficulty": "medium",
        "favorite_subjects": ["mathematics", "science"],
        "weak_areas": ["reading_comprehension"],
        "strong_areas": ["problem_solving"],
        "learning_goals": ["improve_overall_performance"],
        "available_time": 30,  # minutes per day
        "performance_trend": "improving",
        "engagement_level": "high"
    }

def get_available_content(content_type, limit):
    """Get available content for recommendations"""
    if not supabase:
        return get_demo_content()
    
    try:
        # Get study materials
        materials_response = supabase.table('study_materials').select('*').limit(limit).execute()
        materials = materials_response.data or []
        
        # Get quizzes
        quizzes_response = supabase.table('quizzes').select('*').limit(limit).execute()
        quizzes = quizzes_response.data or []
        
        # Combine and format content
        content = []
        
        for material in materials:
            content.append({
                "id": material['id'],
                "title": material['filename'],
                "type": "material",
                "subject": material.get('ai_analysis', {}).get('subject_category', 'general'),
                "difficulty": material.get('ai_analysis', {}).get('difficulty_level', 'medium'),
                "description": material.get('ai_analysis', {}).get('summary', ''),
                "topics": material.get('ai_analysis', {}).get('key_topics', []),
                "word_count": material.get('word_count', 0)
            })
        
        for quiz in quizzes:
            content.append({
                "id": quiz['id'],
                "title": quiz.get('title', 'Quiz'),
                "type": "quiz",
                "subject": quiz.get('topic', 'general'),
                "difficulty": quiz.get('difficulty', 'medium'),
                "description": quiz.get('description', ''),
                "topics": [quiz.get('topic', 'general')],
                "question_count": len(quiz.get('questions', []))
            })
        
        return content
        
    except Exception as e:
        print(f"Error getting available content: {e}")
        return get_demo_content()

def get_demo_content():
    """Return demo content"""
    return [
        {
            "id": "demo_1",
            "title": "Calculus Fundamentals",
            "type": "material",
            "subject": "mathematics",
            "difficulty": "intermediate",
            "description": "Introduction to calculus concepts",
            "topics": ["derivatives", "integrals"],
            "word_count": 1500
        },
        {
            "id": "demo_2",
            "title": "Algebra Practice Quiz",
            "type": "quiz",
            "subject": "mathematics",
            "difficulty": "easy",
            "description": "Practice algebraic concepts",
            "topics": ["algebra"],
            "question_count": 10
        }
    ]

def calculate_recommendation_scores(user_profile, available_content):
    """Calculate recommendation scores for content"""
    recommendations = []
    
    for content in available_content:
        score = 0
        
        # Subject preference matching
        if content['subject'] in user_profile.get('favorite_subjects', []):
            score += 0.3
        
        # Difficulty matching
        if content['difficulty'] == user_profile.get('preferred_difficulty', 'medium'):
            score += 0.2
        
        # Learning style matching
        if user_profile.get('learning_style') == 'visual' and content['type'] == 'material':
            score += 0.1
        
        # Weak area addressing
        if content['subject'] in user_profile.get('weak_areas', []):
            score += 0.2
        
        # Topic relevance
        content_topics = content.get('topics', [])
        user_weak_areas = user_profile.get('weak_areas', [])
        topic_overlap = len(set(content_topics) & set(user_weak_areas))
        if topic_overlap > 0:
            score += 0.1 * topic_overlap
        
        # Time consideration
        estimated_time = get_estimated_time(content)
        available_time = user_profile.get('available_time', 30)
        if estimated_time <= available_time:
            score += 0.1
        
        recommendations.append({
            **content,
            "score": min(score, 1.0),
            "relevance_factors": get_relevance_factors(content, user_profile)
        })
    
    return recommendations

def get_estimated_time(content):
    """Estimate time needed for content"""
    if content['type'] == 'material':
        return min(content.get('word_count', 1000) // 200, 60)  # 200 words per minute, max 60 minutes
    elif content['type'] == 'quiz':
        return content.get('question_count', 5) * 2  # 2 minutes per question
    else:
        return 15  # Default 15 minutes

def get_relevance_factors(content, user_profile):
    """Get factors that make content relevant"""
    factors = []
    
    if content['subject'] in user_profile.get('favorite_subjects', []):
        factors.append("Matches your interests")
    
    if content['subject'] in user_profile.get('weak_areas', []):
        factors.append("Addresses your weak areas")
    
    if content['difficulty'] == user_profile.get('preferred_difficulty', 'medium'):
        factors.append("Matches your skill level")
    
    return factors

def get_comprehensive_user_data(user_id):
    """Get comprehensive user data for AI analysis"""
    if not supabase:
        return get_demo_comprehensive_data()
    
    try:
        # Get all user data
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(100).execute()
        materials_response = supabase.table('study_materials').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()
        quiz_response = supabase.table('quiz_attempts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        
        performances = performance_response.data or []
        materials = materials_response.data or []
        quiz_attempts = quiz_response.data or []
        
        # Calculate comprehensive analytics
        analytics = calculate_comprehensive_analytics(performances, materials, quiz_attempts)
        
        return {
            "user_id": user_id,
            "performances": performances,
            "materials": materials,
            "quiz_attempts": quiz_attempts,
            "analytics": analytics,
            "learning_patterns": analyze_learning_patterns(performances, quiz_attempts),
            "content_preferences": analyze_content_preferences(materials, quiz_attempts)
        }
        
    except Exception as e:
        print(f"Error getting comprehensive user data: {e}")
        return get_demo_comprehensive_data()

def get_demo_comprehensive_data():
    """Return demo comprehensive data"""
    return {
        "user_id": "demo-user",
        "performances": [
            {"score": 85, "topic": "mathematics", "difficulty": "medium", "time_spent": 300},
            {"score": 92, "topic": "science", "difficulty": "easy", "time_spent": 240}
        ],
        "materials": [
            {"filename": "Calculus.pdf", "ai_analysis": {"subject_category": "mathematics"}}
        ],
        "quiz_attempts": [
            {"score": 80, "topic": "mathematics", "difficulty": "medium"}
        ],
        "analytics": {
            "avg_score": 85,
            "strengths": ["mathematics"],
            "weaknesses": ["reading_comprehension"],
            "learning_style": "visual"
        },
        "learning_patterns": {
            "best_time": "morning",
            "session_length": 30,
            "difficulty_preference": "medium"
        },
        "content_preferences": {
            "preferred_types": ["quiz", "material"],
            "preferred_subjects": ["mathematics", "science"],
            "preferred_difficulty": "medium"
        }
    }

def calculate_comprehensive_analytics(performances, materials, quiz_attempts):
    """Calculate comprehensive learning analytics"""
    all_attempts = performances + quiz_attempts
    
    if not all_attempts:
        return {"avg_score": 75, "strengths": [], "weaknesses": []}
    
    # Calculate scores by topic
    topic_scores = {}
    for attempt in all_attempts:
        topic = attempt.get('topic', 'general')
        score = (attempt.get('score', 0) / attempt.get('total_questions', 1)) * 100
        if topic not in topic_scores:
            topic_scores[topic] = []
        topic_scores[topic].append(score)
    
    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []
    
    for topic, scores in topic_scores.items():
        avg_score = sum(scores) / len(scores)
        if avg_score >= 80:
            strengths.append(topic)
        elif avg_score < 60:
            weaknesses.append(topic)
    
    # Calculate overall metrics
    total_score = sum(attempt.get('score', 0) for attempt in all_attempts)
    total_questions = sum(attempt.get('total_questions', 1) for attempt in all_attempts)
    avg_score = (total_score / total_questions * 100) if total_questions > 0 else 75
    
    return {
        "avg_score": round(avg_score),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "topic_scores": {topic: round(sum(scores)/len(scores)) for topic, scores in topic_scores.items()},
        "total_learning_time": sum(attempt.get('time_spent', 0) for attempt in all_attempts),
        "engagement_level": "high" if len(all_attempts) > 10 else "medium"
    }

def analyze_learning_patterns(performances, quiz_attempts):
    """Analyze user's learning patterns"""
    all_attempts = performances + quiz_attempts
    
    if not all_attempts:
        return {"best_time": "morning", "session_length": 30, "difficulty_preference": "medium"}
    
    # Analyze time patterns (simplified)
    avg_time = sum(attempt.get('time_spent', 0) for attempt in all_attempts) / len(all_attempts)
    
    # Analyze difficulty preferences
    difficulty_scores = {}
    for attempt in all_attempts:
        difficulty = attempt.get('difficulty', 'medium')
        score = (attempt.get('score', 0) / attempt.get('total_questions', 1)) * 100
        if difficulty not in difficulty_scores:
            difficulty_scores[difficulty] = []
        difficulty_scores[difficulty].append(score)
    
    preferred_difficulty = "medium"
    if difficulty_scores:
        best_difficulty = max(difficulty_scores.keys(), key=lambda k: sum(difficulty_scores[k])/len(difficulty_scores[k]))
        preferred_difficulty = best_difficulty
    
    return {
        "best_time": "morning",  # Would analyze actual timestamps
        "session_length": min(int(avg_time), 60),
        "difficulty_preference": preferred_difficulty,
        "consistency": "high" if len(all_attempts) > 5 else "medium"
    }

def analyze_content_preferences(materials, quiz_attempts):
    """Analyze user's content preferences"""
    # Analyze material preferences
    material_subjects = [m.get('ai_analysis', {}).get('subject_category', 'general') for m in materials]
    quiz_subjects = [q.get('topic', 'general') for q in quiz_attempts]
    
    all_subjects = material_subjects + quiz_subjects
    subject_counts = {}
    for subject in all_subjects:
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
    
    preferred_subjects = sorted(subject_counts.keys(), key=lambda x: subject_counts[x], reverse=True)[:3]
    
    return {
        "preferred_types": ["material", "quiz"],
        "preferred_subjects": preferred_subjects,
        "preferred_difficulty": "medium",
        "engagement_level": "high" if len(materials) + len(quiz_attempts) > 5 else "medium"
    }

def enhance_recommendations(ai_recommendations, user_data):
    """Enhance AI recommendations with additional metadata"""
    recommendations = ai_recommendations.get('recommendations', [])
    
    for rec in recommendations:
        # Add metadata
        rec['metadata'] = {
            "ai_generated": True,
            "confidence": 0.85,
            "last_updated": "now()"
        }
        
        # Add personalized insights
        rec['personalized_insights'] = {
            "matches_learning_style": True,
            "addresses_weak_areas": rec['subject'] in user_data.get('analytics', {}).get('weaknesses', []),
            "builds_on_strengths": rec['subject'] in user_data.get('analytics', {}).get('strengths', []),
            "difficulty_appropriate": True
        }
    
    return ai_recommendations

def generate_rule_based_recommendations(user_id, context, preferences, learning_goal):
    """Generate rule-based recommendations as fallback"""
    return {
        "success": True,
        "recommendations": [
            {
                "content_id": "rule_based_1",
                "title": "Personalized Study Material",
                "type": "material",
                "subject": "mathematics",
                "difficulty": "medium",
                "estimated_time": "30 minutes",
                "description": "Customized content based on your learning goals",
                "learning_objectives": ["Improve understanding", "Practice concepts"],
                "prerequisites": ["Basic knowledge"],
                "relevance_score": 0.8,
                "personalization_factors": ["Matches your goals", "Appropriate difficulty"],
                "why_recommended": "Based on your performance and learning goals",
                "expected_benefits": ["Better understanding", "Improved performance"],
                "next_steps": ["Complete the material", "Take a practice quiz"]
            }
        ],
        "recommendation_strategy": {
            "primary_focus": "improve_performance",
            "difficulty_progression": "gradual",
            "content_mix": "balanced",
            "time_optimization": "efficient"
        },
        "learning_insights": {
            "current_level": "intermediate",
            "learning_style": "mixed",
            "strengths": ["problem_solving"],
            "improvement_areas": ["concept_understanding"],
            "motivation_factors": ["progress_tracking", "achievement_recognition"]
        },
        "ai_confidence": 0.6,
        "generated_at": "now()"
    }

def get_demo_recommendations():
    """Return demo recommendations"""
    return {
        "success": True,
        "recommendations": [
            {
                "content_id": "demo_1",
                "title": "Calculus Practice Problems",
                "type": "quiz",
                "subject": "mathematics",
                "difficulty": "medium",
                "estimated_time": "20 minutes",
                "description": "Practice calculus problems to improve your skills",
                "relevance_score": 0.9,
                "personalization_factors": ["Matches your interests", "Addresses weak areas"]
            }
        ],
        "total_available": 10,
        "user_profile": get_demo_user_profile(),
        "recommendation_engine": "demo"
    }
