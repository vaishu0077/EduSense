# EduSense Deployment Guide

This guide will help you deploy EduSense to production using Vercel (frontend) and Render (backend).

## Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **Google AI Studio Account**: Get Gemini API key from [makersuite.google.com](https://makersuite.google.com)
3. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
4. **Render Account**: Sign up at [render.com](https://render.com)
5. **GitHub Repository**: Push your code to GitHub

## Step 1: Set up Supabase

### 1.1 Create a new Supabase project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note down your project URL and anon key

### 1.2 Set up database tables
Run the following SQL in your Supabase SQL editor:

```sql
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (handled by Supabase Auth)
-- Create profiles table to extend auth.users
CREATE TABLE public.profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  username TEXT UNIQUE,
  full_name TEXT,
  role TEXT DEFAULT 'student' CHECK (role IN ('student', 'teacher', 'admin')),
  avatar_url TEXT,
  bio TEXT,
  grade_level TEXT,
  subjects JSONB,
  learning_style TEXT,
  difficulty_preference TEXT DEFAULT 'medium',
  accessibility_needs JSONB,
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  email_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ
);

-- Topics table
CREATE TABLE public.topics (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  subject TEXT NOT NULL,
  grade_level TEXT NOT NULL,
  difficulty_level TEXT DEFAULT 'medium',
  learning_objectives TEXT,
  prerequisites JSONB,
  estimated_duration INTEGER,
  tags JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chapters table
CREATE TABLE public.chapters (
  id SERIAL PRIMARY KEY,
  topic_id INTEGER REFERENCES public.topics(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  simplified_content TEXT,
  content_type TEXT DEFAULT 'text',
  file_url TEXT,
  file_size INTEGER,
  order_index INTEGER DEFAULT 0,
  is_required BOOLEAN DEFAULT true,
  complexity_score FLOAT,
  keywords JSONB,
  summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quizzes table
CREATE TABLE public.quizzes (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  topic_id INTEGER REFERENCES public.topics(id) ON DELETE CASCADE,
  difficulty_level TEXT DEFAULT 'medium',
  time_limit INTEGER,
  max_attempts INTEGER DEFAULT 3,
  passing_score FLOAT DEFAULT 0.7,
  is_ai_generated BOOLEAN DEFAULT false,
  generation_prompt TEXT,
  ai_model_used TEXT,
  shuffle_questions BOOLEAN DEFAULT true,
  show_correct_answers BOOLEAN DEFAULT true,
  show_explanations BOOLEAN DEFAULT true,
  tags JSONB,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Questions table
CREATE TABLE public.questions (
  id SERIAL PRIMARY KEY,
  quiz_id INTEGER REFERENCES public.quizzes(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  question_type TEXT NOT NULL CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay', 'fill_in_blank')),
  points FLOAT DEFAULT 1.0,
  difficulty_level TEXT DEFAULT 'medium',
  order_index INTEGER DEFAULT 0,
  is_ai_generated BOOLEAN DEFAULT false,
  generation_context TEXT,
  options JSONB,
  correct_answer TEXT NOT NULL,
  explanation TEXT,
  hints JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Answers table
CREATE TABLE public.answers (
  id SERIAL PRIMARY KEY,
  question_id INTEGER REFERENCES public.questions(id) ON DELETE CASCADE,
  answer_text TEXT NOT NULL,
  is_correct BOOLEAN DEFAULT false,
  order_index INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quiz attempts table
CREATE TABLE public.quiz_attempts (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  quiz_id INTEGER REFERENCES public.quizzes(id) ON DELETE CASCADE,
  attempt_number INTEGER DEFAULT 1,
  score FLOAT,
  percentage FLOAT,
  time_taken INTEGER,
  is_completed BOOLEAN DEFAULT false,
  is_passed BOOLEAN DEFAULT false,
  responses JSONB,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Performance table
CREATE TABLE public.performances (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  topic_id INTEGER REFERENCES public.topics(id) ON DELETE CASCADE,
  overall_score FLOAT,
  quiz_scores JSONB,
  time_spent INTEGER DEFAULT 0,
  attempts_count INTEGER DEFAULT 0,
  completion_percentage FLOAT DEFAULT 0.0,
  last_activity TIMESTAMPTZ,
  mastery_level TEXT DEFAULT 'beginner',
  correct_answers INTEGER DEFAULT 0,
  total_questions INTEGER DEFAULT 0,
  average_response_time FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Learning paths table
CREATE TABLE public.learning_paths (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'archived')),
  difficulty_level TEXT DEFAULT 'medium',
  estimated_duration INTEGER,
  topics_sequence JSONB NOT NULL,
  current_topic_index INTEGER DEFAULT 0,
  completed_topics JSONB,
  is_ai_generated BOOLEAN DEFAULT false,
  generation_reason TEXT,
  ai_model_used TEXT,
  progress_percentage FLOAT DEFAULT 0.0,
  total_topics INTEGER NOT NULL,
  completed_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Weaknesses table
CREATE TABLE public.weaknesses (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  topic_id INTEGER REFERENCES public.topics(id) ON DELETE CASCADE,
  severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  confidence_score FLOAT NOT NULL,
  description TEXT,
  related_quiz_scores JSONB,
  related_attempts JSONB,
  last_identified TIMESTAMPTZ DEFAULT NOW(),
  is_improving BOOLEAN DEFAULT false,
  improvement_rate FLOAT,
  recommended_actions JSONB,
  is_resolved BOOLEAN DEFAULT false,
  resolved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics table
CREATE TABLE public.analytics (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  analytics_type TEXT NOT NULL CHECK (analytics_type IN ('performance', 'engagement', 'learning_pattern', 'weakness_analysis', 'prediction')),
  data JSONB NOT NULL,
  insights TEXT,
  recommendations JSONB,
  period_start TIMESTAMPTZ NOT NULL,
  period_end TIMESTAMPTZ NOT NULL,
  generated_by TEXT DEFAULT 'system',
  confidence_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Predictions table
CREATE TABLE public.predictions (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  prediction_type TEXT NOT NULL CHECK (prediction_type IN ('performance', 'completion_time', 'dropout_risk', 'mastery_level')),
  predicted_value FLOAT NOT NULL,
  confidence_score FLOAT NOT NULL,
  prediction_horizon INTEGER NOT NULL,
  context_data JSONB,
  model_used TEXT,
  model_version TEXT,
  actual_value FLOAT,
  accuracy_score FLOAT,
  is_validated BOOLEAN DEFAULT false,
  validated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

-- Content table
CREATE TABLE public.content (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  content_type TEXT NOT NULL,
  file_url TEXT,
  file_size INTEGER,
  file_name TEXT,
  extracted_text TEXT,
  simplified_text TEXT,
  summary TEXT,
  subject TEXT NOT NULL,
  grade_level TEXT NOT NULL,
  difficulty_level TEXT DEFAULT 'medium',
  tags JSONB,
  uploaded_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weaknesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Profiles policies
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Topics policies (public read, admin write)
CREATE POLICY "Anyone can view topics" ON public.topics FOR SELECT USING (true);
CREATE POLICY "Teachers and admins can manage topics" ON public.topics FOR ALL USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role IN ('teacher', 'admin'))
);

-- Similar policies for other tables...
-- (Add more RLS policies as needed)

-- Create storage bucket for content
INSERT INTO storage.buckets (id, name, public) VALUES ('content', 'content', true);

-- Create storage policies
CREATE POLICY "Anyone can view content" ON storage.objects FOR SELECT USING (bucket_id = 'content');
CREATE POLICY "Authenticated users can upload content" ON storage.objects FOR INSERT WITH CHECK (
  bucket_id = 'content' AND auth.role() = 'authenticated'
);
```

### 1.3 Set up storage bucket
1. Go to Storage in your Supabase dashboard
2. Create a new bucket called "content"
3. Make it public for file access

## Step 2: Deploy Backend to Render

### 2.1 Create a new Web Service on Render
1. Go to [render.com](https://render.com) and create a new Web Service
2. Connect your GitHub repository
3. Use these settings:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

### 2.2 Set environment variables in Render
Add these environment variables in your Render service settings:

```
DATABASE_URL=your-supabase-database-url
GEMINI_API_KEY=your-gemini-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=["https://your-frontend-domain.vercel.app"]
```

### 2.3 Deploy
Click "Deploy" and wait for the deployment to complete. Note the service URL.

## Step 3: Deploy Frontend to Vercel

### 3.1 Create a new project on Vercel
1. Go to [vercel.com](https://vercel.com) and create a new project
2. Connect your GitHub repository
3. Set the root directory to `frontend`

### 3.2 Set environment variables in Vercel
Add these environment variables in your Vercel project settings:

```
REACT_APP_API_URL=https://your-backend-url.onrender.com
REACT_APP_SUPABASE_URL=your-supabase-url
REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3.3 Deploy
Click "Deploy" and wait for the deployment to complete.

## Step 4: Configure Domain and SSL

### 4.1 Custom Domain (Optional)
1. In Vercel, go to your project settings
2. Add your custom domain
3. Configure DNS settings as instructed

### 4.2 Update CORS settings
Update your backend environment variables to include your production frontend URL:

```
ALLOWED_HOSTS=["https://your-domain.vercel.app", "https://your-custom-domain.com"]
```

## Step 5: Test the Deployment

### 5.1 Test Authentication
1. Visit your deployed frontend URL
2. Try to register a new account
3. Check if the user appears in Supabase Auth

### 5.2 Test AI Features
1. Create a topic and generate a quiz
2. Verify that Gemini API is working
3. Test content simplification

### 5.3 Test File Upload
1. Upload a PDF or document
2. Verify it appears in Supabase storage
3. Test content processing

## Step 6: Monitoring and Maintenance

### 6.1 Set up monitoring
- Use Render's built-in monitoring
- Set up error tracking with Sentry (optional)
- Monitor API usage and costs

### 6.2 Regular maintenance
- Monitor Supabase usage and costs
- Check Gemini API usage and limits
- Update dependencies regularly
- Backup database regularly

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure your backend ALLOWED_HOSTS includes your frontend URL
2. **Database Connection**: Verify your DATABASE_URL is correct
3. **API Key Issues**: Check that all API keys are properly set
4. **File Upload Issues**: Verify Supabase storage bucket is public and policies are correct

### Getting Help

1. Check the logs in Render dashboard
2. Check Supabase logs in the dashboard
3. Use browser developer tools to debug frontend issues
4. Check Vercel function logs

## Cost Optimization

### Supabase
- Use the free tier for development
- Monitor usage to avoid overages
- Consider upgrading to Pro for production

### Render
- Use the free tier for development
- Upgrade to paid plans for production
- Monitor resource usage

### Gemini API
- Monitor API usage and costs
- Implement caching to reduce API calls
- Use appropriate model settings

## Security Considerations

1. **Environment Variables**: Never commit API keys to version control
2. **Database Security**: Use RLS policies properly
3. **API Security**: Implement rate limiting and authentication
4. **File Upload**: Validate file types and sizes
5. **CORS**: Configure CORS properly for production

## Performance Optimization

1. **Database Indexing**: Add indexes for frequently queried columns
2. **Caching**: Implement Redis caching for frequently accessed data
3. **CDN**: Use Vercel's CDN for static assets
4. **Image Optimization**: Optimize images before upload
5. **API Optimization**: Implement pagination and filtering

This deployment guide should get your EduSense application running in production. Make sure to test thoroughly and monitor your application after deployment.
