"""
Vercel serverless function to handle file uploads and AI processing
"""

import os
import json
import tempfile
import PyPDF2
import docx
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for file uploads"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                raise ValueError('Content-Type must be multipart/form-data')
            
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse multipart data
            files, form_data = self._parse_multipart_data(post_data, content_type)
            
            if not files:
                raise ValueError('No files provided')
            
            file_data = files[0]
            filename = form_data.get('filename', ['unknown.txt'])[0]
            
            # Process the file
            result = process_file(file_data, filename)
            
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
                "error": str(e)
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def _parse_multipart_data(self, data, content_type):
        """Simple multipart form data parser"""
        # This is a simplified parser - in production, use a proper library
        boundary = content_type.split('boundary=')[1]
        parts = data.split(f'--{boundary}'.encode())
        
        files = []
        form_data = {}
        
        for part in parts[1:-1]:  # Skip first and last empty parts
            if b'Content-Disposition: form-data' in part:
                # Extract filename
                if b'filename=' in part:
                    # This is a file
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        file_content = part[header_end + 4:]
                        files.append(file_content)
                else:
                    # This is form data
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        field_content = part[header_end + 4:]
                        # Extract field name and value
                        if b'name=' in part:
                            name_start = part.find(b'name="') + 6
                            name_end = part.find(b'"', name_start)
                            field_name = part[name_start:name_end].decode()
                            
                            if field_name not in form_data:
                                form_data[field_name] = []
                            form_data[field_name].append(field_content.decode())
        
        return files, form_data

def process_file(file_data, filename):
    """Process uploaded file and extract content"""
    try:
        # Determine file type
        file_extension = filename.split('.')[-1].lower()
        
        # Extract text content based on file type
        if file_extension == 'pdf':
            content = extract_pdf_content(file_data)
        elif file_extension in ['doc', 'docx']:
            content = extract_docx_content(file_data)
        elif file_extension == 'txt':
            content = file_data.decode('utf-8')
        else:
            raise ValueError(f'Unsupported file type: {file_extension}')
        
        if not content.strip():
            raise ValueError('No content found in file')
        
        # Generate AI analysis
        ai_analysis = analyze_content_with_ai(content, filename)
        
        # Save to database
        material_id = save_material_to_db(filename, content, ai_analysis)
        
        return {
            "success": True,
            "material_id": material_id,
            "filename": filename,
            "content_preview": content[:500] + "..." if len(content) > 500 else content,
            "ai_analysis": ai_analysis,
            "word_count": len(content.split()),
            "char_count": len(content)
        }
        
    except Exception as e:
        print(f"File processing error: {e}")
        raise e

def extract_pdf_content(file_data):
    """Extract text content from PDF"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(file_data)
            temp_file.flush()
            
            # Read PDF content
            with open(temp_file.name, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract PDF content: {str(e)}")

def extract_docx_content(file_data):
    """Extract text content from DOCX"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_file.write(file_data)
            temp_file.flush()
            
            # Read DOCX content
            doc = docx.Document(temp_file.name)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract DOCX content: {str(e)}")

def analyze_content_with_ai(content, filename):
    """Analyze content using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Analyze this educational material: "{filename}"
        
        Content: {content[:2000]}...
        
        Provide a comprehensive analysis in JSON format:
        {{
            "summary": "Brief summary of the content",
            "key_topics": ["topic1", "topic2", "topic3"],
            "difficulty_level": "beginner|intermediate|advanced",
            "subject_category": "mathematics|science|history|etc",
            "learning_objectives": ["objective1", "objective2"],
            "key_concepts": ["concept1", "concept2"],
            "suggested_quiz_questions": [
                {{
                    "question": "Sample question",
                    "difficulty": "easy|medium|hard",
                    "topic": "specific topic"
                }}
            ],
            "study_recommendations": ["recommendation1", "recommendation2"]
        }}
        
        Focus on educational value and learning outcomes.
        """
        
        response = model.generate_content(prompt)
        
        # Try to parse JSON response
        try:
            analysis = json.loads(response.text)
            return analysis
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "summary": response.text[:200] + "...",
                "key_topics": ["General"],
                "difficulty_level": "intermediate",
                "subject_category": "general",
                "learning_objectives": ["Understand the material"],
                "key_concepts": ["Main concepts"],
                "suggested_quiz_questions": [],
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
            "key_concepts": ["Main concepts"],
            "suggested_quiz_questions": [],
            "study_recommendations": ["Review the material thoroughly"]
        }

def save_material_to_db(filename, content, ai_analysis):
    """Save material to Supabase database"""
    if not supabase:
        return "demo-material-id"
    
    try:
        material_data = {
            "filename": filename,
            "content": content,
            "ai_analysis": ai_analysis,
            "word_count": len(content.split()),
            "char_count": len(content),
            "created_at": "now()"
        }
        
        result = supabase.table('study_materials').insert(material_data).execute()
        
        if result.data:
            return result.data[0]['id']
        else:
            return "demo-material-id"
            
    except Exception as e:
        print(f"Database save error: {e}")
        return "demo-material-id"
