"""
Vercel serverless function to generate personalized learning paths using Gemini 2.0 Flash
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def generate_learning_path(user_profile, weaknesses, available_topics):
    """Generate personalized learning path using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Create a personalized learning path for this student:
        
        User Profile:
        {json.dumps(user_profile, indent=2)}
        
        Identified Weaknesses:
        {json.dumps(weaknesses, indent=2)}
        
        Available Topics:
        {json.dumps(available_topics, indent=2)}
        
        Create a learning path that:
        1. Addresses identified weaknesses
        2. Matches learning style and preferences
        3. Provides appropriate difficulty progression
        4. Includes estimated time for each topic
        5. Suggests specific activities and resources
        6. Sets clear learning objectives
        
        Return as JSON:
        {{
            "title": "Learning Path Title",
            "description": "Path description",
            "estimated_duration": 120,
            "difficulty_progression": "beginner to intermediate",
            "topics_sequence": [
                {{
                    "topic_id": 1,
                    "topic_name": "Topic Name",
                    "order": 1,
                    "estimated_time": 30,
                    "focus_areas": ["area1", "area2"],
                    "activities": ["activity1", "activity2"],
                    "resources": ["resource1", "resource2"],
                    "learning_objectives": ["objective1", "objective2"],
                    "assessment_method": "quiz"
                }}
            ],
            "overall_learning_objectives": ["objective1", "objective2"],
            "success_metrics": ["metric1", "metric2"],
            "recommended_schedule": {{
                "daily_time": 30,
                "weekly_sessions": 5,
                "estimated_completion": "2 weeks"
            }}
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        path_data = json.loads(response.text)
        
        return {
            "success": True,
            "learning_path": path_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "learning_path": None
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            user_profile = data.get('user_profile', {})
            weaknesses = data.get('weaknesses', [])
            available_topics = data.get('available_topics', [])
            
            # Generate learning path
            result = generate_learning_path(user_profile, weaknesses, available_topics)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
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
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
