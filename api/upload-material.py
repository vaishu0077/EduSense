"""
Vercel serverless function to handle file uploads and AI processing
Simplified version to handle Vercel limitations
"""

import os
import json
import base64
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai
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
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for file uploads"""
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
            filename = data.get('filename', 'unknown.txt')
            file_content = data.get('content', '')
            file_type = data.get('type', 'text')
            user_id = data.get('user_id', 'demo-user')
            
            # Validate file size (1MB limit for Vercel serverless)
            if len(file_content) > 1 * 1024 * 1024:  # 1MB
                raise ValueError('File too large. Maximum size is 1MB for PDF uploads.')
            
            # Process the file
            result = process_file_simple(filename, file_content, file_type, user_id)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Upload error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "message": "Upload failed. Please try a smaller file or check your connection."
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def process_file_simple(filename, content, file_type, user_id):
    """Process uploaded file with simplified approach"""
    try:
        # Validate content
        if not content or not content.strip():
            raise ValueError('No content found in file')
        
        # Limit content length for processing
        max_content_length = 10000  # 10KB limit for AI processing
        if len(content) > max_content_length:
            content = content[:max_content_length] + "... [Content truncated]"
        
        # Generate AI analysis
        ai_analysis = analyze_content_with_ai_simple(content, filename)
        
        # Save to database
        material_id = save_material_to_db_simple(filename, content, ai_analysis, user_id)
        
        return {
            "success": True,
            "material_id": material_id,
            "filename": filename,
            "content_preview": content[:500] + "..." if len(content) > 500 else content,
            "ai_analysis": ai_analysis,
            "word_count": len(content.split()),
            "char_count": len(content),
            "file_type": file_type
        }
        
    except Exception as e:
        print(f"File processing error: {e}")
        raise e

def analyze_content_with_ai_simple(content, filename):
    """Analyze content using Gemini AI with simplified approach"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Analyze this educational material: "{filename}"
        
        Content: {content[:1500]}...
        
        Provide a brief analysis in JSON format:
        {{
            "summary": "Brief summary (2-3 sentences)",
            "key_topics": ["topic1", "topic2"],
            "difficulty_level": "beginner|intermediate|advanced",
            "subject_category": "mathematics|science|history|general",
            "learning_objectives": ["objective1", "objective2"],
            "study_recommendations": ["recommendation1", "recommendation2"]
        }}
        
        Keep responses concise and educational.
        """
        
        response = model.generate_content(prompt)
        
        # Try to parse JSON response
        try:
            analysis = json.loads(response.text)
            return analysis
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "summary": "Educational material uploaded successfully",
                "key_topics": ["General"],
                "difficulty_level": "intermediate",
                "subject_category": "general",
                "learning_objectives": ["Understand the material"],
                "study_recommendations": ["Review the material thoroughly"]
            }
            
    except Exception as e:
        print(f"AI analysis error: {e}")
        return {
            "summary": "Content analysis unavailable",
            "key_topics": ["General"],
            "difficulty_level": "intermediate",
            "subject_category": "general",
            "learning_objectives": ["Understand the material"],
            "study_recommendations": ["Review the material thoroughly"]
        }

def save_material_to_db_simple(filename, content, ai_analysis, user_id):
    """Save material to Supabase database with simplified approach"""
    if not supabase:
        return f"demo-material-{user_id}-{len(filename)}"
    
    try:
        material_data = {
            "user_id": user_id,
            "filename": filename,
            "content": content,
            "ai_analysis": ai_analysis,
            "word_count": len(content.split()),
            "subject_category": ai_analysis.get('subject_category', 'general'),
            "difficulty_level": ai_analysis.get('difficulty_level', 'intermediate'),
            "created_at": "now()"
        }
        
        result = supabase.table('study_materials').insert(material_data).execute()
        
        if result.data:
            return result.data[0]['id']
        else:
            return f"demo-material-{user_id}-{len(filename)}"
            
    except Exception as e:
        print(f"Database save error: {e}")
        return f"demo-material-{user_id}-{len(filename)}"
