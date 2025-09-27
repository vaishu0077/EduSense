"""
Vercel serverless function for AI insights
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
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for AI insights"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            user_id = query_params.get('user_id', [''])[0]
            
            if not user_id:
                raise ValueError('user_id is required')
            
            # Generate mock AI insights
            ai_insights = {
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
                    },
                    {
                        "type": "weakness_alert",
                        "title": "Attention Required",
                        "description": "Science concepts need more practice",
                        "confidence": 0.78,
                        "actionable": True,
                        "recommendation": "Focus on chemistry and physics fundamentals"
                    }
                ],
                "overall_learning_score": 78,
                "next_review_date": "2024-01-15T00:00:00Z",
                "generated_at": "2024-01-01T00:00:00Z"
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(ai_insights).encode('utf-8'))
            
        except Exception as e:
            print(f"AI insights error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "message": "AI insights failed"
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))
