"""
Vercel serverless function to generate quiz questions from material content
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
        """Handle POST requests for quiz generation"""
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
            num_questions = int(data.get('num_questions', 5))
            difficulty = data.get('difficulty', 'intermediate')
            topic = data.get('topic', 'General')
            
            print(f"Generating {num_questions} quiz questions for: {filename}")
            
            # Generate quiz questions
            result = generate_quiz_questions(content, filename, num_questions, difficulty, topic)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Quiz generation error: {e}")
            # Return fallback quiz
            fallback_result = {
                "success": True,
                "questions": generate_fallback_questions(data.get('num_questions', 5), data.get('topic', 'General')),
                "generated_by": "fallback-system"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(fallback_result).encode('utf-8'))

def generate_quiz_questions(content, filename, num_questions, difficulty, topic):
    """Generate quiz questions using Gemini AI"""
    try:
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""Create {num_questions} {difficulty} level quiz questions based on this material:

FILENAME: {filename}
TOPIC: {topic}
CONTENT: {content[:2000]}...

Return ONLY a JSON array of quiz questions with this exact structure:
[
  {{
    "question": "Your question here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Why this answer is correct"
  }}
]

Requirements:
- Create questions based on the actual content provided
- Each question must have exactly 4 options
- correct_answer must be 0, 1, 2, or 3 (index of correct option)
- Make questions appropriate for {difficulty} difficulty
- Focus on understanding the material content
- Return only valid JSON, no additional text
- Base questions on the specific content, not generic topics"""

        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            questions = json.loads(response.text.strip())
            if isinstance(questions, list) and len(questions) > 0:
                # Validate each question
                for i, question in enumerate(questions):
                    if not all(field in question for field in ['question', 'options', 'correct_answer']):
                        raise Exception(f"Missing fields in question {i+1}")
                    if not isinstance(question['options'], list) or len(question['options']) != 4:
                        raise Exception(f"Question {i+1} must have exactly 4 options")
                    if not isinstance(question['correct_answer'], int) or question['correct_answer'] not in [0, 1, 2, 3]:
                        raise Exception(f"Question {i+1} has invalid correct_answer")
                
                return {
                    "success": True,
                    "questions": questions,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Invalid questions format")
        except json.JSONDecodeError:
            # Try to extract array from response
            import re
            array_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
            if array_match:
                questions = json.loads(array_match.group())
                return {
                    "success": True,
                    "questions": questions,
                    "generated_by": "gemini-2.0-flash-exp"
                }
            else:
                raise Exception("Could not parse questions")
                
    except Exception as e:
        print(f"AI quiz generation error: {e}")
        # Return fallback questions based on content
        return {
            "success": True,
            "questions": generate_content_based_fallback(content, filename, num_questions, topic),
            "generated_by": "fallback-analysis"
        }

def generate_content_based_fallback(content, filename, num_questions, topic):
    """Generate fallback questions based on content analysis"""
    content_lower = content.lower()
    
    # Generate questions based on content type
    if 'smart' in content_lower and 'city' in content_lower:
        questions = [
            {
                "question": "What is the main focus of smart city development?",
                "options": ["Technology integration", "Population growth", "Economic policies", "Social programs"],
                "correct_answer": 0,
                "explanation": "Smart cities focus on integrating technology to improve urban living"
            },
            {
                "question": "Which technology is most important for smart cities?",
                "options": ["IoT devices", "Traditional infrastructure", "Manual systems", "Paper records"],
                "correct_answer": 0,
                "explanation": "IoT devices are essential for collecting data in smart cities"
            }
        ]
    elif 'energy' in content_lower:
        questions = [
            {
                "question": "What is the primary goal of energy efficiency?",
                "options": ["Reduce consumption", "Increase costs", "Waste energy", "Ignore sustainability"],
                "correct_answer": 0,
                "explanation": "Energy efficiency aims to reduce consumption while maintaining performance"
            },
            {
                "question": "Which is a renewable energy source?",
                "options": ["Solar power", "Coal", "Natural gas", "Oil"],
                "correct_answer": 0,
                "explanation": "Solar power is a renewable energy source that doesn't deplete"
            }
        ]
    elif 'calculus' in content_lower or 'derivative' in content_lower:
        questions = [
            {
                "question": "What does a derivative represent?",
                "options": ["Rate of change", "Total area", "Volume", "Distance"],
                "correct_answer": 0,
                "explanation": "A derivative represents the rate of change of a function"
            },
            {
                "question": "What is the derivative of x²?",
                "options": ["2x", "x", "2", "x²"],
                "correct_answer": 0,
                "explanation": "The derivative of x² is 2x using the power rule"
            }
        ]
    else:
        questions = [
            {
                "question": f"What is the main topic of this {topic} material?",
                "options": ["Core concepts", "Advanced topics", "Basic principles", "Complex theories"],
                "correct_answer": 0,
                "explanation": "The material focuses on core concepts and fundamental understanding"
            },
            {
                "question": f"Which best describes this {topic} content?",
                "options": ["Educational material", "Technical documentation", "Research findings", "Practical guidelines"],
                "correct_answer": 0,
                "explanation": "This is educational material designed for learning"
            }
        ]
    
    # Return the requested number of questions
    return questions[:num_questions]

def generate_fallback_questions(num_questions, topic):
    """Generate basic fallback questions"""
    questions = []
    for i in range(num_questions):
        questions.append({
            "question": f"What is the main focus of this {topic} material? (Question {i+1})",
            "options": ["Core concepts", "Advanced topics", "Basic principles", "Complex theories"],
            "correct_answer": 0,
            "explanation": f"This question tests your understanding of the main topic in question {i+1}"
        })
    return questions
