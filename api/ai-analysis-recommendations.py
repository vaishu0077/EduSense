"""
Vercel serverless function to analyze study recommendations from material content
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
        """Handle POST requests for study recommendations analysis"""
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
            
            print(f"Analyzing study recommendations for: {filename}")
            
            # Analyze study recommendations
            result = analyze_study_recommendations(content, filename)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Study recommendations analysis error: {e}")
            # Return fallback recommendations
            fallback_result = {
                "success": True,
                "recommendations": [
                    "Read through the material systematically and take detailed notes",
                    "Create concept maps to visualize relationships between topics",
                    "Practice with real-world examples and case studies",
                    "Review and test your understanding with practice questions"
                ],
                "generated_by": "fallback-system"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(fallback_result).encode('utf-8'))

def analyze_study_recommendations(content, filename):
    """Analyze study recommendations using Gemini AI"""
    try:
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""Analyze this document and create specific study recommendations:

FILENAME: {filename}
CONTENT: {content[:2000]}...

Return ONLY a JSON array of 3-4 specific, actionable study recommendations:

["Recommendation 1", "Recommendation 2", "Recommendation 3", "Recommendation 4"]

Requirements:
- Create recommendations based on the actual content
- Make them specific and actionable
- Focus on how to study this material effectively
- Return only the JSON array, no additional text
- Provide practical study strategies for this material"""

        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            recommendations = json.loads(response.text.strip())
            if isinstance(recommendations, list) and len(recommendations) > 0:
                return {
                    "success": True,
                    "recommendations": recommendations,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Invalid recommendations format")
        except json.JSONDecodeError:
            # Try to extract array from response
            import re
            array_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
            if array_match:
                recommendations = json.loads(array_match.group())
                return {
                    "success": True,
                    "recommendations": recommendations,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Could not parse recommendations")
                
    except Exception as e:
        print(f"AI study recommendations analysis error: {e}")
        # Return fallback recommendations based on content analysis
        content_lower = content.lower()
        
        if 'smart' in content_lower and 'city' in content_lower:
            recommendations = [
                "Research real-world smart city implementations and case studies",
                "Create diagrams showing the integration of different smart city technologies",
                "Analyze the benefits and challenges of smart city development",
                "Study the role of data analytics in urban planning"
            ]
        elif 'energy' in content_lower:
            recommendations = [
                "Study different types of renewable energy sources and their efficiency",
                "Analyze energy consumption patterns and optimization strategies",
                "Research the environmental impact of different energy systems",
                "Practice calculating energy efficiency and cost-benefit analysis"
            ]
        elif 'calculus' in content_lower or 'derivative' in content_lower:
            recommendations = [
                "Practice derivative rules with various function types",
                "Work through integration problems step by step",
                "Apply calculus concepts to real-world problems",
                "Create visual representations of rates of change"
            ]
        else:
            recommendations = [
                "Read through the material systematically and take detailed notes",
                "Create concept maps to visualize relationships between topics",
                "Practice with real-world examples and case studies",
                "Review and test your understanding with practice questions"
            ]
        
        return {
            "success": True,
            "recommendations": recommendations,
            "generated_by": "fallback-analysis"
        }
