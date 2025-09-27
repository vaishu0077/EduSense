"""
AI service for content generation, simplification, and analysis using Gemini 2.0 Flash
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import logging
from app.core.config import settings
from app.core.celery import celery

logger = logging.getLogger(__name__)

# Initialize Gemini client
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class AIService:
    """AI service for various educational tasks"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.temperature = settings.AI_MODEL_TEMPERATURE
        self.max_tokens = settings.MAX_AI_TOKENS
    
    async def generate_quiz(
        self,
        topic: str,
        difficulty_level: str = "medium",
        num_questions: int = 10,
        question_types: Optional[List[str]] = None,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a quiz using AI"""
        try:
            prompt = self._build_quiz_prompt(
                topic, difficulty_level, num_questions, question_types, focus_areas
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            
            quiz_data = json.loads(response.text)
            return quiz_data
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            raise Exception(f"Failed to generate quiz: {str(e)}")
    
    async def simplify_content(
        self,
        content: str,
        target_grade_level: str = "middle school",
        simplification_level: str = "medium"
    ) -> Dict[str, Any]:
        """Simplify educational content using AI"""
        try:
            prompt = self._build_simplification_prompt(content, target_grade_level, simplification_level)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            
            simplified_data = json.loads(response.text)
            return simplified_data
            
        except Exception as e:
            logger.error(f"Error simplifying content: {str(e)}")
            raise Exception(f"Failed to simplify content: {str(e)}")
    
    async def analyze_weaknesses(
        self,
        performance_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze student weaknesses using AI"""
        try:
            prompt = self._build_weakness_analysis_prompt(performance_data, user_profile)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            
            analysis_data = json.loads(response.text)
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error analyzing weaknesses: {str(e)}")
            raise Exception(f"Failed to analyze weaknesses: {str(e)}")
    
    async def generate_learning_path(
        self,
        user_profile: Dict[str, Any],
        weaknesses: List[Dict[str, Any]],
        available_topics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate personalized learning path using AI"""
        try:
            prompt = self._build_learning_path_prompt(user_profile, weaknesses, available_topics)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            
            path_data = json.loads(response.text)
            return path_data
            
        except Exception as e:
            logger.error(f"Error generating learning path: {str(e)}")
            raise Exception(f"Failed to generate learning path: {str(e)}")
    
    async def predict_performance(
        self,
        user_data: Dict[str, Any],
        topic_data: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict student performance using AI"""
        try:
            prompt = self._build_performance_prediction_prompt(user_data, topic_data, historical_performance)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            
            prediction_data = json.loads(response.text)
            return prediction_data
            
        except Exception as e:
            logger.error(f"Error predicting performance: {str(e)}")
            raise Exception(f"Failed to predict performance: {str(e)}")
    
    def _build_quiz_prompt(
        self,
        topic: str,
        difficulty_level: str,
        num_questions: int,
        question_types: Optional[List[str]],
        focus_areas: Optional[List[str]]
    ) -> str:
        """Build prompt for quiz generation"""
        prompt = f"""
        Create a comprehensive quiz on the topic: "{topic}"
        
        Requirements:
        - Difficulty level: {difficulty_level}
        - Number of questions: {num_questions}
        - Question types: {question_types or ['multiple_choice', 'true_false', 'short_answer']}
        - Focus areas: {focus_areas or ['general knowledge']}
        
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
            "questions": [
                {{
                    "question_text": "Question here",
                    "question_type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Explanation here",
                    "difficulty_level": "medium",
                    "points": 1
                }}
            ]
        }}
        """
        return prompt
    
    def _build_simplification_prompt(
        self,
        content: str,
        target_grade_level: str,
        simplification_level: str
    ) -> str:
        """Build prompt for content simplification"""
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
        
        Return as JSON:
        {{
            "simplified_text": "Simplified content here",
            "key_concepts": ["concept1", "concept2"],
            "summary": "Brief summary",
            "vocabulary": {{"word": "definition"}},
            "complexity_reduction": 0.3
        }}
        """
        return prompt
    
    def _build_weakness_analysis_prompt(
        self,
        performance_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> str:
        """Build prompt for weakness analysis"""
        prompt = f"""
        Analyze the following student performance data and identify learning weaknesses:
        
        Performance Data:
        {json.dumps(performance_data, indent=2)}
        
        User Profile:
        {json.dumps(user_profile, indent=2)}
        
        Please identify:
        1. Specific topic weaknesses
        2. Learning pattern issues
        3. Recommended interventions
        4. Priority areas for improvement
        5. Confidence scores for each weakness
        
        Return as JSON:
        {{
            "weaknesses": [
                {{
                    "topic": "topic name",
                    "severity": "high/medium/low",
                    "confidence": 0.85,
                    "description": "Weakness description",
                    "recommendations": ["action1", "action2"]
                }}
            ],
            "overall_analysis": "Overall assessment",
            "priority_actions": ["action1", "action2", "action3"]
        }}
        """
        return prompt
    
    def _build_learning_path_prompt(
        self,
        user_profile: Dict[str, Any],
        weaknesses: List[Dict[str, Any]],
        available_topics: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for learning path generation"""
        prompt = f"""
        Create a personalized learning path for this student:
        
        User Profile:
        {json.dumps(user_profile, indent=2)}
        
        Identified Weaknesses:
        {json.dumps(weaknesses, indent=2)}
        
        Available Topics:
        {json.dumps(available_topics, indent=2)}
        
        Create a learning path that:
        1. Addresses identified weaknesses
        2. Matches learning style and preferences
        3. Provides appropriate difficulty progression
        4. Includes estimated time for each topic
        5. Suggests specific activities and resources
        
        Return as JSON:
        {{
            "title": "Learning Path Title",
            "description": "Path description",
            "estimated_duration": 120,
            "topics_sequence": [
                {{
                    "topic_id": 1,
                    "order": 1,
                    "estimated_time": 30,
                    "focus_areas": ["area1", "area2"],
                    "activities": ["activity1", "activity2"]
                }}
            ],
            "learning_objectives": ["objective1", "objective2"],
            "success_metrics": ["metric1", "metric2"]
        }}
        """
        return prompt
    
    def _build_performance_prediction_prompt(
        self,
        user_data: Dict[str, Any],
        topic_data: Dict[str, Any],
        historical_performance: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for performance prediction"""
        prompt = f"""
        Predict student performance based on the following data:
        
        User Data:
        {json.dumps(user_data, indent=2)}
        
        Topic Data:
        {json.dumps(topic_data, indent=2)}
        
        Historical Performance:
        {json.dumps(historical_performance, indent=2)}
        
        Predict:
        1. Likely performance score (0-100)
        2. Confidence in prediction (0-1)
        3. Risk factors
        4. Success probability
        5. Recommended preparation time
        
        Return as JSON:
        {{
            "predicted_score": 75,
            "confidence": 0.82,
            "risk_factors": ["factor1", "factor2"],
            "success_probability": 0.78,
            "recommended_prep_time": 45,
            "prediction_reasoning": "Explanation of prediction"
        }}
        """
        return prompt

# Celery tasks for background AI processing
@celery.task
def generate_quiz_async(topic, difficulty_level, num_questions, question_types, focus_areas):
    """Async task for quiz generation"""
    ai_service = AIService()
    return ai_service.generate_quiz(topic, difficulty_level, num_questions, question_types, focus_areas)

@celery.task
def simplify_content_async(content, target_grade_level, simplification_level):
    """Async task for content simplification"""
    ai_service = AIService()
    return ai_service.simplify_content(content, target_grade_level, simplification_level)

@celery.task
def analyze_weaknesses_async(performance_data, user_profile):
    """Async task for weakness analysis"""
    ai_service = AIService()
    return ai_service.analyze_weaknesses(performance_data, user_profile)
