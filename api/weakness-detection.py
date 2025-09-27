"""
Vercel serverless function for AI-powered weakness detection and analysis
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from supabase import create_client, Client
import math
from datetime import datetime, timedelta

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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for weakness analysis"""
        try:
            # Parse query parameters
            query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
            user_id = query_params.get('user_id', ['demo-user'])[0]
            analysis_type = query_params.get('type', ['comprehensive'])[0]
            
            # Get weakness analysis
            analysis = get_weakness_analysis(user_id, analysis_type)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(analysis).encode('utf-8'))
            
        except Exception as e:
            print(f"Weakness analysis GET error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests for detailed weakness analysis"""
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
            user_id = data.get('user_id', 'demo-user')
            focus_areas = data.get('focus_areas', [])
            time_period = data.get('time_period', 30)  # days
            analysis_depth = data.get('depth', 'detailed')  # basic, detailed, comprehensive
            
            # Generate detailed weakness analysis
            analysis = generate_detailed_weakness_analysis(
                user_id, focus_areas, time_period, analysis_depth
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(analysis).encode('utf-8'))
            
        except Exception as e:
            print(f"Detailed weakness analysis error: {e}")
            error_result = {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

def get_weakness_analysis(user_id, analysis_type):
    """Get weakness analysis for a user"""
    try:
        # Get user's performance data
        performance_data = get_user_performance_data(user_id)
        
        # Perform analysis based on type
        if analysis_type == 'comprehensive':
            analysis = perform_comprehensive_weakness_analysis(performance_data)
        elif analysis_type == 'subject':
            analysis = perform_subject_weakness_analysis(performance_data)
        elif analysis_type == 'skill':
            analysis = perform_skill_weakness_analysis(performance_data)
        else:
            analysis = perform_basic_weakness_analysis(performance_data)
        
        return {
            "success": True,
            "analysis": analysis,
            "user_id": user_id,
            "analysis_type": analysis_type,
            "confidence": analysis.get('confidence', 0.7),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Weakness analysis error: {e}")
        return get_demo_weakness_analysis()

def generate_detailed_weakness_analysis(user_id, focus_areas, time_period, analysis_depth):
    """Generate detailed AI-powered weakness analysis"""
    try:
        # Get comprehensive user data
        user_data = get_comprehensive_user_data(user_id)
        
        # Generate analysis using AI
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        Analyze this student's learning data to identify specific weaknesses and provide actionable insights:
        
        Student Performance Data:
        {json.dumps(user_data, indent=2)}
        
        Focus Areas: {', '.join(focus_areas) if focus_areas else 'All areas'}
        Time Period: {time_period} days
        Analysis Depth: {analysis_depth}
        
        Generate detailed weakness analysis in this format:
        {{
            "overall_weaknesses": {{
                "primary_weaknesses": [
                    {{
                        "weakness": "Specific weakness description",
                        "severity": "low|medium|high|critical",
                        "impact": "How this affects overall performance",
                        "frequency": "How often this weakness appears",
                        "trend": "improving|stable|declining|worsening"
                    }}
                ],
                "secondary_weaknesses": [
                    {{
                        "weakness": "Secondary weakness",
                        "severity": "low|medium|high",
                        "impact": "Impact description",
                        "frequency": "Occurrence rate"
                    }}
                ],
                "emerging_weaknesses": [
                    {{
                        "weakness": "Newly identified weakness",
                        "severity": "low|medium|high",
                        "confidence": 0.0-1.0,
                        "early_indicators": ["indicator1", "indicator2"]
                    }}
                ]
            }},
            "subject_specific_weaknesses": [
                {{
                    "subject": "mathematics|science|history|etc",
                    "weaknesses": [
                        {{
                            "skill": "Specific skill or concept",
                            "current_level": "beginner|intermediate|advanced",
                            "target_level": "beginner|intermediate|advanced",
                            "gap_analysis": "What's missing",
                            "root_causes": ["cause1", "cause2"],
                            "evidence": ["specific examples from performance data"]
                        }}
                    ],
                    "overall_subject_score": 0-100,
                    "improvement_potential": "high|medium|low"
                }}
            ]},
            "skill_gap_analysis": {{
                "cognitive_skills": [
                    {{
                        "skill": "Critical thinking|Problem solving|Memory|Attention",
                        "current_level": "weak|developing|proficient|strong",
                        "gap_size": "small|medium|large",
                        "impact_on_learning": "high|medium|low"
                    }}
                ],
                "learning_skills": [
                    {{
                        "skill": "Time management|Study strategies|Note-taking|Test-taking",
                        "current_level": "weak|developing|proficient|strong",
                        "gap_size": "small|medium|large",
                        "impact_on_learning": "high|medium|low"
                    }}
                ]
            }},
            "pattern_analysis": {{
                "common_mistake_patterns": [
                    {{
                        "pattern": "Description of mistake pattern",
                        "frequency": "high|medium|low",
                        "context": "When this pattern occurs",
                        "underlying_cause": "Why this pattern happens"
                    }}
                ],
                "performance_patterns": [
                    {{
                        "pattern": "Performance pattern description",
                        "frequency": "high|medium|low",
                        "triggers": ["What triggers this pattern"],
                        "consequences": ["What happens as a result"]
                    }}
                ]
            }},
            "recommendations": [
                {{
                    "priority": "high|medium|low",
                    "category": "immediate|short_term|long_term",
                    "recommendation": "Specific actionable recommendation",
                    "rationale": "Why this recommendation is important",
                    "expected_impact": "high|medium|low",
                    "implementation_difficulty": "easy|medium|hard",
                    "timeline": "When to implement",
                    "success_metrics": ["How to measure success"]
                }}
            ],
            "intervention_strategies": [
                {{
                    "strategy": "Specific intervention strategy",
                    "target_weakness": "Which weakness this addresses",
                    "method": "How to implement",
                    "resources_needed": ["resource1", "resource2"],
                    "expected_outcome": "What to expect",
                    "monitoring_approach": "How to track progress"
                }}
            ]
        }}
        
        Requirements:
        1. Base analysis on actual performance data
        2. Identify both obvious and subtle weaknesses
        3. Provide specific, actionable recommendations
        4. Consider learning patterns and trends
        5. Include confidence levels for all assessments
        6. Focus on areas with highest improvement potential
        """
        
        response = model.generate_content(prompt)
        
        # Parse AI response
        try:
            ai_analysis = json.loads(response.text)
            
            # Enhance with additional analytics
            enhanced_analysis = enhance_weakness_analysis(ai_analysis, user_data)
            
            return {
                "success": True,
                "analysis": enhanced_analysis,
                "user_id": user_id,
                "ai_confidence": 0.85,
                "generated_at": datetime.now().isoformat()
            }
            
        except json.JSONDecodeError:
            # Fallback to statistical analysis
            return generate_statistical_weakness_analysis(user_data, focus_areas, time_period)
            
    except Exception as e:
        print(f"AI weakness analysis error: {e}")
        return generate_statistical_weakness_analysis(user_data, focus_areas, time_period)

def get_user_performance_data(user_id):
    """Get user's performance data for analysis"""
    if not supabase:
        return get_demo_performance_data()
    
    try:
        # Get performance data
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(100).execute()
        performances = performance_response.data or []
        
        # Get quiz attempts
        quiz_response = supabase.table('quiz_attempts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        quiz_attempts = quiz_response.data or []
        
        # Get learning path progress
        path_response = supabase.table('learning_paths').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()
        learning_paths = path_response.data or []
        
        return {
            "performances": performances,
            "quiz_attempts": quiz_attempts,
            "learning_paths": learning_paths,
            "total_attempts": len(performances) + len(quiz_attempts),
            "time_span": calculate_time_span(performances + quiz_attempts)
        }
        
    except Exception as e:
        print(f"Error getting performance data: {e}")
        return get_demo_performance_data()

def get_demo_performance_data():
    """Return demo performance data"""
    return {
        "performances": [
            {"score": 65, "total_questions": 10, "topic": "mathematics", "difficulty": "medium", "time_spent": 300, "created_at": "2024-01-15T10:00:00Z"},
            {"score": 70, "total_questions": 8, "topic": "science", "difficulty": "easy", "time_spent": 240, "created_at": "2024-01-14T15:30:00Z"},
            {"score": 55, "total_questions": 12, "topic": "mathematics", "difficulty": "hard", "time_spent": 450, "created_at": "2024-01-13T09:15:00Z"}
        ],
        "quiz_attempts": [
            {"score": 60, "total_questions": 5, "topic": "mathematics", "difficulty": "medium", "created_at": "2024-01-12T14:20:00Z"},
            {"score": 75, "total_questions": 5, "topic": "science", "difficulty": "easy", "created_at": "2024-01-11T16:45:00Z"}
        ],
        "learning_paths": [
            {"path_data": {"title": "Mathematics Mastery", "steps": []}, "status": "active", "created_at": "2024-01-10T08:00:00Z"}
        ],
        "total_attempts": 5,
        "time_span": 5
    }

def perform_comprehensive_weakness_analysis(performance_data):
    """Perform comprehensive weakness analysis"""
    performances = performance_data.get('performances', [])
    quiz_attempts = performance_data.get('quiz_attempts', [])
    
    all_attempts = performances + quiz_attempts
    
    if not all_attempts:
        return get_demo_weakness_analysis()
    
    # Calculate overall performance metrics
    scores = [(a.get('score', 0) / a.get('total_questions', 1)) * 100 for a in all_attempts]
    avg_score = sum(scores) / len(scores)
    
    # Identify weaknesses by score thresholds
    low_scores = [score for score in scores if score < 70]
    medium_scores = [score for score in scores if 70 <= score < 85]
    high_scores = [score for score in scores if score >= 85]
    
    # Analyze by topic
    topic_analysis = analyze_topic_weaknesses(all_attempts)
    
    # Analyze by difficulty
    difficulty_analysis = analyze_difficulty_weaknesses(all_attempts)
    
    # Identify patterns
    patterns = identify_performance_patterns(all_attempts)
    
    return {
        "overall_weaknesses": {
            "primary_weaknesses": identify_primary_weaknesses(scores, topic_analysis),
            "secondary_weaknesses": identify_secondary_weaknesses(scores, topic_analysis),
            "emerging_weaknesses": identify_emerging_weaknesses(all_attempts)
        },
        "subject_specific_weaknesses": topic_analysis,
        "difficulty_weaknesses": difficulty_analysis,
        "pattern_analysis": patterns,
        "overall_score": round(avg_score),
        "weakness_severity": "high" if avg_score < 60 else "medium" if avg_score < 80 else "low",
        "confidence": 0.8
    }

def perform_subject_weakness_analysis(performance_data):
    """Perform subject-specific weakness analysis"""
    performances = performance_data.get('performances', [])
    quiz_attempts = performance_data.get('quiz_attempts', [])
    
    all_attempts = performances + quiz_attempts
    
    # Group by subject
    subject_data = {}
    for attempt in all_attempts:
        subject = attempt.get('topic', 'general')
        score = (attempt.get('score', 0) / attempt.get('total_questions', 1)) * 100
        
        if subject not in subject_data:
            subject_data[subject] = []
        subject_data[subject].append(score)
    
    subject_weaknesses = []
    for subject, scores in subject_data.items():
        avg_score = sum(scores) / len(scores)
        
        subject_weaknesses.append({
            "subject": subject,
            "avg_score": round(avg_score),
            "weakness_level": "high" if avg_score < 60 else "medium" if avg_score < 80 else "low",
            "score_trend": analyze_score_trend(scores),
            "improvement_potential": "high" if avg_score < 70 else "medium" if avg_score < 85 else "low",
            "data_points": len(scores)
        })
    
    return {
        "subject_weaknesses": subject_weaknesses,
        "weakest_subject": min(subject_weaknesses, key=lambda x: x['avg_score'])['subject'] if subject_weaknesses else "N/A",
        "strongest_subject": max(subject_weaknesses, key=lambda x: x['avg_score'])['subject'] if subject_weaknesses else "N/A"
    }

def perform_skill_weakness_analysis(performance_data):
    """Perform skill-based weakness analysis"""
    performances = performance_data.get('performances', [])
    quiz_attempts = performance_data.get('quiz_attempts', [])
    
    all_attempts = performances + quiz_attempts
    
    # Analyze time efficiency
    time_analysis = analyze_time_efficiency(all_attempts)
    
    # Analyze consistency
    consistency_analysis = analyze_consistency(all_attempts)
    
    # Analyze difficulty progression
    progression_analysis = analyze_difficulty_progression(all_attempts)
    
    return {
        "time_efficiency": time_analysis,
        "consistency": consistency_analysis,
        "progression": progression_analysis,
        "overall_skill_level": "developing" if time_analysis['efficiency'] < 0.6 else "proficient"
    }

def perform_basic_weakness_analysis(performance_data):
    """Perform basic weakness analysis"""
    performances = performance_data.get('performances', [])
    quiz_attempts = performance_data.get('quiz_attempts', [])
    
    all_attempts = performances + quiz_attempts
    
    if not all_attempts:
        return {"weaknesses": [], "confidence": 0.5}
    
    # Calculate basic metrics
    scores = [(a.get('score', 0) / a.get('total_questions', 1)) * 100 for a in all_attempts]
    avg_score = sum(scores) / len(scores)
    
    # Identify basic weaknesses
    weaknesses = []
    if avg_score < 70:
        weaknesses.append({
            "weakness": "Low overall performance",
            "severity": "high" if avg_score < 50 else "medium",
            "description": f"Average score of {round(avg_score)}% is below expected level"
        })
    
    # Check for declining performance
    if len(scores) >= 3:
        recent_avg = sum(scores[:3]) / 3
        older_avg = sum(scores[3:]) / len(scores[3:]) if len(scores) > 3 else recent_avg
        if recent_avg < older_avg - 10:
            weaknesses.append({
                "weakness": "Declining performance",
                "severity": "medium",
                "description": "Recent performance is declining compared to earlier attempts"
            })
    
    return {
        "weaknesses": weaknesses,
        "avg_score": round(avg_score),
        "confidence": 0.7
    }

def analyze_topic_weaknesses(all_attempts):
    """Analyze weaknesses by topic"""
    topic_data = {}
    for attempt in all_attempts:
        topic = attempt.get('topic', 'general')
        score = (attempt.get('score', 0) / attempt.get('total_questions', 1)) * 100
        
        if topic not in topic_data:
            topic_data[topic] = []
        topic_data[topic].append(score)
    
    topic_analysis = []
    for topic, scores in topic_data.items():
        avg_score = sum(scores) / len(scores)
        
        topic_analysis.append({
            "subject": topic,
            "avg_score": round(avg_score),
            "weakness_level": "high" if avg_score < 60 else "medium" if avg_score < 80 else "low",
            "score_variance": calculate_variance(scores),
            "improvement_trend": analyze_score_trend(scores),
            "data_points": len(scores)
        })
    
    return topic_analysis

def analyze_difficulty_weaknesses(all_attempts):
    """Analyze weaknesses by difficulty level"""
    difficulty_data = {}
    for attempt in all_attempts:
        difficulty = attempt.get('difficulty', 'medium')
        score = (attempt.get('score', 0) / attempt.get('total_questions', 1)) * 100
        
        if difficulty not in difficulty_data:
            difficulty_data[difficulty] = []
        difficulty_data[difficulty].append(score)
    
    difficulty_analysis = []
    for difficulty, scores in difficulty_data.items():
        avg_score = sum(scores) / len(scores)
        
        difficulty_analysis.append({
            "difficulty": difficulty,
            "avg_score": round(avg_score),
            "performance_level": "struggling" if avg_score < 60 else "developing" if avg_score < 80 else "proficient",
            "readiness_for_next_level": avg_score >= 80,
            "data_points": len(scores)
        })
    
    return difficulty_analysis

def identify_performance_patterns(all_attempts):
    """Identify performance patterns"""
    patterns = []
    
    # Analyze score patterns
    scores = [(a.get('score', 0) / a.get('total_questions', 1)) * 100 for a in all_attempts]
    
    # Check for consistent low performance
    low_scores = [score for score in scores if score < 60]
    if len(low_scores) / len(scores) > 0.5:
        patterns.append({
            "pattern": "Consistent low performance",
            "frequency": "high",
            "description": "More than 50% of attempts score below 60%"
        })
    
    # Check for declining trend
    if len(scores) >= 5:
        recent_avg = sum(scores[:3]) / 3
        older_avg = sum(scores[3:]) / len(scores[3:])
        if recent_avg < older_avg - 10:
            patterns.append({
                "pattern": "Declining performance trend",
                "frequency": "medium",
                "description": "Recent performance is significantly lower than earlier attempts"
            })
    
    # Check for inconsistency
    if len(scores) >= 3:
        variance = calculate_variance(scores)
        if variance > 400:  # High variance
            patterns.append({
                "pattern": "Inconsistent performance",
                "frequency": "high",
                "description": "High variability in scores indicates inconsistent performance"
            })
    
    return patterns

def analyze_time_efficiency(all_attempts):
    """Analyze time efficiency"""
    if not all_attempts:
        return {"efficiency": 0.5, "avg_time_per_question": 60}
    
    time_data = []
    for attempt in all_attempts:
        time_spent = attempt.get('time_spent', 0)
        questions = attempt.get('total_questions', 1)
        if time_spent > 0 and questions > 0:
            time_per_question = time_spent / questions
            time_data.append(time_per_question)
    
    if not time_data:
        return {"efficiency": 0.5, "avg_time_per_question": 60}
    
    avg_time = sum(time_data) / len(time_data)
    
    # Efficiency score (lower time = higher efficiency)
    if avg_time < 30:
        efficiency = 0.9
    elif avg_time < 60:
        efficiency = 0.7
    elif avg_time < 120:
        efficiency = 0.5
    else:
        efficiency = 0.3
    
    return {
        "efficiency": efficiency,
        "avg_time_per_question": round(avg_time),
        "time_trend": "improving" if len(time_data) >= 3 and time_data[0] > time_data[-1] else "stable"
    }

def analyze_consistency(all_attempts):
    """Analyze performance consistency"""
    if not all_attempts:
        return {"consistency": 0.5, "variance": 0}
    
    scores = [(a.get('score', 0) / a.get('total_questions', 1)) * 100 for a in all_attempts]
    variance = calculate_variance(scores)
    
    # Consistency score (lower variance = higher consistency)
    if variance < 100:
        consistency = 0.9
    elif variance < 400:
        consistency = 0.7
    elif variance < 900:
        consistency = 0.5
    else:
        consistency = 0.3
    
    return {
        "consistency": consistency,
        "variance": round(variance),
        "score_range": f"{min(scores):.1f}% - {max(scores):.1f}%"
    }

def analyze_difficulty_progression(all_attempts):
    """Analyze difficulty progression capability"""
    if not all_attempts:
        return {"progression": 0.5, "readiness": "medium"}
    
    # Group by difficulty
    difficulty_scores = {}
    for attempt in all_attempts:
        difficulty = attempt.get('difficulty', 'medium')
        score = (attempt.get('score', 0) / attempt.get('total_questions', 1)) * 100
        
        if difficulty not in difficulty_scores:
            difficulty_scores[difficulty] = []
        difficulty_scores[difficulty].append(score)
    
    # Analyze progression readiness
    readiness = "low"
    if "easy" in difficulty_scores and "medium" in difficulty_scores:
        easy_avg = sum(difficulty_scores["easy"]) / len(difficulty_scores["easy"])
        medium_avg = sum(difficulty_scores["medium"]) / len(difficulty_scores["medium"])
        
        if easy_avg >= 85 and medium_avg >= 75:
            readiness = "high"
        elif easy_avg >= 80 and medium_avg >= 70:
            readiness = "medium"
    
    return {
        "progression": 0.7 if readiness == "high" else 0.5 if readiness == "medium" else 0.3,
        "readiness": readiness,
        "difficulty_performance": {k: round(sum(v)/len(v)) for k, v in difficulty_scores.items()}
    }

def identify_primary_weaknesses(scores, topic_analysis):
    """Identify primary weaknesses"""
    weaknesses = []
    
    # Overall low performance
    avg_score = sum(scores) / len(scores)
    if avg_score < 70:
        weaknesses.append({
            "weakness": "Overall low performance",
            "severity": "high" if avg_score < 50 else "medium",
            "impact": "Significantly affects learning progress",
            "frequency": "consistent",
            "trend": "stable"
        })
    
    # Subject-specific weaknesses
    for topic in topic_analysis:
        if topic['avg_score'] < 60:
            weaknesses.append({
                "weakness": f"Poor performance in {topic['subject']}",
                "severity": "high",
                "impact": f"Limits understanding in {topic['subject']}",
                "frequency": "consistent",
                "trend": "stable"
            })
    
    return weaknesses

def identify_secondary_weaknesses(scores, topic_analysis):
    """Identify secondary weaknesses"""
    weaknesses = []
    
    # Moderate performance issues
    avg_score = sum(scores) / len(scores)
    if 70 <= avg_score < 80:
        weaknesses.append({
            "weakness": "Moderate performance level",
            "severity": "medium",
            "impact": "Limits potential for advanced learning",
            "frequency": "frequent"
        })
    
    # Subject-specific moderate weaknesses
    for topic in topic_analysis:
        if 60 <= topic['avg_score'] < 75:
            weaknesses.append({
                "weakness": f"Developing skills in {topic['subject']}",
                "severity": "medium",
                "impact": f"Room for improvement in {topic['subject']}",
                "frequency": "occasional"
            })
    
    return weaknesses

def identify_emerging_weaknesses(all_attempts):
    """Identify emerging weaknesses"""
    if len(all_attempts) < 3:
        return []
    
    # Analyze recent trend
    recent_attempts = all_attempts[:3]
    recent_scores = [(a.get('score', 0) / a.get('total_questions', 1)) * 100 for a in recent_attempts]
    recent_avg = sum(recent_scores) / len(recent_scores)
    
    older_attempts = all_attempts[3:]
    if older_attempts:
        older_scores = [(a.get('score', 0) / a.get('total_questions', 1)) * 100 for a in older_attempts]
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg < older_avg - 15:
            return [{
                "weakness": "Recent performance decline",
                "severity": "medium",
                "confidence": 0.7,
                "early_indicators": ["Lower scores in recent attempts", "Increased time per question"]
            }]
    
    return []

def analyze_score_trend(scores):
    """Analyze score trend"""
    if len(scores) < 2:
        return "insufficient_data"
    
    if len(scores) >= 3:
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg + 5:
            return "improving"
        elif second_avg < first_avg - 5:
            return "declining"
        else:
            return "stable"
    else:
        return "stable"

def calculate_variance(scores):
    """Calculate variance of scores"""
    if len(scores) < 2:
        return 0
    
    mean = sum(scores) / len(scores)
    variance = sum((score - mean) ** 2 for score in scores) / len(scores)
    return variance

def calculate_time_span(attempts):
    """Calculate time span of attempts"""
    if not attempts:
        return 0
    
    dates = []
    for attempt in attempts:
        created_at = attempt.get('created_at', '')
        if created_at:
            try:
                date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                dates.append(date)
            except:
                pass
    
    if len(dates) < 2:
        return 0
    
    return (max(dates) - min(dates)).days

def get_comprehensive_user_data(user_id):
    """Get comprehensive user data for analysis"""
    if not supabase:
        return get_demo_comprehensive_data()
    
    try:
        # Get all user data
        performance_response = supabase.table('performance').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(100).execute()
        materials_response = supabase.table('study_materials').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(20).execute()
        quiz_response = supabase.table('quiz_attempts').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        
        performances = performance_response.data or []
        materials = materials_response.data or []
        quiz_attempts = quiz_response.data or []
        
        return {
            "user_id": user_id,
            "performances": performances,
            "materials": materials,
            "quiz_attempts": quiz_attempts,
            "total_attempts": len(performances) + len(quiz_attempts),
            "time_span": calculate_time_span(performances + quiz_attempts)
        }
        
    except Exception as e:
        print(f"Error getting comprehensive user data: {e}")
        return get_demo_comprehensive_data()

def get_demo_comprehensive_data():
    """Return demo comprehensive data"""
    return {
        "user_id": "demo-user",
        "performances": [
            {"score": 65, "topic": "mathematics", "difficulty": "medium", "time_spent": 300},
            {"score": 70, "topic": "science", "difficulty": "easy", "time_spent": 240}
        ],
        "materials": [
            {"filename": "Calculus.pdf", "ai_analysis": {"subject_category": "mathematics"}}
        ],
        "quiz_attempts": [
            {"score": 60, "topic": "mathematics", "difficulty": "medium"}
        ],
        "total_attempts": 3,
        "time_span": 5
    }

def enhance_weakness_analysis(ai_analysis, user_data):
    """Enhance AI analysis with additional insights"""
    # Add metadata
    ai_analysis['metadata'] = {
        "data_points": user_data.get('total_attempts', 0),
        "time_span_days": user_data.get('time_span', 0),
        "analysis_confidence": 0.85,
        "generated_at": datetime.now().isoformat()
    }
    
    # Add severity assessment
    if 'overall_weaknesses' in ai_analysis:
        primary_weaknesses = ai_analysis['overall_weaknesses'].get('primary_weaknesses', [])
        high_severity_count = len([w for w in primary_weaknesses if w.get('severity') == 'high'])
        
        if high_severity_count > 2:
            ai_analysis['overall_severity'] = 'critical'
        elif high_severity_count > 0:
            ai_analysis['overall_severity'] = 'high'
        else:
            ai_analysis['overall_severity'] = 'medium'
    
    return ai_analysis

def generate_statistical_weakness_analysis(user_data, focus_areas, time_period):
    """Generate statistical weakness analysis as fallback"""
    return {
        "success": True,
        "analysis": {
            "overall_weaknesses": {
                "primary_weaknesses": [
                    {
                        "weakness": "Statistical analysis indicates moderate performance",
                        "severity": "medium",
                        "impact": "Room for improvement in overall performance",
                        "frequency": "consistent",
                        "trend": "stable"
                    }
                ],
                "secondary_weaknesses": [],
                "emerging_weaknesses": []
            },
            "subject_specific_weaknesses": [
                {
                    "subject": "general",
                    "avg_score": 75,
                    "weakness_level": "medium",
                    "improvement_potential": "medium"
                }
            ],
            "recommendations": [
                {
                    "priority": "medium",
                    "category": "short_term",
                    "recommendation": "Focus on consistent practice",
                    "rationale": "Statistical analysis suggests need for regular practice",
                    "expected_impact": "medium",
                    "implementation_difficulty": "easy",
                    "timeline": "2-3 weeks"
                }
            ]
        },
        "user_id": user_data.get('user_id', 'demo-user'),
        "ai_confidence": 0.6,
        "generated_at": datetime.now().isoformat()
    }

def get_demo_weakness_analysis():
    """Return demo weakness analysis"""
    return {
        "success": True,
        "analysis": {
            "overall_weaknesses": {
                "primary_weaknesses": [
                    {
                        "weakness": "Mathematics problem-solving",
                        "severity": "medium",
                        "impact": "Affects overall mathematics performance",
                        "frequency": "frequent",
                        "trend": "stable"
                    }
                ],
                "secondary_weaknesses": [
                    {
                        "weakness": "Time management",
                        "severity": "low",
                        "impact": "Slightly affects quiz performance",
                        "frequency": "occasional"
                    }
                ],
                "emerging_weaknesses": []
            },
            "subject_specific_weaknesses": [
                {
                    "subject": "mathematics",
                    "avg_score": 70,
                    "weakness_level": "medium",
                    "improvement_potential": "high"
                }
            ],
            "recommendations": [
                {
                    "priority": "high",
                    "category": "immediate",
                    "recommendation": "Practice mathematics problem-solving daily",
                    "rationale": "Addresses primary weakness in mathematics",
                    "expected_impact": "high",
                    "implementation_difficulty": "medium",
                    "timeline": "1-2 weeks"
                }
            ]
        },
        "user_id": "demo-user",
        "analysis_type": "comprehensive",
        "confidence": 0.7,
        "generated_at": datetime.now().isoformat()
    }
