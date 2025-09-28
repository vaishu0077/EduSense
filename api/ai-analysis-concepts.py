"""
Vercel serverless function to analyze key concepts from material content
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
        """Handle POST requests for key concepts analysis"""
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
            
            print(f"Analyzing key concepts for: {filename}")
            
            # Analyze key concepts
            result = analyze_key_concepts(content, filename)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Key concepts analysis error: {e}")
            # Return fallback concepts
            fallback_result = {
                "success": True,
                "concepts": ["Core Principles", "Fundamental Concepts", "Key Ideas", "Main Principles"],
                "generated_by": "fallback-system"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(fallback_result).encode('utf-8'))

def analyze_key_concepts(content, filename):
    """Analyze key concepts using Gemini AI"""
    try:
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""Analyze this document and extract the key concepts:

FILENAME: {filename}
CONTENT: {content[:2000]}...

Return ONLY a JSON array of 3-5 specific key concepts that are central to understanding the material:

["Concept 1", "Concept 2", "Concept 3", "Concept 4"]

Requirements:
- Extract concepts that are fundamental to the material
- Use specific, meaningful concept names
- Return only the JSON array, no additional text
- Focus on the core ideas that students need to understand"""

        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            concepts = json.loads(response.text.strip())
            if isinstance(concepts, list) and len(concepts) > 0:
                return {
                    "success": True,
                    "concepts": concepts,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Invalid concepts format")
        except json.JSONDecodeError:
            # Try to extract array from response
            import re
            array_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
            if array_match:
                concepts = json.loads(array_match.group())
                return {
                    "success": True,
                    "concepts": concepts,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Could not parse concepts")
                
    except Exception as e:
        print(f"AI key concepts analysis error: {e}")
        # Return fallback concepts based on content analysis
        content_lower = content.lower()
        
        if 'smart' in content_lower and 'city' in content_lower:
            concepts = ["Smart City Infrastructure", "IoT Integration", "Data Analytics", "Sustainable Development"]
        elif 'energy' in content_lower:
            concepts = ["Energy Systems", "Renewable Resources", "Energy Efficiency", "Power Distribution"]
        elif 'calculus' in content_lower or 'derivative' in content_lower:
            concepts = ["Derivatives", "Integration", "Limits", "Rate of Change"]
        elif 'war' in content_lower or 'history' in content_lower:
            concepts = ["Historical Context", "Political Factors", "Social Impact", "Economic Consequences"]
        else:
            concepts = ["Core Principles", "Fundamental Concepts", "Key Ideas", "Main Principles"]
        
        return {
            "success": True,
            "concepts": concepts,
            "generated_by": "fallback-analysis"
        }
