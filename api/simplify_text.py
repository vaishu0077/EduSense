"""
Vercel serverless function to simplify educational content using Gemini 2.0 Flash
"""

import os
import json
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def simplify_text(content, target_grade_level, simplification_level):
    """Simplify educational content using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Simplify the following educational content for {target_grade_level} students.
        Simplification level: {simplification_level}
        
        Original content:
        {content}
        
        Please provide:
        1. Simplified version of the content
        2. Key concepts extracted
        3. Summary (2-3 sentences)
        4. Vocabulary list with definitions
        5. Complexity reduction percentage
        6. Learning objectives
        
        Return as JSON:
        {{
            "simplified_text": "Simplified content here",
            "key_concepts": ["concept1", "concept2"],
            "summary": "Brief summary",
            "vocabulary": {{"word": "definition"}},
            "complexity_reduction": 0.3,
            "learning_objectives": ["objective1", "objective2"],
            "original_length": 500,
            "simplified_length": 350
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        simplified_data = json.loads(response.text)
        
        return {
            "success": True,
            "data": simplified_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

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
        content = data.get('content', '')
        target_grade_level = data.get('target_grade_level', 'middle school')
        simplification_level = data.get('simplification_level', 'medium')
        
        if not content:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Content is required'})
            }
        
        # Simplify content
        result = simplify_text(content, target_grade_level, simplification_level)
        
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
