-- Minimal Database Setup (if you get any other errors)
-- Run each section separately

-- 1. Create performance table (most important)
CREATE TABLE public.performance (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  difficulty TEXT NOT NULL,
  score INTEGER NOT NULL,
  total_questions INTEGER NOT NULL,
  time_spent INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Enable RLS and create policy
ALTER TABLE public.performance ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own performance" ON public.performance
  FOR ALL USING (auth.uid() = user_id);

-- 3. Create basic quiz table
CREATE TABLE public.quizzes (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  topic TEXT NOT NULL,
  difficulty TEXT NOT NULL,
  questions JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view quizzes" ON public.quizzes
  FOR SELECT USING (true);
