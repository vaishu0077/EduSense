-- =====================================================
-- COMPLETE DATABASE SCHEMA FOR EDUSENSE
-- =====================================================
-- This file combines all database schemas for:
-- 1. Study Materials System
-- 2. AI Enhancements
-- 3. Real-time Features
-- =====================================================

-- =====================================================
-- PART 1: STUDY MATERIALS SYSTEM
-- =====================================================

-- Create study_materials table
CREATE TABLE IF NOT EXISTS study_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    content TEXT NOT NULL,
    ai_analysis JSONB,
    word_count INTEGER DEFAULT 0,
    char_count INTEGER DEFAULT 0,
    starred BOOLEAN DEFAULT FALSE,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create material_folders table for organization
CREATE TABLE IF NOT EXISTS material_folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    parent_folder_id UUID REFERENCES material_folders(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create material_folder_assignments table
CREATE TABLE IF NOT EXISTS material_folder_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID REFERENCES study_materials(id) ON DELETE CASCADE,
    folder_id UUID REFERENCES material_folders(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(material_id, folder_id)
);

-- Create material_quizzes table to track quizzes generated from materials
CREATE TABLE IF NOT EXISTS material_quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID REFERENCES study_materials(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    quiz_title TEXT NOT NULL,
    quiz_description TEXT,
    questions JSONB NOT NULL,
    difficulty TEXT NOT NULL,
    num_questions INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create material_analytics table for tracking material usage
CREATE TABLE IF NOT EXISTS material_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID REFERENCES study_materials(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL, -- 'view', 'download', 'quiz_generated', 'starred', 'unstarred'
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- PART 2: AI ENHANCEMENTS
-- =====================================================

-- Learning Paths Table
CREATE TABLE IF NOT EXISTS learning_paths (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    path_data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'archived')),
    progress_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
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
CREATE TABLE IF NOT EXISTS content_recommendations (
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
CREATE TABLE IF NOT EXISTS performance_predictions (
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
CREATE TABLE IF NOT EXISTS weakness_analysis (
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
CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL CHECK (insight_type IN ('learning_pattern', 'performance_trend', 'weakness_alert', 'strength_highlight', 'recommendation')),
    insight_data JSONB NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    actionable BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '14 days')
);

-- =====================================================
-- PART 3: REAL-TIME FEATURES
-- =====================================================

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
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
CREATE TABLE IF NOT EXISTS chat_messages (
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
CREATE TABLE IF NOT EXISTS user_sessions (
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
CREATE TABLE IF NOT EXISTS realtime_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    metric_type VARCHAR(50) DEFAULT 'counter' CHECK (metric_type IN ('counter', 'gauge', 'histogram')),
    tags JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Progress Table (for real-time updates)
CREATE TABLE IF NOT EXISTS user_progress (
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
CREATE INDEX IF NOT EXISTS idx_study_materials_user_id ON study_materials(user_id);
CREATE INDEX IF NOT EXISTS idx_study_materials_created_at ON study_materials(created_at);
CREATE INDEX IF NOT EXISTS idx_study_materials_starred ON study_materials(starred);
CREATE INDEX IF NOT EXISTS idx_study_materials_ai_analysis ON study_materials USING GIN(ai_analysis);
CREATE INDEX IF NOT EXISTS idx_study_materials_content_search ON study_materials USING GIN(to_tsvector('english', content));

-- AI Enhancement Indexes
CREATE INDEX IF NOT EXISTS idx_learning_paths_user_id ON learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_content_recommendations_user_id ON content_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_predictions_user_id ON performance_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_weakness_analysis_user_id ON weakness_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_user_id ON ai_insights(user_id);

-- Real-time Indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_seen ON user_sessions(last_seen);
CREATE INDEX IF NOT EXISTS idx_realtime_analytics_user_id ON realtime_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE study_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_folders ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_folder_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE weakness_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE realtime_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;

-- Study Materials RLS Policies
CREATE POLICY "Users can view their own materials" ON study_materials FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own materials" ON study_materials FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own materials" ON study_materials FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own materials" ON study_materials FOR DELETE USING (auth.uid() = user_id);

-- AI Enhancement RLS Policies
CREATE POLICY "Users can view their own learning paths" ON learning_paths FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own learning paths" ON learning_paths FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own learning paths" ON learning_paths FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own learning paths" ON learning_paths FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own preferences" ON user_preferences FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own preferences" ON user_preferences FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own preferences" ON user_preferences FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own recommendations" ON content_recommendations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own predictions" ON performance_predictions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own weakness analysis" ON weakness_analysis FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can view their own insights" ON ai_insights FOR SELECT USING (auth.uid() = user_id);

-- Real-time RLS Policies
CREATE POLICY "Users can view their own notifications" ON notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own notifications" ON notifications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "System can insert notifications" ON notifications FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view messages they sent or received" ON chat_messages FOR SELECT USING (auth.uid() = user_id OR auth.uid() = recipient_id OR recipient_id IS NULL);
CREATE POLICY "Users can insert their own messages" ON chat_messages FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own sessions" ON user_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own sessions" ON user_sessions FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own analytics" ON realtime_analytics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "System can insert analytics" ON realtime_analytics FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view their own progress" ON user_progress FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own progress" ON user_progress FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own progress" ON user_progress FOR INSERT WITH CHECK (auth.uid() = user_id);

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
CREATE TRIGGER update_study_materials_updated_at BEFORE UPDATE ON study_materials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_learning_paths_updated_at BEFORE UPDATE ON learning_paths FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_sessions_updated_at BEFORE UPDATE ON user_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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
    INSERT INTO notifications (user_id, title, message, type, action_url, metadata)
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
    INSERT INTO user_activity_log (user_id, activity_type, activity_data)
    VALUES (p_user_id, p_activity_type, p_activity_data)
    RETURNING id INTO activity_id;
    RETURN activity_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ENABLE REALTIME FOR SUPABASE
-- =====================================================

-- Enable realtime for tables that need live updates
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;
ALTER PUBLICATION supabase_realtime ADD TABLE chat_messages;
ALTER PUBLICATION supabase_realtime ADD TABLE user_progress;
ALTER PUBLICATION supabase_realtime ADD TABLE realtime_analytics;

-- =====================================================
-- SAMPLE DATA (OPTIONAL)
-- =====================================================

-- Insert sample study materials
INSERT INTO study_materials (
    user_id, filename, file_type, content, ai_analysis, word_count, char_count
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    'Calculus Fundamentals.pdf',
    'application/pdf',
    'Calculus is the mathematical study of continuous change...',
    '{"summary": "Introduction to calculus concepts", "key_topics": ["derivatives", "integrals"], "difficulty_level": "intermediate"}'::JSONB,
    150, 850
) ON CONFLICT DO NOTHING;

-- Insert sample user preferences
INSERT INTO user_preferences (user_id, learning_style, preferred_difficulty, favorite_subjects, learning_goals, available_time)
VALUES ('00000000-0000-0000-0000-000000000000', 'visual', 'medium', ARRAY['mathematics', 'science'], ARRAY['improve_problem_solving'], 45)
ON CONFLICT (user_id) DO NOTHING;

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON study_materials TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON material_folders TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON material_folder_assignments TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON material_quizzes TO authenticated;
GRANT SELECT, INSERT ON material_analytics TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON learning_paths TO authenticated;
GRANT SELECT, INSERT, UPDATE ON user_preferences TO authenticated;
GRANT SELECT ON content_recommendations TO authenticated;
GRANT SELECT ON performance_predictions TO authenticated;
GRANT SELECT ON weakness_analysis TO authenticated;
GRANT SELECT ON ai_insights TO authenticated;
GRANT SELECT, UPDATE ON notifications TO authenticated;
GRANT SELECT, INSERT ON chat_messages TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_sessions TO authenticated;
GRANT SELECT ON realtime_analytics TO authenticated;
GRANT SELECT, INSERT, UPDATE ON user_progress TO authenticated;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

-- This completes the database setup for EduSense
-- All tables, indexes, RLS policies, and functions are now created
-- You can now use the real-time features, AI enhancements, and study materials system
