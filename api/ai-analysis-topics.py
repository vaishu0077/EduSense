"""
Vercel serverless function to analyze key topics from material content
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
        """Handle POST requests for topic analysis"""
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
            
            print(f"Analyzing topics for: {filename}")
            
            # Analyze topics
            result = analyze_topics(content, filename)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Topic analysis error: {e}")
            # Return fallback topics
            fallback_result = {
                "success": True,
                "topics": ["Main Concepts", "Key Ideas", "Important Points", "Core Topics"],
                "generated_by": "fallback-system"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(fallback_result).encode('utf-8'))

def analyze_topics(content, filename):
    """Analyze key topics using Gemini AI"""
    try:
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""Analyze this document and extract the key topics:

FILENAME: {filename}
CONTENT: {content[:2000]}...

Return ONLY a JSON array of 4-6 specific topics that are actually discussed in the content:

["Topic 1", "Topic 2", "Topic 3", "Topic 4"]

Requirements:
- Extract topics that are actually mentioned in the content
- Use specific, meaningful topic names
- Return only the JSON array, no additional text
- Focus on the main subjects discussed in the document"""

        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            topics = json.loads(response.text.strip())
            if isinstance(topics, list) and len(topics) > 0:
                return {
                    "success": True,
                    "topics": topics,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Invalid topics format")
        except json.JSONDecodeError:
            # Try to extract array from response
            import re
            array_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
            if array_match:
                topics = json.loads(array_match.group())
                return {
                    "success": True,
                    "topics": topics,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Could not parse topics")
                
    except Exception as e:
        print(f"AI topic analysis error: {e}")
        # Return fallback topics based on content analysis
        content_lower = content.lower()
        
        if 'smart' in content_lower and 'city' in content_lower:
            topics = ["Smart Cities", "Urban Development", "Technology Integration", "Sustainable Development"]
        elif 'energy' in content_lower:
            topics = ["Energy Systems", "Renewable Energy", "Energy Efficiency", "Power Generation"]
        elif 'calculus' in content_lower or 'derivative' in content_lower:
            topics = ["Calculus", "Derivatives", "Integration", "Mathematical Analysis"]
        elif 'war' in content_lower or 'history' in content_lower:
            topics = ["Historical Events", "War Analysis", "Political Context", "Social Impact"]
        else:
            topics = ["Main Concepts", "Key Ideas", "Important Points", "Core Topics"]
        
        return {
            "success": True,
            "topics": topics,
            "generated_by": "fallback-analysis"
        }
