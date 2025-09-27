"""
Vercel serverless function to generate quizzes from study materials using AI
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

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
        """Handle POST requests for quiz generation from materials"""
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
            material_content = data.get('content', '')
            material_analysis = data.get('ai_analysis', {})
            num_questions = int(data.get('num_questions', 5))
            difficulty = data.get('difficulty', 'medium')
            focus_topics = data.get('focus_topics', [])
            
            if not material_content.strip():
                raise ValueError("No material content provided")
            
            # Generate quiz from material
            result = generate_quiz_from_material(
                material_content, 
                material_analysis, 
                num_questions, 
                difficulty, 
                focus_topics
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Quiz generation error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "questions": []
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def generate_quiz_from_material(content, analysis, num_questions, difficulty, focus_topics):
    """Generate quiz questions from study material using AI"""
    try:
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build focus topics string
        focus_text = ""
        if focus_topics:
            focus_text = f"\nFocus on these specific topics: {', '.join(focus_topics)}"
        
        # Create comprehensive prompt for quiz generation
        prompt = f"""
        Create a {difficulty} level quiz with {num_questions} multiple choice questions based on this study material.
        
        Study Material Content:
        {content[:3000]}...
        
        Material Analysis:
        - Subject: {analysis.get('subject_category', 'General')}
        - Key Topics: {', '.join(analysis.get('key_topics', []))}
        - Key Concepts: {', '.join(analysis.get('key_concepts', []))}
        - Learning Objectives: {', '.join(analysis.get('learning_objectives', []))}
        {focus_text}
        
        Requirements:
        1. Questions must be directly based on the provided material content
        2. Each question must have exactly 4 options (A, B, C, D)
        3. correct_answer must be the index (0-3) of the correct option
        4. Include detailed explanations for each answer
        5. Ensure questions are appropriate for {difficulty} difficulty level
        6. Cover the most important concepts from the material
        7. Make questions test understanding, not just memorization
        
        Return ONLY a valid JSON object with this exact structure:
        {{
            "quiz_title": "Quiz title based on material",
            "quiz_description": "Brief description of what the quiz covers",
            "questions": [
                {{
                    "question": "Question text here",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Detailed explanation of why this answer is correct",
                    "topic": "Specific topic this question covers",
                    "difficulty": "easy|medium|hard"
                }}
            ]
        }}
        
        Focus on creating questions that test:
        - Understanding of key concepts
        - Application of knowledge
        - Critical thinking about the material
        - Important details and facts
        
        Return only valid JSON, no additional text.
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=3000
            )
        )
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        response_text = response_text.strip()
        
        # Parse the JSON response
        quiz_data = json.loads(response_text)
        
        # Validate the response structure
        if not isinstance(quiz_data, dict) or 'questions' not in quiz_data:
            raise Exception("Invalid response structure from AI")
        
        if not isinstance(quiz_data['questions'], list) or len(quiz_data['questions']) == 0:
            raise Exception("No questions generated by AI")
        
        # Validate each question
        for i, question in enumerate(quiz_data['questions']):
            required_fields = ['question', 'options', 'correct_answer']
            if not all(field in question for field in required_fields):
                raise Exception(f"Missing required fields in question {i+1}")
            
            if not isinstance(question['options'], list) or len(question['options']) != 4:
                raise Exception(f"Question {i+1} must have exactly 4 options")
            
            if not isinstance(question['correct_answer'], int) or question['correct_answer'] not in [0, 1, 2, 3]:
                raise Exception(f"Question {i+1} has invalid correct_answer")
        
        return {
            "success": True,
            "quiz_title": quiz_data.get('quiz_title', 'Material-Based Quiz'),
            "quiz_description": quiz_data.get('quiz_description', 'Quiz generated from study material'),
            "questions": quiz_data['questions'],
            "material_based": True,
            "source_material": {
                "topics": analysis.get('key_topics', []),
                "concepts": analysis.get('key_concepts', []),
                "subject": analysis.get('subject_category', 'General')
            },
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return get_fallback_material_quiz(content, analysis, num_questions, difficulty)
        
    except Exception as e:
        print(f"Quiz generation error: {e}")
        return get_fallback_material_quiz(content, analysis, num_questions, difficulty)

def get_fallback_material_quiz(content, analysis, num_questions, difficulty):
    """Return a fallback quiz when AI generation fails"""
    fallback_questions = []
    
    # Extract key topics and concepts
    topics = analysis.get('key_topics', ['General'])
    concepts = analysis.get('key_concepts', ['Main concepts'])
    subject = analysis.get('subject_category', 'General')
    
    # Create simple questions based on the material
    for i in range(min(num_questions, 5)):
        topic = topics[i % len(topics)] if topics else 'General'
        concept = concepts[i % len(concepts)] if concepts else 'Key concept'
        
        question = {
            "question": f"What is an important aspect of {topic} discussed in this material?",
            "options": [
                f"Understanding {concept}",
                "Memorizing random facts",
                "Ignoring the basics",
                "Skipping practice"
            ],
            "correct_answer": 0,
            "explanation": f"This material focuses on understanding {concept} in {topic}",
            "topic": topic,
            "difficulty": difficulty
        }
        
        fallback_questions.append(question)
    
    return {
        "success": True,
        "quiz_title": f"{subject} Material Quiz",
        "quiz_description": f"Quiz based on {subject} study material",
        "questions": fallback_questions,
        "material_based": True,
        "source_material": {
            "topics": topics,
            "concepts": concepts,
            "subject": subject
        },
        "generated_by": "fallback-system",
        "note": "AI generation failed, using fallback questions"
    }
