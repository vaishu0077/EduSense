"""
Vercel serverless function to simplify educational content using Gemini 2.0 Flash
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def simplify_text(content, target_grade_level, simplification_level):
    """Simplify educational content using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Simplify the following educational content for {target_grade_level} students.
        Simplification level: {simplification_level}
        
        Original content:
        {content}
        
        Please provide:
        1. Simplified version of the content
        2. Key concepts extracted
        3. Summary (2-3 sentences)
        4. Vocabulary list with definitions
        5. Complexity reduction percentage
        6. Learning objectives
        
        Return as JSON:
        {{
            "simplified_text": "Simplified content here",
            "key_concepts": ["concept1", "concept2"],
            "summary": "Brief summary",
            "vocabulary": {{"word": "definition"}},
            "complexity_reduction": 0.3,
            "learning_objectives": ["objective1", "objective2"],
            "original_length": 500,
            "simplified_length": 350
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        simplified_data = json.loads(response.text)
        
        return {
            "success": True,
            "data": simplified_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            content = data.get('content', '')
            target_grade_level = data.get('target_grade_level', 'middle school')
            simplification_level = data.get('simplification_level', 'medium')
            
            if not content:
                raise ValueError("Content is required")
            
            # Simplify content
            result = simplify_text(content, target_grade_level, simplification_level)
            
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
