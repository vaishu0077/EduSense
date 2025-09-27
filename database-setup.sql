-- EduSense Database Schema
-- Run this in Supabase SQL Editor

-- Enable Row Level Security
ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

-- Create students table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.students (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  email TEXT,
  grade TEXT,
  subjects TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create quizzes table
CREATE TABLE IF NOT EXISTS public.quizzes (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  topic TEXT NOT NULL,
  difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
  questions JSONB NOT NULL,
  created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create performance table
CREATE TABLE IF NOT EXISTS public.performance (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  quiz_id INTEGER REFERENCES public.quizzes(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  difficulty TEXT NOT NULL,
  score INTEGER NOT NULL,
  total_questions INTEGER NOT NULL,
  time_spent INTEGER DEFAULT 0, -- in seconds
  percentage DECIMAL(5,2) GENERATED ALWAYS AS (
    CASE 
      WHEN total_questions > 0 THEN (score::DECIMAL / total_questions) * 100
      ELSE 0 
    END
  ) STORED,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create learning_paths table
CREATE TABLE IF NOT EXISTS public.learning_paths (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  current_level TEXT DEFAULT 'beginner',
  progress INTEGER DEFAULT 0, -- percentage
  recommended_next JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create study_materials table (for future use)
CREATE TABLE IF NOT EXISTS public.study_materials (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT,
  file_url TEXT,
  file_type TEXT,
  topic TEXT,
  ai_summary TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security on all tables
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.study_materials ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for students table
CREATE POLICY "Users can view own student profile" ON public.students
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own student profile" ON public.students
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create RLS policies for quizzes table
CREATE POLICY "Anyone can view quizzes" ON public.quizzes
  FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create quizzes" ON public.quizzes
  FOR INSERT WITH CHECK (auth.uid() = created_by);

-- Create RLS policies for performance table
CREATE POLICY "Users can view own performance" ON public.performance
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own performance" ON public.performance
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create RLS policies for learning_paths table
CREATE POLICY "Users can manage own learning paths" ON public.learning_paths
  FOR ALL USING (auth.uid() = user_id);

-- Create RLS policies for study_materials table
CREATE POLICY "Users can manage own study materials" ON public.study_materials
  FOR ALL USING (auth.uid() = user_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_performance_user_id ON public.performance(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_topic ON public.performance(topic);
CREATE INDEX IF NOT EXISTS idx_performance_created_at ON public.performance(created_at);
CREATE INDEX IF NOT EXISTS idx_quizzes_topic ON public.quizzes(topic);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON public.students(user_id);

-- Create functions for analytics
CREATE OR REPLACE FUNCTION get_user_analytics(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'total_quizzes', COUNT(*),
    'average_score', ROUND(AVG(percentage), 2),
    'total_time', SUM(time_spent),
    'topics_studied', COUNT(DISTINCT topic),
    'best_topic', (
      SELECT topic 
      FROM public.performance 
      WHERE user_id = user_uuid 
      GROUP BY topic 
      ORDER BY AVG(percentage) DESC 
      LIMIT 1
    ),
    'recent_performance', (
      SELECT json_agg(
        json_build_object(
          'topic', topic,
          'score', score,
          'percentage', percentage,
          'date', created_at
        ) ORDER BY created_at DESC
      )
      FROM (
        SELECT topic, score, percentage, created_at
        FROM public.performance 
        WHERE user_id = user_uuid 
        ORDER BY created_at DESC 
        LIMIT 10
      ) recent
    )
  ) INTO result
  FROM public.performance
  WHERE user_id = user_uuid;
  
  RETURN COALESCE(result, '{}'::JSON);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Insert sample quiz data (optional)
INSERT INTO public.quizzes (title, description, topic, difficulty, questions, created_by) VALUES
(
  'Basic Mathematics Quiz',
  'Test your fundamental math skills',
  'Mathematics',
  'easy',
  '[
    {
      "question": "What is 2 + 2?",
      "options": ["3", "4", "5", "6"],
      "correct_answer": 1,
      "explanation": "2 + 2 equals 4"
    },
    {
      "question": "What is 10 ÷ 2?",
      "options": ["4", "5", "6", "7"],
      "correct_answer": 1,
      "explanation": "10 divided by 2 equals 5"
    }
  ]'::jsonb,
  NULL
),
(
  'Science Basics Quiz',
  'Fundamental science concepts',
  'Science',
  'medium',
  '[
    {
      "question": "What is the chemical symbol for water?",
      "options": ["H2O", "CO2", "NaCl", "O2"],
      "correct_answer": 0,
      "explanation": "Water is composed of two hydrogen atoms and one oxygen atom: H2O"
    }
  ]'::jsonb,
  NULL
);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- Enable realtime for performance table (optional)
ALTER PUBLICATION supabase_realtime ADD TABLE public.performance;
