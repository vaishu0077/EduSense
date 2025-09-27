"""
Vercel serverless function to generate AI-powered quizzes using Gemini 2.0 Flash
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
            
            # Extract parameters with defaults
            topic = data.get('topic', 'Mathematics')
            difficulty = data.get('difficulty', 'medium')
            num_questions = int(data.get('num_questions', 5))
            
            print(f"Generating quiz: topic={topic}, difficulty={difficulty}, num_questions={num_questions}")
            
            # Generate quiz
            result = generate_quiz(topic, difficulty, num_questions)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Quiz generation error: {e}")
            # Return fallback quiz on any error
            fallback_result = get_fallback_quiz(
                data.get('topic', 'Mathematics'), 
                data.get('difficulty', 'medium'), 
                int(data.get('num_questions', 5))
            )
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(fallback_result).encode('utf-8'))

    def do_GET(self):
        """Handle GET requests - redirect to POST"""
        self.send_response(405)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Use POST method'}).encode('utf-8'))

def generate_quiz(topic, difficulty, num_questions):
    """Generate a quiz using Gemini AI"""
    try:
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Simplified prompt for better reliability
        prompt = f"""Create a {difficulty} level quiz about {topic} with {num_questions} multiple choice questions.

Return ONLY a valid JSON object with this exact structure:
{{
  "questions": [
    {{
      "question": "Your question here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Why this answer is correct"
    }}
  ]
}}

Requirements:
- Each question must have exactly 4 options
- correct_answer must be 0, 1, 2, or 3 (index of correct option)
- Make questions appropriate for {difficulty} difficulty
- Focus on {topic} subject matter
- Return only valid JSON, no additional text"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2000
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
            "questions": quiz_data['questions'],
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return get_fallback_quiz(topic, difficulty, num_questions)
        
    except Exception as e:
        print(f"Quiz generation error: {e}")
        return get_fallback_quiz(topic, difficulty, num_questions)

def get_fallback_quiz(topic, difficulty, num_questions):
    """Return a fallback quiz when AI generation fails"""
    fallback_questions = []
    
    # Create simple fallback questions based on topic
    topic_questions = {
        'mathematics': [
            {
                "question": "What is the result of 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": 1,
                "explanation": "2 + 2 equals 4"
            },
            {
                "question": "What is 10 ÷ 2?",
                "options": ["4", "5", "6", "7"],
                "correct_answer": 1,
                "explanation": "10 divided by 2 equals 5"
            },
            {
                "question": "What is 3 × 4?",
                "options": ["10", "11", "12", "13"],
                "correct_answer": 2,
                "explanation": "3 multiplied by 4 equals 12"
            }
        ],
        'science': [
            {
                "question": "What is the chemical symbol for water?",
                "options": ["H2O", "CO2", "NaCl", "O2"],
                "correct_answer": 0,
                "explanation": "Water is H2O - two hydrogen atoms and one oxygen atom"
            },
            {
                "question": "How many planets are in our solar system?",
                "options": ["7", "8", "9", "10"],
                "correct_answer": 1,
                "explanation": "There are 8 planets in our solar system"
            },
            {
                "question": "What gas do plants absorb during photosynthesis?",
                "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
                "correct_answer": 1,
                "explanation": "Plants absorb carbon dioxide during photosynthesis"
            }
        ],
        'history': [
            {
                "question": "In which year did World War II end?",
                "options": ["1944", "1945", "1946", "1947"],
                "correct_answer": 1,
                "explanation": "World War II ended in 1945"
            },
            {
                "question": "Who was the first President of the United States?",
                "options": ["Thomas Jefferson", "George Washington", "John Adams", "Benjamin Franklin"],
                "correct_answer": 1,
                "explanation": "George Washington was the first President of the United States"
            }
        ]
    }
    
    # Get questions for the topic or use generic ones
    topic_lower = topic.lower()
    if topic_lower in topic_questions:
        available_questions = topic_questions[topic_lower]
    else:
        # Generic questions
        available_questions = [
            {
                "question": f"What is an important concept in {topic}?",
                "options": [
                    f"Understanding {topic} fundamentals",
                    "Memorizing random facts",
                    "Ignoring the basics",
                    "Skipping practice"
                ],
                "correct_answer": 0,
                "explanation": f"Understanding fundamentals is key to learning {topic}"
            },
            {
                "question": f"How can you improve your {topic} skills?",
                "options": [
                    "Never practicing",
                    "Regular study and practice",
                    "Avoiding difficult problems",
                    "Only reading theory"
                ],
                "correct_answer": 1,
                "explanation": f"Regular study and practice are essential for improving {topic} skills"
            }
        ]
    
    # Select questions up to the requested number
    for i in range(min(num_questions, len(available_questions))):
        fallback_questions.append(available_questions[i])
    
    # If we need more questions, repeat the available ones
    while len(fallback_questions) < num_questions and available_questions:
        fallback_questions.append(available_questions[len(fallback_questions) % len(available_questions)])
    
    return {
        "success": True,
        "questions": fallback_questions,
        "generated_by": "fallback-system",
        "note": "AI generation failed, using fallback questions"
    }