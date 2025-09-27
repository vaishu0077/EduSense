"""
Consolidated Materials services API
Combines: search-materials, generate-quiz-from-material
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for materials services"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            service = query_params.get('service', ['search'])[0]
            user_id = query_params.get('user_id', [''])[0]
            
            if service == 'search':
                response_data = self.search_materials(user_id, query_params)
            elif service == 'generate-quiz':
                response_data = self.generate_quiz_from_material(user_id, query_params)
            else:
                raise ValueError('Invalid service. Use: search, generate-quiz')
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            print(f"Materials services error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "message": "Materials service failed"
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def search_materials(self, user_id, params):
        """Search and retrieve study materials"""
        search = params.get('search', [''])[0]
        subject = params.get('subject', [''])[0]
        difficulty = params.get('difficulty', [''])[0]
        starred = params.get('starred', [''])[0]
        
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
        
        return {
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

    def generate_quiz_from_material(self, user_id, params):
        """Generate quiz from study material"""
        material_id = params.get('material_id', [''])[0]
        num_questions = int(params.get('num_questions', ['5'])[0])
        difficulty = params.get('difficulty', ['medium'])[0]
        
        if not material_id:
            raise ValueError('material_id is required')
        
        # Generate mock quiz based on material
        questions = []
        for i in range(num_questions):
            questions.append({
                "question": f"Question {i+1} based on material {material_id}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": i % 4,
                "explanation": f"This question tests understanding of key concepts from the material."
            })
        
        return {
            "success": True,
            "quiz": {
                "id": f"quiz-{material_id}-{user_id}",
                "title": f"Quiz from Material {material_id}",
                "description": f"Generated quiz with {num_questions} questions",
                "questions": questions,
                "difficulty": difficulty,
                "num_questions": num_questions,
                "material_id": material_id,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
