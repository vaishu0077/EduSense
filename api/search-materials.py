"""
Vercel serverless function for searching and retrieving study materials
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
        """Handle GET requests for searching materials"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            user_id = query_params.get('user_id', [''])[0]
            search = query_params.get('search', [''])[0]
            subject = query_params.get('subject', [''])[0]
            difficulty = query_params.get('difficulty', [''])[0]
            starred = query_params.get('starred', [''])[0]
            
            # Generate mock materials data
            mock_materials = [
                {
                    "id": "demo-material-1",
                    "filename": "Calculus Fundamentals.pdf",
                    "file_type": "application/pdf",
                    "file_size": 1024000,
                    "content": "Calculus is the mathematical study of continuous change...",
                    "ai_analysis": {
                        "summary": "Introduction to calculus concepts including derivatives and integrals",
                        "key_topics": ["derivatives", "integrals", "limits", "continuity"],
                        "subject_category": "mathematics",
                        "difficulty_level": "intermediate",
                        "learning_objectives": ["Understand derivatives", "Master integration techniques"],
                        "study_recommendations": ["Practice derivative rules", "Work through integration examples"]
                    },
                    "word_count": 150,
                    "char_count": 850,
                    "starred": False,
                    "tags": ["mathematics", "calculus", "derivatives"],
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "demo-material-2",
                    "filename": "World War II History.docx",
                    "file_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "file_size": 2048000,
                    "content": "World War II was a global war that lasted from 1939 to 1945...",
                    "ai_analysis": {
                        "summary": "Comprehensive overview of World War II events and impact",
                        "key_topics": ["battles", "politics", "economics", "technology"],
                        "subject_category": "history",
                        "difficulty_level": "intermediate",
                        "learning_objectives": ["Understand war causes", "Analyze war impact"],
                        "study_recommendations": ["Study timeline of events", "Analyze causes and effects"]
                    },
                    "word_count": 200,
                    "char_count": 1200,
                    "starred": True,
                    "tags": ["history", "world-war-ii", "politics"],
                    "created_at": "2024-01-02T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z"
                }
            ]
            
            # Filter materials based on search criteria
            filtered_materials = mock_materials
            
            if search:
                filtered_materials = [
                    m for m in filtered_materials 
                    if search.lower() in m['filename'].lower() or 
                       search.lower() in m['content'].lower()
                ]
            
            if subject:
                filtered_materials = [
                    m for m in filtered_materials 
                    if m['ai_analysis'].get('subject_category', '').lower() == subject.lower()
                ]
            
            if difficulty:
                filtered_materials = [
                    m for m in filtered_materials 
                    if m['ai_analysis'].get('difficulty_level', '').lower() == difficulty.lower()
                ]
            
            if starred == 'true':
                filtered_materials = [
                    m for m in filtered_materials 
                    if m['starred'] == True
                ]
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                "success": True,
                "materials": filtered_materials,
                "total": len(filtered_materials),
                "filters": {
                    "search": search,
                    "subject": subject,
                    "difficulty": difficulty,
                    "starred": starred
                }
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            print(f"Search materials error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "message": "Failed to search materials"
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))