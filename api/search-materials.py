"""
Vercel serverless function to search and filter study materials
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from supabase import create_client, Client

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# Initialize Supabase client
supabase_url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
supabase_key = os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
else:
    supabase = None

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for material search"""
        try:
            # Parse query parameters
            query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            
            search_query = query_params.get('q', [''])[0]
            subject_filter = query_params.get('subject', [''])[0]
            difficulty_filter = query_params.get('difficulty', [''])[0]
            starred_filter = query_params.get('starred', [''])[0]
            sort_by = query_params.get('sort', ['date'])[0]
            sort_order = query_params.get('order', ['desc'])[0]
            limit = int(query_params.get('limit', ['20'])[0])
            offset = int(query_params.get('offset', ['0'])[0])
            
            # Get user ID from headers
            user_id = self.headers.get('X-User-ID', 'demo-user')
            
            # Search materials
            results = search_materials(
                user_id,
                search_query,
                subject_filter,
                difficulty_filter,
                starred_filter,
                sort_by,
                sort_order,
                limit,
                offset
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode('utf-8'))
            
        except Exception as e:
            print(f"Search error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "materials": [],
                "total": 0
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests for advanced search with AI"""
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
            search_query = data.get('query', '')
            search_type = data.get('type', 'semantic')  # 'semantic', 'keyword', 'ai'
            user_id = data.get('user_id', 'demo-user')
            
            # Perform AI-powered search
            results = perform_ai_search(user_id, search_query, search_type)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode('utf-8'))
            
        except Exception as e:
            print(f"AI search error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "materials": [],
                "total": 0
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def search_materials(user_id, search_query, subject_filter, difficulty_filter, starred_filter, sort_by, sort_order, limit, offset):
    """Search materials with filters and sorting"""
    if not supabase:
        # Return demo data when Supabase is not configured
        return get_demo_materials()
    
    try:
        # Build query
        query = supabase.table('study_materials').select('*')
        
        # Apply filters
        if subject_filter:
            query = query.eq('ai_analysis->subject_category', subject_filter)
        
        if difficulty_filter:
            query = query.eq('ai_analysis->difficulty_level', difficulty_filter)
        
        if starred_filter == 'true':
            query = query.eq('starred', True)
        
        # Apply search query
        if search_query:
            # Search in filename and content
            query = query.or_(f'filename.ilike.%{search_query}%,content.ilike.%{search_query}%')
        
        # Apply sorting
        if sort_by == 'name':
            query = query.order('filename', desc=(sort_order == 'desc'))
        elif sort_by == 'date':
            query = query.order('created_at', desc=(sort_order == 'desc'))
        elif sort_by == 'subject':
            query = query.order('ai_analysis->subject_category', desc=(sort_order == 'desc'))
        elif sort_by == 'difficulty':
            query = query.order('ai_analysis->difficulty_level', desc=(sort_order == 'desc'))
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        result = query.execute()
        
        materials = result.data or []
        
        return {
            "success": True,
            "materials": materials,
            "total": len(materials),
            "offset": offset,
            "limit": limit,
            "has_more": len(materials) == limit
        }
        
    except Exception as e:
        print(f"Database search error: {e}")
        return get_demo_materials()

def perform_ai_search(user_id, search_query, search_type):
    """Perform AI-powered semantic search"""
    try:
        # Get all materials first
        if not supabase:
            materials = get_demo_materials()['materials']
        else:
            result = supabase.table('study_materials').select('*').execute()
            materials = result.data or []
        
        if not materials:
            return {
                "success": True,
                "materials": [],
                "total": 0,
                "search_type": search_type
            }
        
        if search_type == 'ai':
            # Use AI to find relevant materials
            relevant_materials = ai_semantic_search(materials, search_query)
        else:
            # Use keyword matching
            relevant_materials = keyword_search(materials, search_query)
        
        return {
            "success": True,
            "materials": relevant_materials,
            "total": len(relevant_materials),
            "search_type": search_type,
            "query": search_query
        }
        
    except Exception as e:
        print(f"AI search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "materials": [],
            "total": 0
        }

def ai_semantic_search(materials, search_query):
    """Use AI to find semantically relevant materials"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create search prompt
        materials_summary = []
        for i, material in enumerate(materials[:10]):  # Limit to first 10 for performance
            summary = {
                "id": material.get('id', i),
                "filename": material.get('filename', ''),
                "summary": material.get('ai_analysis', {}).get('summary', ''),
                "topics": material.get('ai_analysis', {}).get('key_topics', []),
                "subject": material.get('ai_analysis', {}).get('subject_category', ''),
                "difficulty": material.get('ai_analysis', {}).get('difficulty_level', '')
            }
            materials_summary.append(summary)
        
        prompt = f"""
        Find the most relevant study materials for this search query: "{search_query}"
        
        Available materials:
        {json.dumps(materials_summary, indent=2)}
        
        Return a JSON array of material IDs that are most relevant to the search query, ordered by relevance.
        Consider:
        1. Topic relevance
        2. Subject match
        3. Difficulty appropriateness
        4. Content similarity
        
        Return format:
        {{
            "relevant_ids": [1, 3, 5],
            "reasoning": "Brief explanation of why these materials are relevant"
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse AI response
        try:
            ai_result = json.loads(response.text)
            relevant_ids = ai_result.get('relevant_ids', [])
            
            # Filter materials by relevant IDs
            relevant_materials = [m for m in materials if m.get('id') in relevant_ids]
            
            return relevant_materials
            
        except json.JSONDecodeError:
            # Fallback to keyword search
            return keyword_search(materials, search_query)
            
    except Exception as e:
        print(f"AI semantic search error: {e}")
        return keyword_search(materials, search_query)

def keyword_search(materials, search_query):
    """Perform keyword-based search"""
    if not search_query:
        return materials
    
    query_lower = search_query.lower()
    relevant_materials = []
    
    for material in materials:
        score = 0
        
        # Check filename
        if query_lower in material.get('filename', '').lower():
            score += 3
        
        # Check summary
        if query_lower in material.get('ai_analysis', {}).get('summary', '').lower():
            score += 2
        
        # Check topics
        topics = material.get('ai_analysis', {}).get('key_topics', [])
        for topic in topics:
            if query_lower in topic.lower():
                score += 2
        
        # Check subject
        if query_lower in material.get('ai_analysis', {}).get('subject_category', '').lower():
            score += 1
        
        # Check content (first 1000 characters)
        content = material.get('content', '')[:1000].lower()
        if query_lower in content:
            score += 1
        
        if score > 0:
            relevant_materials.append({**material, 'relevance_score': score})
    
    # Sort by relevance score
    relevant_materials.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return relevant_materials

def get_demo_materials():
    """Return demo materials when database is not available"""
    return {
        "success": True,
        "materials": [
            {
                "id": "demo-1",
                "filename": "Calculus Fundamentals.pdf",
                "content": "Calculus is the mathematical study of continuous change...",
                "ai_analysis": {
                    "summary": "Introduction to calculus concepts including derivatives and integrals",
                    "key_topics": ["derivatives", "integrals", "limits"],
                    "subject_category": "mathematics",
                    "difficulty_level": "intermediate"
                },
                "word_count": 1500,
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "demo-2",
                "filename": "World War II History.docx",
                "content": "World War II was a global war that lasted from 1939 to 1945...",
                "ai_analysis": {
                    "summary": "Comprehensive overview of World War II events and impact",
                    "key_topics": ["battles", "politics", "economics"],
                    "subject_category": "history",
                    "difficulty_level": "intermediate"
                },
                "word_count": 2000,
                "created_at": "2024-01-14T15:30:00Z"
            }
        ],
        "total": 2,
        "offset": 0,
        "limit": 20,
        "has_more": False
    }
