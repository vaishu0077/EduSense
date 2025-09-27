"""
Vercel serverless function to generate AI-powered quizzes using Gemini 2.0 Flash
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def generate_quiz(topic, difficulty, num_questions):
    """Generate a quiz using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Create a comprehensive quiz on the topic: "{topic}"
        
        Requirements:
        - Difficulty level: {difficulty}
        - Number of questions: {num_questions}
        - Question types: multiple_choice, true_false, short_answer
        - Include educational explanations
        
        For each question, provide:
        1. Question text
        2. Question type
        3. Options (for multiple choice)
        4. Correct answer
        5. Explanation
        6. Difficulty level
        7. Points (1-5)
        
        Return the response as a JSON object with this structure:
        {{
            "title": "Quiz Title",
            "description": "Quiz description",
            "time_limit": 30,
            "questions": [
                {{
                    "id": 1,
                    "question_text": "Question here",
                    "question_type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Explanation here",
                    "difficulty_level": "medium",
                    "points": 1,
                    "hints": ["Hint 1", "Hint 2"]
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        quiz_data = json.loads(response.text)
        
        return {
            "success": True,
            "quiz": quiz_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "quiz": None
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            topic = data.get('topic', 'General Knowledge')
            difficulty = data.get('difficulty', 'medium')
            num_questions = data.get('num_questions', 5)
            
            # Generate quiz
            result = generate_quiz(topic, difficulty, num_questions)
            
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
