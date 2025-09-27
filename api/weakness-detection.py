"""
Vercel serverless function for weakness detection
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
        """Handle GET requests for weakness detection"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            user_id = query_params.get('user_id', [''])[0]
            analysis_type = query_params.get('type', ['comprehensive'])[0]
            
            if not user_id:
                raise ValueError('user_id is required')
            
            # Generate mock weakness analysis
            weakness_analysis = {
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
                "confidence": 0.85,
                "generated_at": "2024-01-01T00:00:00Z"
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(weakness_analysis).encode('utf-8'))
            
        except Exception as e:
            print(f"Weakness detection error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "message": "Weakness detection failed"
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))