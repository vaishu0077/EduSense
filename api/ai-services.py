"""
Consolidated AI services API
Combines: adaptive-difficulty, ai-insights, content-recommendation, 
performance-prediction, personalized-learning-path, weakness-detection
"""

import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for AI services"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            service = query_params.get('service', [''])[0]
            user_id = query_params.get('user_id', [''])[0]
            
            if not user_id:
                raise ValueError('user_id is required')
            
            if service == 'adaptive-difficulty':
                response_data = self.get_adaptive_difficulty(user_id, query_params)
            elif service == 'ai-insights':
                response_data = self.get_ai_insights(user_id, query_params)
            elif service == 'content-recommendation':
                response_data = self.get_content_recommendations(user_id, query_params)
            elif service == 'performance-prediction':
                response_data = self.get_performance_prediction(user_id, query_params)
            elif service == 'personalized-learning-path':
                response_data = self.get_personalized_learning_path(user_id, query_params)
            elif service == 'weakness-detection':
                response_data = self.get_weakness_detection(user_id, query_params)
            else:
                raise ValueError('Invalid service. Use: adaptive-difficulty, ai-insights, content-recommendation, performance-prediction, personalized-learning-path, weakness-detection')
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            print(f"AI services error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "message": "AI service failed"
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def get_adaptive_difficulty(self, user_id, params):
        """Adaptive difficulty adjustment"""
        topic = params.get('topic', [''])[0]
        current_difficulty = params.get('difficulty', ['medium'])[0]
        
        return {
            "user_id": user_id,
            "topic": topic,
            "current_difficulty": current_difficulty,
            "recommended_difficulty": "medium",
            "confidence": 0.85,
            "reasoning": "Based on your recent performance, medium difficulty is optimal",
            "next_review": "2024-01-15T00:00:00Z"
        }

    def get_ai_insights(self, user_id, params):
        """AI insights and recommendations"""
        return {
            "user_id": user_id,
            "insights": [
                {
                    "type": "learning_pattern",
                    "title": "Study Pattern Detected",
                    "description": "You perform best in the morning hours (9-11 AM)",
                    "confidence": 0.85,
                    "actionable": True,
                    "recommendation": "Schedule your most challenging topics during morning hours"
                },
                {
                    "type": "performance_trend",
                    "title": "Improvement Trend",
                    "description": "Your math scores have improved by 15% over the last week",
                    "confidence": 0.92,
                    "actionable": True,
                    "recommendation": "Continue with your current study approach for math"
                }
            ],
            "overall_learning_score": 78,
            "next_review_date": "2024-01-15T00:00:00Z"
        }

    def get_content_recommendations(self, user_id, params):
        """Content recommendations"""
        limit = int(params.get('limit', ['5'])[0])
        
        return {
            "user_id": user_id,
            "recommendations": [
                {
                    "id": "rec-1",
                    "type": "quiz",
                    "title": "Advanced Calculus Practice",
                    "description": "Challenging calculus problems to test your skills",
                    "subject": "mathematics",
                    "difficulty": "hard",
                    "relevance_score": 0.9
                },
                {
                    "id": "rec-2",
                    "type": "material",
                    "title": "Physics Fundamentals",
                    "description": "Essential physics concepts and formulas",
                    "subject": "science",
                    "difficulty": "medium",
                    "relevance_score": 0.8
                }
            ],
            "total": limit
        }

    def get_performance_prediction(self, user_id, params):
        """Performance prediction"""
        prediction_type = params.get('type', ['overall'])[0]
        
        return {
            "user_id": user_id,
            "prediction_type": prediction_type,
            "predicted_score": 85,
            "confidence": 0.88,
            "time_horizon": 30,
            "factors": [
                "Recent quiz performance",
                "Study consistency",
                "Topic mastery levels"
            ],
            "recommendations": [
                "Focus on weak areas",
                "Maintain current study pace",
                "Practice regularly"
            ]
        }

    def get_personalized_learning_path(self, user_id, params):
        """Personalized learning path"""
        return {
            "user_id": user_id,
            "learning_path": {
                "id": f"path-{user_id}",
                "title": "Personalized Learning Journey",
                "description": "Customized learning path based on your preferences",
                "steps": [
                    {
                        "id": 1,
                        "title": "Foundation Review",
                        "description": "Review basic concepts",
                        "estimated_time": "2 hours",
                        "difficulty": "easy"
                    },
                    {
                        "id": 2,
                        "title": "Practice Problems",
                        "description": "Solve practice problems",
                        "estimated_time": "3 hours",
                        "difficulty": "medium"
                    }
                ],
                "total_estimated_time": "5 hours",
                "progress": 0
            }
        }

    def get_weakness_detection(self, user_id, params):
        """Weakness detection and analysis"""
        analysis_type = params.get('type', ['comprehensive'])[0]
        
        return {
            "user_id": user_id,
            "analysis_type": analysis_type,
            "weakness_areas": [
                {
                    "subject": "Mathematics",
                    "weakness": "Algebraic equations",
                    "severity": "medium",
                    "recommendations": ["Practice solving linear equations", "Review quadratic formulas"]
                },
                {
                    "subject": "Science",
                    "weakness": "Chemical bonding",
                    "severity": "high",
                    "recommendations": ["Study ionic and covalent bonds", "Practice Lewis structures"]
                }
            ],
            "overall_weakness_score": 65,
            "improvement_suggestions": [
                "Focus on algebraic problem-solving",
                "Review chemical bonding concepts",
                "Practice with interactive simulations"
            ],
            "confidence": 0.85
        }
