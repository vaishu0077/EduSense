#!/usr/bin/env python3
"""
Test script to verify API endpoints are working
"""

import json
import sys
import os

# Add current directory to path to import our API functions
sys.path.append('.')
sys.path.append('./api')

def test_performance_api():
    """Test the performance API"""
    print("🧪 Testing Performance API...")
    print("-" * 40)
    
    try:
        # Import the performance module
        from api.performance import get_performance_data, save_quiz_result
        
        # Test getting performance data
        print("✅ Performance module imported successfully")
        
        # Test with demo user
        result = get_performance_data('demo-user')
        print(f"✅ get_performance_data returned: {type(result)}")
        
        if isinstance(result, dict) and 'stats' in result:
            print("✅ Performance data has correct structure")
        else:
            print("❌ Performance data missing 'stats' key")
            
        # Test saving quiz result
        test_data = {
            'topic': 'Mathematics',
            'difficulty': 'easy',
            'score': 3,
            'total_questions': 5,
            'time_spent': 120
        }
        
        save_result = save_quiz_result('demo-user', test_data)
        print(f"✅ save_quiz_result returned: {type(save_result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance API Error: {e}")
        return False

def test_quiz_api():
    """Test the quiz generation API"""
    print("\n🧪 Testing Quiz Generation API...")
    print("-" * 40)
    
    try:
        # Import the quiz module
        from api.generate_quiz import generate_quiz, get_fallback_quiz
        
        print("✅ Quiz generation module imported successfully")
        
        # Test fallback quiz (should always work)
        fallback_result = get_fallback_quiz('Mathematics', 'easy', 2)
        print(f"✅ get_fallback_quiz returned: {type(fallback_result)}")
        
        if isinstance(fallback_result, dict) and 'questions' in fallback_result:
            print("✅ Fallback quiz has correct structure")
            print(f"   Questions count: {len(fallback_result['questions'])}")
        else:
            print("❌ Fallback quiz missing 'questions' key")
            
        # Test AI quiz generation (might fail without API key)
        try:
            ai_result = generate_quiz('Mathematics', 'easy', 2)
            print(f"✅ generate_quiz returned: {type(ai_result)}")
            
            if ai_result.get('generated_by') == 'fallback-system':
                print("ℹ️  AI generation fell back to fallback system (likely no API key)")
            elif ai_result.get('generated_by') == 'gemini-2.0-flash-exp':
                print("🎉 AI generation working with Gemini!")
            
        except Exception as ai_error:
            print(f"⚠️  AI generation failed (expected without API key): {ai_error}")
            
        return True
        
    except Exception as e:
        print(f"❌ Quiz API Error: {e}")
        return False

def test_request_simulation():
    """Test simulating Vercel request objects"""
    print("\n🧪 Testing Request Simulation...")
    print("-" * 40)
    
    try:
        # Create a mock request object
        class MockRequest:
            def __init__(self, method='GET', body=None, headers=None):
                self.method = method
                self.body = body or {}
                self.headers = headers or {}
        
        # Test performance handler
        from api.performance import handler as perf_handler
        
        mock_request = MockRequest('GET', {}, {'X-User-ID': 'test-user'})
        result = perf_handler(mock_request)
        
        print(f"✅ Performance handler returned status: {result.get('statusCode')}")
        
        if result.get('statusCode') == 200:
            body = json.loads(result.get('body', '{}'))
            if 'stats' in body:
                print("✅ Performance handler returns correct data structure")
            else:
                print("❌ Performance handler missing 'stats' in response")
        
        # Test quiz handler
        from api.generate_quiz import handler as quiz_handler
        
        quiz_request = MockRequest('POST', json.dumps({
            'topic': 'Mathematics',
            'difficulty': 'easy',
            'num_questions': 2
        }), {})
        
        quiz_result = quiz_handler(quiz_request)
        print(f"✅ Quiz handler returned status: {quiz_result.get('statusCode')}")
        
        if quiz_result.get('statusCode') == 200:
            quiz_body = json.loads(quiz_result.get('body', '{}'))
            if 'questions' in quiz_body:
                print("✅ Quiz handler returns correct data structure")
            else:
                print("❌ Quiz handler missing 'questions' in response")
        
        return True
        
    except Exception as e:
        print(f"❌ Request simulation error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 API Testing Suite")
    print("=" * 50)
    
    results = []
    results.append(test_performance_api())
    results.append(test_quiz_api())
    results.append(test_request_simulation())
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All API tests passed!")
        print("Your APIs should work when deployed to Vercel.")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("The APIs might still work on Vercel with proper environment variables.")
