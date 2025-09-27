-- EduSense Database Schema for Supabase
-- Run this in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Students table (extends auth.users)
CREATE TABLE public.students (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  name TEXT,
  email TEXT,
  grade TEXT,
  subjects JSONB,
  learning_style TEXT,
  difficulty_preference TEXT DEFAULT 'medium',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quizzes table
CREATE TABLE public.quizzes (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  topic TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  difficulty_level TEXT DEFAULT 'medium',
  time_limit INTEGER DEFAULT 30,
  is_ai_generated BOOLEAN DEFAULT false,
  ai_model_used TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Questions table
CREATE TABLE public.questions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  quiz_id UUID REFERENCES public.quizzes(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  question_type TEXT NOT NULL CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay')),
  options JSONB,
  correct_answer TEXT NOT NULL,
  explanation TEXT,
  points INTEGER DEFAULT 1,
  order_index INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance table
CREATE TABLE public.performance (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  score FLOAT,
  attempts INTEGER DEFAULT 1,
  time_taken INTEGER,
  quiz_id UUID REFERENCES public.quizzes(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz attempts table
CREATE TABLE public.quiz_attempts (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  quiz_id UUID REFERENCES public.quizzes(id) ON DELETE CASCADE,
  score FLOAT,
  percentage FLOAT,
  time_taken INTEGER,
  responses JSONB,
  is_completed BOOLEAN DEFAULT false,
  is_passed BOOLEAN DEFAULT false,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Learning paths table
CREATE TABLE public.learning_paths (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  topics_sequence JSONB NOT NULL,
  current_topic_index INTEGER DEFAULT 0,
  progress_percentage FLOAT DEFAULT 0.0,
  is_ai_generated BOOLEAN DEFAULT false,
  ai_model_used TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content table for uploaded materials
CREATE TABLE public.content (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  content_type TEXT NOT NULL,
  file_url TEXT,
  file_size INTEGER,
  extracted_text TEXT,
  simplified_text TEXT,
  subject TEXT,
  grade_level TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content ENABLE ROW LEVEL SECURITY;

-- Create RLS policies

-- Students can view and update their own profile
CREATE POLICY "Students can view own profile" ON public.students FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Students can update own profile" ON public.students FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Students can insert own profile" ON public.students FOR INSERT WITH CHECK (auth.uid() = id);

-- Quizzes are publicly readable
CREATE POLICY "Anyone can view quizzes" ON public.quizzes FOR SELECT USING (true);

-- Questions are publicly readable
CREATE POLICY "Anyone can view questions" ON public.questions FOR SELECT USING (true);

-- Students can view and insert their own performance
CREATE POLICY "Students can view own performance" ON public.performance FOR SELECT USING (auth.uid() = student_id);
CREATE POLICY "Students can insert own performance" ON public.performance FOR INSERT WITH CHECK (auth.uid() = student_id);

-- Students can view and insert their own quiz attempts
CREATE POLICY "Students can view own quiz attempts" ON public.quiz_attempts FOR SELECT USING (auth.uid() = student_id);
CREATE POLICY "Students can insert own quiz attempts" ON public.quiz_attempts FOR INSERT WITH CHECK (auth.uid() = student_id);
CREATE POLICY "Students can update own quiz attempts" ON public.quiz_attempts FOR UPDATE USING (auth.uid() = student_id);

-- Students can view and insert their own learning paths
CREATE POLICY "Students can view own learning paths" ON public.learning_paths FOR SELECT USING (auth.uid() = student_id);
CREATE POLICY "Students can insert own learning paths" ON public.learning_paths FOR INSERT WITH CHECK (auth.uid() = student_id);
CREATE POLICY "Students can update own learning paths" ON public.learning_paths FOR UPDATE USING (auth.uid() = student_id);

-- Students can view and insert their own content
CREATE POLICY "Students can view own content" ON public.content FOR SELECT USING (auth.uid() = student_id);
CREATE POLICY "Students can insert own content" ON public.content FOR INSERT WITH CHECK (auth.uid() = student_id);
CREATE POLICY "Students can update own content" ON public.content FOR UPDATE USING (auth.uid() = student_id);

-- Create storage bucket for content
INSERT INTO storage.buckets (id, name, public) VALUES ('content', 'content', true);

-- Create storage policies
CREATE POLICY "Anyone can view content" ON storage.objects FOR SELECT USING (bucket_id = 'content');
CREATE POLICY "Authenticated users can upload content" ON storage.objects FOR INSERT WITH CHECK (
  bucket_id = 'content' AND auth.role() = 'authenticated'
);
CREATE POLICY "Users can update own content" ON storage.objects FOR UPDATE USING (
  bucket_id = 'content' AND auth.uid()::text = (storage.foldername(name))[1]
);
CREATE POLICY "Users can delete own content" ON storage.objects FOR DELETE USING (
  bucket_id = 'content' AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Create indexes for better performance
CREATE INDEX idx_performance_student_id ON public.performance(student_id);
CREATE INDEX idx_performance_topic ON public.performance(topic);
CREATE INDEX idx_quiz_attempts_student_id ON public.quiz_attempts(student_id);
CREATE INDEX idx_quiz_attempts_quiz_id ON public.quiz_attempts(quiz_id);
CREATE INDEX idx_questions_quiz_id ON public.questions(quiz_id);
CREATE INDEX idx_learning_paths_student_id ON public.learning_paths(student_id);
CREATE INDEX idx_content_student_id ON public.content(student_id);

-- Create function to automatically create student profile
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.students (id, name, email)
  VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name', NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically create student profile on signup
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Insert sample data for testing
INSERT INTO public.quizzes (topic, title, description, difficulty_level) VALUES
('Mathematics', 'Basic Algebra Quiz', 'Test your algebra fundamentals', 'medium'),
('Science', 'Biology Basics', 'Understanding living organisms', 'easy'),
('English', 'Grammar and Vocabulary', 'Test your English language skills', 'medium');

-- Insert sample questions
INSERT INTO public.questions (quiz_id, question_text, question_type, options, correct_answer, explanation) VALUES
((SELECT id FROM public.quizzes WHERE title = 'Basic Algebra Quiz' LIMIT 1), 
 'What is 2x + 3 = 7?', 'multiple_choice', 
 '["x = 1", "x = 2", "x = 3", "x = 4"]', 'x = 2', 
 'Subtract 3 from both sides: 2x = 4, then divide by 2: x = 2'),

((SELECT id FROM public.quizzes WHERE title = 'Biology Basics' LIMIT 1), 
 'What gas do plants absorb during photosynthesis?', 'multiple_choice', 
 '["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"]', 'Carbon Dioxide', 
 'Plants absorb carbon dioxide from the atmosphere during photosynthesis'),

((SELECT id FROM public.quizzes WHERE title = 'Grammar and Vocabulary' LIMIT 1), 
 'Which word is a noun?', 'multiple_choice', 
 '["run", "quickly", "book", "beautiful"]', 'book', 
 'A noun is a person, place, thing, or idea. "Book" is a thing.');
