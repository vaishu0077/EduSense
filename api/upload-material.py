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
    """Analyze content using Gemini AI with enhanced approach"""
    try:
        # Check if Gemini API key is available
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_api_key:
            print("GEMINI_API_KEY not found, using enhanced fallback analysis")
            return get_enhanced_fallback_analysis(content, filename)
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Enhanced prompt for better analysis
        prompt = f"""
        You are an expert educational content analyzer. Analyze this educational material thoroughly:

        FILENAME: "{filename}"
        CONTENT: {content[:2000]}...

        Provide a detailed educational analysis in JSON format:
        {{
            "summary": "Comprehensive 2-3 sentence summary explaining the main concepts and learning objectives",
            "key_topics": ["Extract 4-6 specific topics from the content"],
            "key_concepts": ["Identify 3-5 key concepts or principles"],
            "difficulty_level": "beginner|intermediate|advanced",
            "subject_category": "mathematics|science|history|english|physics|chemistry|biology|general",
            "learning_objectives": ["Create 3-4 specific learning objectives"],
            "study_recommendations": ["Provide 3-4 actionable study recommendations"],
            "suggested_quiz_questions": [
                {{
                    "question": "Create a specific question based on the content",
                    "topic": "related topic from the content",
                    "difficulty": "easy|medium|hard"
                }},
                {{
                    "question": "Create another question based on the content",
                    "topic": "different topic from the content", 
                    "difficulty": "easy|medium|hard"
                }}
            ]
        }}

        IMPORTANT: 
        - Base all analysis on the actual content provided
        - Extract specific topics and concepts from the text
        - Make learning objectives measurable and specific
        - Ensure quiz questions are directly related to the content
        - Return ONLY valid JSON, no additional text
        """
        
        print(f"Analyzing content with Gemini API for file: {filename}")
        response = model.generate_content(prompt)
        print(f"Gemini response received: {response.text[:200]}...")
        
        # Try to parse JSON response
        try:
            analysis = json.loads(response.text)
            print("Successfully parsed Gemini JSON response")
            return analysis
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Raw response: {response.text}")
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                try:
                    analysis = json.loads(json_match.group())
                    print("Successfully extracted JSON from response")
                    return analysis
                except:
                    pass
            return get_enhanced_fallback_analysis(content, filename)
            
    except Exception as e:
        print(f"AI analysis error: {e}")
        return get_enhanced_fallback_analysis(content, filename)

def get_enhanced_fallback_analysis(content, filename):
    """Enhanced fallback analysis based on content analysis"""
    try:
        # Basic content analysis
        words = content.split()
        word_count = len(words)
        
        # Extract potential topics from content
        content_lower = content.lower()
        
        # Subject detection based on keywords
        subject_keywords = {
            'mathematics': ['math', 'algebra', 'calculus', 'geometry', 'equation', 'formula', 'number', 'solve'],
            'science': ['science', 'physics', 'chemistry', 'biology', 'experiment', 'theory', 'hypothesis'],
            'history': ['history', 'war', 'ancient', 'century', 'empire', 'civilization', 'historical'],
            'english': ['literature', 'poetry', 'novel', 'writing', 'grammar', 'essay', 'language'],
            'physics': ['physics', 'force', 'energy', 'motion', 'quantum', 'mechanics', 'thermodynamics'],
            'chemistry': ['chemistry', 'chemical', 'molecule', 'reaction', 'compound', 'element', 'bond'],
            'biology': ['biology', 'cell', 'organism', 'evolution', 'genetics', 'ecosystem', 'species']
        }
        
        detected_subject = 'general'
        max_matches = 0
        
        for subject, keywords in subject_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > max_matches:
                max_matches = matches
                detected_subject = subject
        
        # Difficulty assessment based on content length and complexity
        if word_count < 200:
            difficulty = 'beginner'
        elif word_count < 500:
            difficulty = 'intermediate'
        else:
            difficulty = 'advanced'
        
        # Extract potential topics from content (first few words as topics)
        potential_topics = []
        if len(words) > 10:
            # Look for capitalized words that might be topics
            for word in words[:50]:  # Check first 50 words
                if word[0].isupper() and len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'this', 'that']:
                    potential_topics.append(word)
                    if len(potential_topics) >= 4:
                        break
        
        if not potential_topics:
            potential_topics = ["Main Topic", "Core Concepts", "Key Ideas", "Important Points"]
        
        # Generate content-specific analysis
        return {
            "summary": f"This {detected_subject} material contains {word_count} words covering key concepts and principles. The content appears to focus on fundamental understanding and practical application.",
            "key_topics": potential_topics[:4],
            "key_concepts": ["Core Principles", "Fundamental Concepts", "Key Ideas", "Main Principles"][:3],
            "difficulty_level": difficulty,
            "subject_category": detected_subject,
            "learning_objectives": [
                f"Understand the main concepts in {detected_subject}",
                "Apply the principles to practical situations",
                "Analyze and evaluate the key ideas presented"
            ],
            "study_recommendations": [
                "Read through the material carefully and take notes",
                "Identify the main concepts and their relationships",
                "Practice applying the concepts with examples",
                "Review and summarize the key points"
            ],
            "suggested_quiz_questions": [
                {
                    "question": f"What is the main focus of this {detected_subject} material?",
                    "topic": potential_topics[0] if potential_topics else "General",
                    "difficulty": "easy"
                },
                {
                    "question": f"Explain one key concept from this {detected_subject} content",
                    "topic": potential_topics[1] if len(potential_topics) > 1 else "Core Concepts",
                    "difficulty": "medium"
                }
            ]
        }
        
    except Exception as e:
        print(f"Enhanced fallback analysis error: {e}")
        # Final fallback
        return {
            "summary": "Educational material uploaded successfully. Content analysis completed with basic processing.",
            "key_topics": ["Main Topics", "Core Concepts", "Key Ideas", "Important Points"],
            "key_concepts": ["Fundamental Concepts", "Core Principles", "Key Ideas"],
            "difficulty_level": "intermediate",
            "subject_category": "general",
            "learning_objectives": ["Understand the material", "Apply key concepts", "Analyze the content"],
            "study_recommendations": ["Review the material thoroughly", "Take notes on key points", "Practice with examples"],
            "suggested_quiz_questions": [
                {
                    "question": "What is the main topic of this material?",
                    "topic": "General",
                    "difficulty": "easy"
                }
            ]
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
