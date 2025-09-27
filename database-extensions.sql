-- =====================================================
-- EDUSENSE DATABASE EXTENSIONS
-- =====================================================
-- This file extends your existing database schema with:
-- 1. Study Materials System (enhanced)
-- 2. AI Enhancements
-- 3. Real-time Features
-- =====================================================

-- =====================================================
-- PART 1: ENHANCE EXISTING TABLES
-- =====================================================

-- Add new columns to existing study_materials table
ALTER TABLE public.study_materials 
ADD COLUMN IF NOT EXISTS ai_analysis JSONB,
ADD COLUMN IF NOT EXISTS word_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS char_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS starred BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS file_size INTEGER,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add new columns to existing learning_paths table
ALTER TABLE public.learning_paths 
ADD COLUMN IF NOT EXISTS path_data JSONB,
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'archived')),
ADD COLUMN IF NOT EXISTS progress_data JSONB DEFAULT '{}';

-- =====================================================
-- PART 2: NEW TABLES FOR STUDY MATERIALS SYSTEM
-- =====================================================

-- Create material_folders table for organization
CREATE TABLE IF NOT EXISTS public.material_folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    parent_folder_id UUID REFERENCES public.material_folders(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create material_folder_assignments table
CREATE TABLE IF NOT EXISTS public.material_folder_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id INTEGER REFERENCES public.study_materials(id) ON DELETE CASCADE,
    folder_id UUID REFERENCES public.material_folders(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(material_id, folder_id)
);

-- Create material_quizzes table to track quizzes generated from materials
CREATE TABLE IF NOT EXISTS public.material_quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id INTEGER REFERENCES public.study_materials(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    quiz_title TEXT NOT NULL,
    quiz_description TEXT,
    questions JSONB NOT NULL,
    difficulty TEXT NOT NULL,
    num_questions INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create material_analytics table for tracking material usage
CREATE TABLE IF NOT EXISTS public.material_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id INTEGER REFERENCES public.study_materials(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL, -- 'view', 'download', 'quiz_generated', 'starred', 'unstarred'
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- PART 3: AI ENHANCEMENTS
-- =====================================================

-- User Preferences Table
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    learning_style VARCHAR(50) DEFAULT 'mixed' CHECK (learning_style IN ('visual', 'auditory', 'kinesthetic', 'reading', 'mixed')),
    preferred_difficulty VARCHAR(20) DEFAULT 'medium' CHECK (preferred_difficulty IN ('easy', 'medium', 'hard')),
    favorite_subjects TEXT[] DEFAULT '{}',
    learning_goals TEXT[] DEFAULT '{}',
    available_time INTEGER DEFAULT 30, -- minutes per day
    notification_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Content Recommendations Table
CREATE TABLE IF NOT EXISTS public.content_recommendations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('quiz', 'material', 'video', 'article', 'practice')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100),
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    relevance_score DECIMAL(3,2) DEFAULT 0.5 CHECK (relevance_score >= 0 AND relevance_score <= 1),
    personalization_factors TEXT[] DEFAULT '{}',
    recommendation_reason TEXT,
    expected_benefits TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
);

-- Performance Predictions Table
CREATE TABLE IF NOT EXISTS public.performance_predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    prediction_type VARCHAR(50) NOT NULL CHECK (prediction_type IN ('overall', 'subject', 'difficulty', 'comprehensive')),
    prediction_data JSONB NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    time_horizon INTEGER DEFAULT 30, -- days
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 day')
);

-- Weakness Analysis Table
CREATE TABLE IF NOT EXISTS public.weakness_analysis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL CHECK (analysis_type IN ('comprehensive', 'subject', 'skill', 'basic')),
    analysis_data JSONB NOT NULL,
    severity_level VARCHAR(20) DEFAULT 'medium' CHECK (severity_level IN ('low', 'medium', 'high', 'critical')),
    confidence DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    focus_areas TEXT[] DEFAULT '{}',
    time_period INTEGER DEFAULT 30, -- days
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '3 days')
);

-- AI Insights Table
CREATE TABLE IF NOT EXISTS public.ai_insights (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL CHECK (insight_type IN ('learning_pattern', 'performance_trend', 'weakness_alert', 'strength_highlight', 'recommendation')),
    insight_data JSONB NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    actionable BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '14 days')
);

-- User Learning Profile Table
CREATE TABLE IF NOT EXISTS public.user_learning_profile (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_data JSONB NOT NULL,
    learning_style VARCHAR(50) DEFAULT 'mixed',
    cognitive_skills JSONB DEFAULT '{}',
    learning_preferences JSONB DEFAULT '{}',
    performance_patterns JSONB DEFAULT '{}',
    engagement_metrics JSONB DEFAULT '{}',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- =====================================================
-- PART 4: REAL-TIME FEATURES
-- =====================================================

-- Notifications Table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error', 'achievement')),
    read BOOLEAN DEFAULT false,
    action_url VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- Chat Messages Table
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    sender_name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    recipient_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    is_support_message BOOLEAN DEFAULT false,
    message_type VARCHAR(50) DEFAULT 'text' CHECK (message_type IN ('text', 'system', 'support')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Sessions Table (for online presence)
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    is_online BOOLEAN DEFAULT true,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    ip_address INET,
    location JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, session_id)
);

-- Real-time Analytics Table
CREATE TABLE IF NOT EXISTS public.realtime_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    metric_type VARCHAR(50) DEFAULT 'counter' CHECK (metric_type IN ('counter', 'gauge', 'histogram')),
    tags JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Progress Table (for real-time updates)
CREATE TABLE IF NOT EXISTS public.user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id UUID,
    score INT,
    quizzes_completed INT DEFAULT 0,
    study_streak INT DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_study_time_minutes INT DEFAULT 0,
    mastery_level JSONB DEFAULT '{}'
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Study Materials Indexes
CREATE INDEX IF NOT EXISTS idx_study_materials_ai_analysis ON public.study_materials USING GIN(ai_analysis);
CREATE INDEX IF NOT EXISTS idx_study_materials_starred ON public.study_materials(starred);
CREATE INDEX IF NOT EXISTS idx_study_materials_content_search ON public.study_materials USING GIN(to_tsvector('english', content));

-- Material System Indexes
CREATE INDEX IF NOT EXISTS idx_material_folders_user_id ON public.material_folders(user_id);
CREATE INDEX IF NOT EXISTS idx_material_folders_parent ON public.material_folders(parent_folder_id);
CREATE INDEX IF NOT EXISTS idx_material_quizzes_material_id ON public.material_quizzes(material_id);
CREATE INDEX IF NOT EXISTS idx_material_quizzes_user_id ON public.material_quizzes(user_id);
CREATE INDEX IF NOT EXISTS idx_material_analytics_material_id ON public.material_analytics(material_id);
CREATE INDEX IF NOT EXISTS idx_material_analytics_user_id ON public.material_analytics(user_id);

-- AI Enhancement Indexes
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON public.user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_content_recommendations_user_id ON public.content_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_predictions_user_id ON public.performance_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_weakness_analysis_user_id ON public.weakness_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_user_id ON public.ai_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_user_learning_profile_user_id ON public.user_learning_profile(user_id);

-- Real-time Indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON public.notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON public.notifications(read);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON public.chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_seen ON public.user_sessions(last_seen);
CREATE INDEX IF NOT EXISTS idx_realtime_analytics_user_id ON public.realtime_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON public.user_progress(user_id);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on new tables
ALTER TABLE public.material_folders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.material_folder_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.material_quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.material_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weakness_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_learning_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.realtime_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_progress ENABLE ROW LEVEL SECURITY;

-- Material System RLS Policies
CREATE POLICY "Users can view their own folders" ON public.material_folders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own folders" ON public.material_folders FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own folders" ON public.material_folders FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own folders" ON public.material_folders FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own folder assignments" ON public.material_folder_assignments FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.study_materials sm WHERE sm.id = material_id AND sm.user_id = auth.uid())
);
CREATE POLICY "Users can insert their own folder assignments" ON public.material_folder_assignments FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM public.study_materials sm WHERE sm.id = material_id AND sm.user_id = auth.uid())
);
CREATE POLICY "Users can delete their own folder assignments" ON public.material_folder_assignments FOR DELETE USING (
    EXISTS (SELECT 1 FROM public.study_materials sm WHERE sm.id = material_id AND sm.user_id = auth.uid())
);

CREATE POLICY "Users can view their own material quizzes" ON public.material_quizzes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own material quizzes" ON public.material_quizzes FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can view their own material analytics" ON public.material_analytics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own material analytics" ON public.material_analytics FOR INSERT WITH CHECK (auth.uid() = user_id);

-- AI Enhancement RLS Policies
CREATE POLICY "Users can view their own preferences" ON public.user_preferences FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own preferences" ON public.user_preferences FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own preferences" ON public.user_preferences FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own recommendations" ON public.content_recommendations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own predictions" ON public.performance_predictions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own weakness analysis" ON public.weakness_analysis FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own insights" ON public.ai_insights FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own profile" ON public.user_learning_profile FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own profile" ON public.user_learning_profile FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own profile" ON public.user_learning_profile FOR UPDATE USING (auth.uid() = user_id);

-- Real-time RLS Policies
CREATE POLICY "Users can view their own notifications" ON public.notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own notifications" ON public.notifications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "System can insert notifications" ON public.notifications FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view messages they sent or received" ON public.chat_messages FOR SELECT USING (auth.uid() = user_id OR auth.uid() = recipient_id OR recipient_id IS NULL);
CREATE POLICY "Users can insert their own messages" ON public.chat_messages FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own sessions" ON public.user_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own sessions" ON public.user_sessions FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own analytics" ON public.realtime_analytics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "System can insert analytics" ON public.realtime_analytics FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view their own progress" ON public.user_progress FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own progress" ON public.user_progress FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own progress" ON public.user_progress FOR INSERT WITH CHECK (auth.uid() = user_id);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_study_materials_updated_at BEFORE UPDATE ON public.study_materials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_learning_paths_updated_at BEFORE UPDATE ON public.learning_paths FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON public.user_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_sessions_updated_at BEFORE UPDATE ON public.user_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_learning_profile_updated_at BEFORE UPDATE ON public.user_learning_profile FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to send notification
CREATE OR REPLACE FUNCTION send_notification(
    p_user_id UUID,
    p_title VARCHAR(255),
    p_message TEXT,
    p_type VARCHAR(50) DEFAULT 'info',
    p_action_url VARCHAR(500) DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    notification_id UUID;
BEGIN
    INSERT INTO public.notifications (user_id, title, message, type, action_url, metadata)
    VALUES (p_user_id, p_title, p_message, p_type, p_action_url, p_metadata)
    RETURNING id INTO notification_id;
    RETURN notification_id;
END;
$$ LANGUAGE plpgsql;

-- Function to log user activity
CREATE OR REPLACE FUNCTION log_user_activity(
    p_user_id UUID,
    p_activity_type VARCHAR(100),
    p_activity_data JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    activity_id UUID;
BEGIN
    INSERT INTO public.user_activity_log (user_id, activity_type, activity_data)
    VALUES (p_user_id, p_activity_type, p_activity_data)
    RETURNING id INTO activity_id;
    RETURN activity_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ENABLE REALTIME FOR SUPABASE
-- =====================================================

-- Enable realtime for tables that need live updates
ALTER PUBLICATION supabase_realtime ADD TABLE public.notifications;
ALTER PUBLICATION supabase_realtime ADD TABLE public.chat_messages;
ALTER PUBLICATION supabase_realtime ADD TABLE public.user_progress;
ALTER PUBLICATION supabase_realtime ADD TABLE public.realtime_analytics;

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON public.material_folders TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.material_folder_assignments TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.material_quizzes TO authenticated;
GRANT SELECT, INSERT ON public.material_analytics TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.user_preferences TO authenticated;
GRANT SELECT ON public.content_recommendations TO authenticated;
GRANT SELECT ON public.performance_predictions TO authenticated;
GRANT SELECT ON public.weakness_analysis TO authenticated;
GRANT SELECT ON public.ai_insights TO authenticated;
GRANT SELECT, UPDATE ON public.notifications TO authenticated;
GRANT SELECT, INSERT ON public.chat_messages TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_sessions TO authenticated;
GRANT SELECT ON public.realtime_analytics TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.user_progress TO authenticated;

-- =====================================================
-- SAMPLE DATA (OPTIONAL)
-- =====================================================

-- Note: Sample data insertion removed to avoid foreign key constraint errors
-- You can manually insert sample data after creating a user account
-- Example: INSERT INTO public.user_preferences (user_id, learning_style, preferred_difficulty, favorite_subjects, learning_goals, available_time)
-- VALUES ('your-actual-user-uuid', 'visual', 'medium', ARRAY['mathematics', 'science'], ARRAY['improve_problem_solving'], 45);

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

-- This completes the database extensions for EduSense
-- All new tables, indexes, RLS policies, and functions are now created
-- Your existing schema remains intact and is enhanced with new capabilities
