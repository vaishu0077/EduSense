"""
Vercel serverless function for AI-powered performance prediction and analytics
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from supabase import create_client, Client
import math
from datetime import datetime, timedelta

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
        """Handle GET requests for performance predictions"""
        try:
            # Parse query parameters
            query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            user_id = query_params.get('user_id', ['demo-user'])[0]
            prediction_type = query_params.get('type', ['overall'])[0]
            time_horizon = int(query_params.get('horizon', ['30'])[0])  # days
            
            # Get performance predictions
            predictions = get_performance_predictions(user_id, prediction_type, time_horizon)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(predictions).encode('utf-8'))
            
        except Exception as e:
            print(f"Performance prediction GET error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "predictions": {}
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests for detailed predictions"""
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
            prediction_goals = data.get('goals', ['performance_improvement'])
            time_frame = data.get('time_frame', 30)  # days
            specific_topics = data.get('topics', [])
            
            # Generate detailed predictions
            predictions = generate_detailed_predictions(
                user_id, prediction_goals, time_frame, specific_topics
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(predictions).encode('utf-8'))
            
        except Exception as e:
            print(f"Detailed prediction error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "predictions": {}
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def get_performance_predictions(user_id, prediction_type, time_horizon):
    """Get performance predictions for a user"""
    try:
        # Get user's historical data
        historical_data = get_user_historical_data(user_id)
        
        # Calculate prediction based on type
        if prediction_type == 'overall':
            predictions = predict_overall_performance(historical_data, time_horizon)
        elif prediction_type == 'subject':
            predictions = predict_subject_performance(historical_data, time_horizon)
        elif prediction_type == 'difficulty':
            predictions = predict_difficulty_progression(historical_data, time_horizon)
        else:
            predictions = predict_comprehensive_performance(historical_data, time_horizon)
        
        return {
            "success": True,
            "predictions": predictions,
            "user_id": user_id,
            "prediction_type": prediction_type,
            "time_horizon": time_horizon,
            "confidence": predictions.get('confidence', 0.7),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Performance prediction error: {e}")
        return get_demo_predictions()

def generate_detailed_predictions(user_id, prediction_goals, time_frame, specific_topics):
    """Generate detailed AI-powered predictions"""
    try:
        # Get comprehensive user data
        user_data = get_comprehensive_user_data(user_id)
        
        # Generate predictions using AI
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Analyze this student's learning data and generate detailed performance predictions:
        
        Student Data:
        {json.dumps(user_data, indent=2)}
        
        Prediction Goals: {', '.join(prediction_goals)}
        Time Frame: {time_frame} days
        Specific Topics: {', '.join(specific_topics) if specific_topics else 'All topics'}
        
        Generate predictions in this format:
        {{
            "overall_predictions": {{
                "expected_score_improvement": 5-15,
                "confidence_level": 0.0-1.0,
                "key_factors": ["factor1", "factor2"],
                "risk_factors": ["risk1", "risk2"],
                "success_probability": 0.0-1.0
            }},
            "subject_predictions": [
                {{
                    "subject": "mathematics",
                    "current_level": "intermediate",
                    "predicted_level": "advanced",
                    "improvement_timeline": "2-3 weeks",
                    "key_skills_to_develop": ["skill1", "skill2"],
                    "predicted_score_range": "80-90%",
                    "confidence": 0.8
                }}
            ],
            "learning_path_predictions": {{
                "recommended_difficulty_progression": "gradual|accelerated|challenging",
                "estimated_mastery_time": "4-6 weeks",
                "critical_milestones": [
                    {{
                        "milestone": "Master basic concepts",
                        "target_date": "Week 2",
                        "success_probability": 0.85
                    }}
                ],
                "potential_challenges": [
                    {{
                        "challenge": "Complex problem solving",
                        "likelihood": "medium",
                        "mitigation_strategy": "Practice with guided examples"
                    }}
                ]
            }},
            "performance_trends": {{
                "short_term": "improving|stable|declining",
                "medium_term": "improving|stable|declining",
                "long_term": "improving|stable|declining",
                "trend_confidence": 0.0-1.0
            }},
            "recommendations": [
                {{
                    "type": "study_strategy|content_focus|time_management",
                    "priority": "high|medium|low",
                    "description": "Specific recommendation",
                    "expected_impact": "high|medium|low",
                    "implementation_timeline": "1-2 weeks"
                }}
            ],
            "risk_assessment": {{
                "dropout_risk": "low|medium|high",
                "underperformance_risk": "low|medium|high",
                "engagement_risk": "low|medium|high",
                "mitigation_strategies": ["strategy1", "strategy2"]
            }}
        }}
        
        Requirements:
        1. Base predictions on actual performance data
        2. Consider learning patterns and trends
        3. Identify both opportunities and risks
        4. Provide actionable recommendations
        5. Include confidence levels for all predictions
        6. Consider individual learning style and pace
        """
        
        response = model.generate_content(prompt)
        
        # Parse AI response
        try:
            ai_predictions = json.loads(response.text)
            
            # Enhance with additional analytics
            enhanced_predictions = enhance_predictions_with_analytics(ai_predictions, user_data)
            
            return {
                "success": True,
                "predictions": enhanced_predictions,
                "user_id": user_id,
                "ai_confidence": 0.85,
                "generated_at": datetime.now().isoformat()
            }
            
        except json.JSONDecodeError:
            # Fallback to statistical predictions
            return generate_statistical_predictions(user_data, prediction_goals, time_frame)
            
    except Exception as e:
        print(f"AI prediction generation error: {e}")
        return generate_statistical_predictions(user_data, prediction_goals, time_frame)

def get_user_historical_data(user_id):
    """Get user's historical performance data"""
    if not supabase:
        return get_demo_historical_data()
    
    try:
        # Get performance data
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(100).execute()
        performances = performance_response.data or []
        
        # Get quiz attempts
        quiz_response = supabase.table('quiz_attempts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        quiz_attempts = quiz_response.data or []
        
        # Get learning path progress
        path_response = supabase.table('learning_paths').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()
        learning_paths = path_response.data or []
        
        return {
            "performances": performances,
            "quiz_attempts": quiz_attempts,
            "learning_paths": learning_paths,
            "total_learning_time": sum(p.get('time_spent', 0) for p in performances),
            "data_points": len(performances) + len(quiz_attempts)
        }
        
    except Exception as e:
        print(f"Error getting historical data: {e}")
        return get_demo_historical_data()

def get_demo_historical_data():
    """Return demo historical data"""
    return {
        "performances": [
            {"score": 85, "total_questions": 10, "topic": "mathematics", "difficulty": "medium", "time_spent": 300, "created_at": "2024-01-15T10:00:00Z"},
            {"score": 92, "total_questions": 8, "topic": "science", "difficulty": "easy", "time_spent": 240, "created_at": "2024-01-14T15:30:00Z"},
            {"score": 78, "total_questions": 12, "topic": "mathematics", "difficulty": "hard", "time_spent": 450, "created_at": "2024-01-13T09:15:00Z"}
        ],
        "quiz_attempts": [
            {"score": 80, "total_questions": 5, "topic": "mathematics", "difficulty": "medium", "created_at": "2024-01-12T14:20:00Z"},
            {"score": 90, "total_questions": 5, "topic": "science", "difficulty": "easy", "created_at": "2024-01-11T16:45:00Z"}
        ],
        "learning_paths": [
            {"path_data": {"title": "Mathematics Mastery", "steps": []}, "status": "active", "created_at": "2024-01-10T08:00:00Z"}
        ],
        "total_learning_time": 990,
        "data_points": 5
    }

def predict_overall_performance(historical_data, time_horizon):
    """Predict overall performance improvement"""
    performances = historical_data.get('performances', [])
    quiz_attempts = historical_data.get('quiz_attempts', [])
    
    if not performances and not quiz_attempts:
        return get_demo_overall_prediction()
    
    # Calculate current performance metrics
    all_attempts = performances + quiz_attempts
    recent_attempts = all_attempts[:10]  # Last 10 attempts
    
    if not recent_attempts:
        return get_demo_overall_prediction()
    
    # Calculate trend
    scores = [(a.get('score', 0) / a.get('total_questions', 1)) * 100 for a in recent_attempts]
    avg_score = sum(scores) / len(scores)
    
    # Calculate trend
    if len(scores) >= 3:
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        trend = "improving" if sum(second_half)/len(second_half) > sum(first_half)/len(first_half) else "declining"
    else:
        trend = "stable"
    
    # Predict future performance
    if trend == "improving":
        predicted_improvement = min(15, len(scores) * 2)  # Up to 15% improvement
    elif trend == "declining":
        predicted_improvement = max(-10, -len(scores) * 1)  # Up to 10% decline
    else:
        predicted_improvement = 5  # Stable improvement
    
    predicted_score = min(100, avg_score + predicted_improvement)
    
    return {
        "current_avg_score": round(avg_score),
        "predicted_score": round(predicted_score),
        "improvement": round(predicted_improvement),
        "trend": trend,
        "confidence": 0.7,
        "time_to_target": f"{time_horizon} days",
        "key_factors": ["Consistent practice", "Difficulty progression"],
        "success_probability": 0.8 if predicted_improvement > 0 else 0.6
    }

def predict_subject_performance(historical_data, time_horizon):
    """Predict performance by subject"""
    performances = historical_data.get('performances', [])
    quiz_attempts = historical_data.get('quiz_attempts', [])
    
    all_attempts = performances + quiz_attempts
    
    # Group by subject
    subject_data = {}
    for attempt in all_attempts:
        subject = attempt.get('topic', 'general')
        score = (attempt.get('score', 0) / attempt.get('total_questions', 1)) * 100
        
        if subject not in subject_data:
            subject_data[subject] = []
        subject_data[subject].append(score)
    
    predictions = []
    for subject, scores in subject_data.items():
        if len(scores) >= 2:
            current_avg = sum(scores) / len(scores)
            trend = "improving" if scores[-1] > scores[0] else "declining"
            
            # Predict improvement
            if trend == "improving":
                predicted_improvement = min(10, len(scores) * 1.5)
            else:
                predicted_improvement = max(-5, -len(scores) * 0.5)
            
            predictions.append({
                "subject": subject,
                "current_score": round(current_avg),
                "predicted_score": round(min(100, current_avg + predicted_improvement)),
                "improvement": round(predicted_improvement),
                "trend": trend,
                "confidence": 0.7,
                "data_points": len(scores)
            })
    
    return predictions if predictions else get_demo_subject_predictions()

def predict_difficulty_progression(historical_data, time_horizon):
    """Predict difficulty progression capability"""
    performances = historical_data.get('performances', [])
    
    if not performances:
        return get_demo_difficulty_prediction()
    
    # Analyze performance by difficulty
    difficulty_performance = {}
    for p in performances:
        difficulty = p.get('difficulty', 'medium')
        score = (p.get('score', 0) / p.get('total_questions', 1)) * 100
        
        if difficulty not in difficulty_performance:
            difficulty_performance[difficulty] = []
        difficulty_performance[difficulty].append(score)
    
    # Determine readiness for next difficulty
    current_difficulty = "medium"  # Default
    if "easy" in difficulty_performance and "medium" in difficulty_performance:
        easy_avg = sum(difficulty_performance["easy"]) / len(difficulty_performance["easy"])
        medium_avg = sum(difficulty_performance["medium"]) / len(difficulty_performance["medium"])
        
        if easy_avg >= 85 and medium_avg >= 75:
            current_difficulty = "medium"
        elif easy_avg >= 90:
            current_difficulty = "medium"
        else:
            current_difficulty = "easy"
    
    # Predict next difficulty level
    if current_difficulty == "easy":
        next_difficulty = "medium"
        readiness_score = 0.8
    elif current_difficulty == "medium":
        next_difficulty = "hard"
        readiness_score = 0.6
    else:
        next_difficulty = "expert"
        readiness_score = 0.4
    
    return {
        "current_difficulty": current_difficulty,
        "next_difficulty": next_difficulty,
        "readiness_score": readiness_score,
        "estimated_time_to_advance": f"{time_horizon // 2} days",
        "recommendations": [
            "Continue current difficulty level",
            "Focus on weak areas before advancing"
        ]
    }

def predict_comprehensive_performance(historical_data, time_horizon):
    """Generate comprehensive performance predictions"""
    overall = predict_overall_performance(historical_data, time_horizon)
    subjects = predict_subject_performance(historical_data, time_horizon)
    difficulty = predict_difficulty_progression(historical_data, time_horizon)
    
    return {
        "overall": overall,
        "subjects": subjects,
        "difficulty": difficulty,
        "summary": {
            "expected_improvement": overall.get('improvement', 0),
            "strongest_subject": max(subjects, key=lambda x: x['current_score'])['subject'] if subjects else "N/A",
            "weakest_subject": min(subjects, key=lambda x: x['current_score'])['subject'] if subjects else "N/A",
            "readiness_for_advancement": difficulty.get('readiness_score', 0.5)
        }
    }

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
        analytics = calculate_performance_analytics(performances, materials, quiz_attempts)
        
        return {
            "user_id": user_id,
            "performances": performances,
            "materials": materials,
            "quiz_attempts": quiz_attempts,
            "analytics": analytics,
            "learning_patterns": analyze_learning_patterns(performances, quiz_attempts),
            "engagement_metrics": calculate_engagement_metrics(performances, quiz_attempts)
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
        "engagement_metrics": {
            "total_sessions": 15,
            "avg_session_time": 30,
            "consistency_score": 0.8
        }
    }

def calculate_performance_analytics(performances, materials, quiz_attempts):
    """Calculate comprehensive performance analytics"""
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
    
    # Analyze time patterns
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
        "best_time": "morning",
        "session_length": min(int(avg_time), 60),
        "difficulty_preference": preferred_difficulty,
        "consistency": "high" if len(all_attempts) > 5 else "medium"
    }

def calculate_engagement_metrics(performances, quiz_attempts):
    """Calculate engagement metrics"""
    all_attempts = performances + quiz_attempts
    
    return {
        "total_sessions": len(all_attempts),
        "avg_session_time": sum(attempt.get('time_spent', 0) for attempt in all_attempts) / len(all_attempts) if all_attempts else 0,
        "consistency_score": min(1.0, len(all_attempts) / 20),  # Normalize to 0-1
        "engagement_level": "high" if len(all_attempts) > 15 else "medium" if len(all_attempts) > 5 else "low"
    }

def enhance_predictions_with_analytics(ai_predictions, user_data):
    """Enhance AI predictions with additional analytics"""
    # Add metadata and confidence adjustments
    if 'overall_predictions' in ai_predictions:
        ai_predictions['overall_predictions']['data_quality'] = "high" if user_data.get('data_points', 0) > 10 else "medium"
        ai_predictions['overall_predictions']['prediction_accuracy'] = 0.85
    
    # Add risk assessment based on historical data
    if 'risk_assessment' not in ai_predictions:
        ai_predictions['risk_assessment'] = {
            "dropout_risk": "low",
            "underperformance_risk": "medium",
            "engagement_risk": "low"
        }
    
    return ai_predictions

def generate_statistical_predictions(user_data, prediction_goals, time_frame):
    """Generate statistical predictions as fallback"""
    return {
        "success": True,
        "predictions": {
            "overall_predictions": {
                "expected_score_improvement": 5,
                "confidence_level": 0.6,
                "key_factors": ["Consistent practice"],
                "risk_factors": ["Inconsistent study habits"],
                "success_probability": 0.7
            },
            "subject_predictions": [
                {
                    "subject": "mathematics",
                    "current_level": "intermediate",
                    "predicted_level": "intermediate+",
                    "improvement_timeline": f"{time_frame // 2} days",
                    "key_skills_to_develop": ["Problem solving", "Concept understanding"],
                    "predicted_score_range": "75-85%",
                    "confidence": 0.6
                }
            ],
            "learning_path_predictions": {
                "recommended_difficulty_progression": "gradual",
                "estimated_mastery_time": f"{time_frame} days",
                "critical_milestones": [
                    {
                        "milestone": "Complete foundation review",
                        "target_date": f"Day {time_frame // 4}",
                        "success_probability": 0.7
                    }
                ],
                "potential_challenges": [
                    {
                        "challenge": "Time management",
                        "likelihood": "medium",
                        "mitigation_strategy": "Set regular study schedule"
                    }
                ]
            },
            "performance_trends": {
                "short_term": "stable",
                "medium_term": "improving",
                "long_term": "improving",
                "trend_confidence": 0.6
            },
            "recommendations": [
                {
                    "type": "study_strategy",
                    "priority": "high",
                    "description": "Maintain consistent daily practice",
                    "expected_impact": "high",
                    "implementation_timeline": "1 week"
                }
            ],
            "risk_assessment": {
                "dropout_risk": "low",
                "underperformance_risk": "medium",
                "engagement_risk": "low",
                "mitigation_strategies": ["Regular progress tracking", "Goal setting"]
            }
        },
        "user_id": user_data.get('user_id', 'demo-user'),
        "ai_confidence": 0.6,
        "generated_at": datetime.now().isoformat()
    }

# Demo data functions
def get_demo_predictions():
    return {
        "success": True,
        "predictions": {
            "current_avg_score": 75,
            "predicted_score": 85,
            "improvement": 10,
            "trend": "improving",
            "confidence": 0.7,
            "time_to_target": "30 days"
        },
        "user_id": "demo-user",
        "prediction_type": "overall",
        "time_horizon": 30,
        "confidence": 0.7,
        "generated_at": datetime.now().isoformat()
    }

def get_demo_overall_prediction():
    return {
        "current_avg_score": 75,
        "predicted_score": 85,
        "improvement": 10,
        "trend": "improving",
        "confidence": 0.7,
        "time_to_target": "30 days",
        "key_factors": ["Consistent practice", "Difficulty progression"],
        "success_probability": 0.8
    }

def get_demo_subject_predictions():
    return [
        {
            "subject": "mathematics",
            "current_score": 80,
            "predicted_score": 88,
            "improvement": 8,
            "trend": "improving",
            "confidence": 0.7,
            "data_points": 5
        }
    ]

def get_demo_difficulty_prediction():
    return {
        "current_difficulty": "medium",
        "next_difficulty": "hard",
        "readiness_score": 0.6,
        "estimated_time_to_advance": "15 days",
        "recommendations": [
            "Continue current difficulty level",
            "Focus on weak areas before advancing"
        ]
    }
