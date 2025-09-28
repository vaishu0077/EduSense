"""
Vercel serverless function to analyze learning objectives from material content
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for learning objectives analysis"""
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
            content = data.get('content', '')
            filename = data.get('filename', 'document')
            
            print(f"Analyzing learning objectives for: {filename}")
            
            # Analyze learning objectives
            result = analyze_learning_objectives(content, filename)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Learning objectives analysis error: {e}")
            # Return fallback objectives
            fallback_result = {
                "success": True,
                "objectives": [
                    "Understand the main concepts presented in the material",
                    "Apply the knowledge to practical scenarios",
                    "Analyze the relationships between different concepts"
                ],
                "generated_by": "fallback-system"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(fallback_result).encode('utf-8'))

def analyze_learning_objectives(content, filename):
    """Analyze learning objectives using Gemini AI"""
    try:
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""Analyze this document and create specific learning objectives:

FILENAME: {filename}
CONTENT: {content[:2000]}...

Return ONLY a JSON array of 3-4 specific, measurable learning objectives:

["Objective 1", "Objective 2", "Objective 3", "Objective 4"]

Requirements:
- Create objectives based on the actual content
- Make them specific and measurable
- Use action verbs like "Understand", "Analyze", "Apply", "Evaluate"
- Return only the JSON array, no additional text
- Focus on what students should learn from this material"""

        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            objectives = json.loads(response.text.strip())
            if isinstance(objectives, list) and len(objectives) > 0:
                return {
                    "success": True,
                    "objectives": objectives,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Invalid objectives format")
        except json.JSONDecodeError:
            # Try to extract array from response
            import re
            array_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
            if array_match:
                objectives = json.loads(array_match.group())
                return {
                    "success": True,
                    "objectives": objectives,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Could not parse objectives")
                
    except Exception as e:
        print(f"AI learning objectives analysis error: {e}")
        # Return fallback objectives based on content analysis
        content_lower = content.lower()
        
        if 'smart' in content_lower and 'city' in content_lower:
            objectives = [
                "Understand the key concepts of smart city development",
                "Analyze the role of technology in urban planning",
                "Evaluate the benefits and challenges of smart city implementation"
            ]
        elif 'energy' in content_lower:
            objectives = [
                "Understand different types of energy systems",
                "Analyze the efficiency of renewable energy sources",
                "Evaluate the environmental impact of energy choices"
            ]
        elif 'calculus' in content_lower or 'derivative' in content_lower:
            objectives = [
                "Understand the fundamental concepts of calculus",
                "Apply derivative rules to solve mathematical problems",
                "Analyze the relationship between derivatives and rates of change"
            ]
        else:
            objectives = [
                "Understand the main concepts presented in the material",
                "Apply the knowledge to practical scenarios",
                "Analyze the relationships between different concepts"
            ]
        
        return {
            "success": True,
            "objectives": objectives,
            "generated_by": "fallback-analysis"
        }
