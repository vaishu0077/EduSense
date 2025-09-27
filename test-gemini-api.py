#!/usr/bin/env python3
"""
Test script to verify Gemini API is working
Run this to check if your GEMINI_API_KEY is configured correctly
"""

import os
import json
import google.generativeai as genai

def test_gemini_api():
    """Test the Gemini API connection"""
    print("🔧 Testing Gemini API Connection...")
    print("-" * 50)
    
    # Check if API key exists
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("\n💡 To fix this:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Set it in your environment:")
        print("   - Windows: set GEMINI_API_KEY=your_key_here")
        print("   - Mac/Linux: export GEMINI_API_KEY=your_key_here")
        print("3. Or add it to your Vercel environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✅ Model initialized successfully")
        
        # Test simple generation
        print("\n🧪 Testing simple generation...")
        response = model.generate_content("Say 'Hello, EduSense!' if you can hear me.")
        print(f"✅ AI Response: {response.text}")
        
        # Test quiz generation
        print("\n🎯 Testing quiz generation...")
        quiz_prompt = """Create a simple math quiz with 2 questions. Return ONLY valid JSON:
{
  "questions": [
    {
      "question": "What is 5 + 3?",
      "options": ["6", "7", "8", "9"],
      "correct_answer": 2,
      "explanation": "5 + 3 equals 8"
    }
  ]
}"""
        
        quiz_response = model.generate_content(quiz_prompt)
        print(f"✅ Quiz Response: {quiz_response.text[:200]}...")
        
        # Try to parse as JSON
        try:
            json.loads(quiz_response.text)
            print("✅ Quiz response is valid JSON")
        except:
            print("⚠️  Quiz response is not valid JSON (but API is working)")
        
        print("\n🎉 SUCCESS: Gemini API is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\n💡 Common fixes:")
        print("1. Check your API key is correct")
        print("2. Ensure you have internet connection")
        print("3. Verify your Google AI Studio account is active")
        print("4. Try regenerating your API key")
        return False

if __name__ == "__main__":
    test_gemini_api()
