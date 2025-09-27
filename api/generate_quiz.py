"""
Vercel serverless function to generate AI-powered quizzes using Gemini 2.0 Flash
"""

import os
import json
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def handler(request):
    """Main handler function for Vercel"""
    try:
        # Handle CORS
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': ''
            }
        
        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        # Parse request body
        data = json.loads(request.body)
        
        # Extract parameters
        topic = data.get('topic', 'General Knowledge')
        difficulty = data.get('difficulty', 'medium')
        num_questions = data.get('num_questions', 5)
        
        # Generate quiz
        result = generate_quiz(topic, difficulty, num_questions)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def generate_quiz(topic, difficulty, num_questions):
    """Generate a quiz using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Create a comprehensive quiz on the topic: "{topic}"
        
        Requirements:
        - Difficulty level: {difficulty}
        - Number of questions: {num_questions}
        - Question types: multiple_choice, true_false, short_answer
        - Include educational explanations
        
        For each question, provide:
        1. Question text
        2. Question type
        3. Options (for multiple choice)
        4. Correct answer
        5. Explanation
        6. Difficulty level
        7. Points (1-5)
        
        Return the response as a JSON object with this structure:
        {{
            "title": "Quiz Title",
            "description": "Quiz description",
            "time_limit": 30,
            "questions": [
                {{
                    "id": 1,
                    "question_text": "Question here",
                    "question_type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Explanation here",
                    "difficulty_level": "medium",
                    "points": 1,
                    "hints": ["Hint 1", "Hint 2"]
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        quiz_data = json.loads(response.text)
        
        return {
            "success": True,
            "quiz": quiz_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "quiz": None
        }
