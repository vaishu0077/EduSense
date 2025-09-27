-- Database schema for AI enhancements
-- This file contains the database schema for the new AI-powered features

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

-- Adaptive Difficulty History Table
CREATE TABLE IF NOT EXISTS adaptive_difficulty_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    topic VARCHAR(100) NOT NULL,
    previous_difficulty VARCHAR(20) NOT NULL CHECK (previous_difficulty IN ('easy', 'medium', 'hard')),
    recommended_difficulty VARCHAR(20) NOT NULL CHECK (recommended_difficulty IN ('easy', 'medium', 'hard')),
    confidence DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    reasoning TEXT,
    performance_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learning Analytics Table
CREATE TABLE IF NOT EXISTS learning_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    analytics_type VARCHAR(50) NOT NULL CHECK (analytics_type IN ('performance', 'engagement', 'progress', 'comprehensive')),
    analytics_data JSONB NOT NULL,
    time_period VARCHAR(20) DEFAULT 'weekly' CHECK (time_period IN ('daily', 'weekly', 'monthly', 'custom')),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
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

-- User Learning Profile Table
CREATE TABLE IF NOT EXISTS user_learning_profile (
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

-- Content Interaction Tracking Table
CREATE TABLE IF NOT EXISTS content_interactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content_id VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN ('view', 'start', 'complete', 'abandon', 'rate', 'bookmark')),
    interaction_data JSONB DEFAULT '{}',
    time_spent INTEGER DEFAULT 0, -- seconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learning Milestones Table
CREATE TABLE IF NOT EXISTS learning_milestones (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL CHECK (milestone_type IN ('achievement', 'streak', 'improvement', 'mastery', 'completion')),
    milestone_data JSONB NOT NULL,
    achieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    points_awarded INTEGER DEFAULT 0,
    badge_data JSONB DEFAULT '{}'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_learning_paths_user_id ON learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_paths_status ON learning_paths(status);
CREATE INDEX IF NOT EXISTS idx_learning_paths_created_at ON learning_paths(created_at);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

CREATE INDEX IF NOT EXISTS idx_content_recommendations_user_id ON content_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_content_recommendations_content_type ON content_recommendations(content_type);
CREATE INDEX IF NOT EXISTS idx_content_recommendations_expires_at ON content_recommendations(expires_at);

CREATE INDEX IF NOT EXISTS idx_performance_predictions_user_id ON performance_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_predictions_type ON performance_predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_performance_predictions_generated_at ON performance_predictions(generated_at);

CREATE INDEX IF NOT EXISTS idx_weakness_analysis_user_id ON weakness_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_weakness_analysis_type ON weakness_analysis(analysis_type);
CREATE INDEX IF NOT EXISTS idx_weakness_analysis_severity ON weakness_analysis(severity_level);

CREATE INDEX IF NOT EXISTS idx_adaptive_difficulty_user_id ON adaptive_difficulty_history(user_id);
CREATE INDEX IF NOT EXISTS idx_adaptive_difficulty_topic ON adaptive_difficulty_history(topic);
CREATE INDEX IF NOT EXISTS idx_adaptive_difficulty_created_at ON adaptive_difficulty_history(created_at);

CREATE INDEX IF NOT EXISTS idx_learning_analytics_user_id ON learning_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_analytics_type ON learning_analytics(analytics_type);
CREATE INDEX IF NOT EXISTS idx_learning_analytics_generated_at ON learning_analytics(generated_at);

CREATE INDEX IF NOT EXISTS idx_ai_insights_user_id ON ai_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_ai_insights_priority ON ai_insights(priority);

CREATE INDEX IF NOT EXISTS idx_user_learning_profile_user_id ON user_learning_profile(user_id);

CREATE INDEX IF NOT EXISTS idx_content_interactions_user_id ON content_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_content_interactions_content_id ON content_interactions(content_id);
CREATE INDEX IF NOT EXISTS idx_content_interactions_type ON content_interactions(interaction_type);

CREATE INDEX IF NOT EXISTS idx_learning_milestones_user_id ON learning_milestones(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_milestones_type ON learning_milestones(milestone_type);
CREATE INDEX IF NOT EXISTS idx_learning_milestones_achieved_at ON learning_milestones(achieved_at);

-- Row Level Security (RLS) Policies
ALTER TABLE learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE weakness_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE adaptive_difficulty_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_learning_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_milestones ENABLE ROW LEVEL SECURITY;

-- RLS Policies for learning_paths
CREATE POLICY "Users can view their own learning paths" ON learning_paths
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own learning paths" ON learning_paths
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own learning paths" ON learning_paths
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own learning paths" ON learning_paths
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for user_preferences
CREATE POLICY "Users can view their own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own preferences" ON user_preferences
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for content_recommendations
CREATE POLICY "Users can view their own recommendations" ON content_recommendations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own recommendations" ON content_recommendations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own recommendations" ON content_recommendations
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own recommendations" ON content_recommendations
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for performance_predictions
CREATE POLICY "Users can view their own predictions" ON performance_predictions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own predictions" ON performance_predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own predictions" ON performance_predictions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own predictions" ON performance_predictions
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for weakness_analysis
CREATE POLICY "Users can view their own weakness analysis" ON weakness_analysis
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own weakness analysis" ON weakness_analysis
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own weakness analysis" ON weakness_analysis
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own weakness analysis" ON weakness_analysis
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for adaptive_difficulty_history
CREATE POLICY "Users can view their own difficulty history" ON adaptive_difficulty_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own difficulty history" ON adaptive_difficulty_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own difficulty history" ON adaptive_difficulty_history
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own difficulty history" ON adaptive_difficulty_history
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for learning_analytics
CREATE POLICY "Users can view their own analytics" ON learning_analytics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own analytics" ON learning_analytics
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own analytics" ON learning_analytics
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own analytics" ON learning_analytics
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for ai_insights
CREATE POLICY "Users can view their own insights" ON ai_insights
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own insights" ON ai_insights
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own insights" ON ai_insights
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own insights" ON ai_insights
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for user_learning_profile
CREATE POLICY "Users can view their own profile" ON user_learning_profile
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile" ON user_learning_profile
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile" ON user_learning_profile
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own profile" ON user_learning_profile
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for content_interactions
CREATE POLICY "Users can view their own interactions" ON content_interactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own interactions" ON content_interactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own interactions" ON content_interactions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own interactions" ON content_interactions
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for learning_milestones
CREATE POLICY "Users can view their own milestones" ON learning_milestones
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own milestones" ON learning_milestones
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own milestones" ON learning_milestones
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own milestones" ON learning_milestones
    FOR DELETE USING (auth.uid() = user_id);

-- Functions for automatic cleanup of expired data
CREATE OR REPLACE FUNCTION cleanup_expired_recommendations()
RETURNS void AS $$
BEGIN
    DELETE FROM content_recommendations WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_expired_predictions()
RETURNS void AS $$
BEGIN
    DELETE FROM performance_predictions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_expired_analysis()
RETURNS void AS $$
BEGIN
    DELETE FROM weakness_analysis WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_expired_analytics()
RETURNS void AS $$
BEGIN
    DELETE FROM learning_analytics WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_expired_insights()
RETURNS void AS $$
BEGIN
    DELETE FROM ai_insights WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Create a comprehensive cleanup function
CREATE OR REPLACE FUNCTION cleanup_all_expired_data()
RETURNS void AS $$
BEGIN
    PERFORM cleanup_expired_recommendations();
    PERFORM cleanup_expired_predictions();
    PERFORM cleanup_expired_analysis();
    PERFORM cleanup_expired_analytics();
    PERFORM cleanup_expired_insights();
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_learning_paths_updated_at
    BEFORE UPDATE ON learning_paths
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_learning_profile_updated_at
    BEFORE UPDATE ON user_learning_profile
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
INSERT INTO user_preferences (user_id, learning_style, preferred_difficulty, favorite_subjects, learning_goals, available_time)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'visual', 'medium', ARRAY['mathematics', 'science'], ARRAY['improve_problem_solving'], 45)
ON CONFLICT (user_id) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW user_learning_summary AS
SELECT 
    u.id as user_id,
    up.learning_style,
    up.preferred_difficulty,
    up.favorite_subjects,
    up.learning_goals,
    up.available_time,
    ulp.profile_data,
    COUNT(lp.id) as total_learning_paths,
    COUNT(CASE WHEN lp.status = 'active' THEN 1 END) as active_paths,
    COUNT(CASE WHEN lp.status = 'completed' THEN 1 END) as completed_paths
FROM auth.users u
LEFT JOIN user_preferences up ON u.id = up.user_id
LEFT JOIN user_learning_profile ulp ON u.id = ulp.user_id
LEFT JOIN learning_paths lp ON u.id = lp.user_id
GROUP BY u.id, up.learning_style, up.preferred_difficulty, up.favorite_subjects, up.learning_goals, up.available_time, ulp.profile_data;

CREATE OR REPLACE VIEW recent_ai_insights AS
SELECT 
    ai.*,
    u.email as user_email
FROM ai_insights ai
JOIN auth.users u ON ai.user_id = u.id
WHERE ai.created_at > NOW() - INTERVAL '7 days'
ORDER BY ai.created_at DESC;

CREATE OR REPLACE VIEW user_performance_summary AS
SELECT 
    p.user_id,
    COUNT(p.id) as total_performances,
    AVG((p.score::decimal / p.total_questions) * 100) as avg_score,
    SUM(p.time_spent) as total_time_spent,
    COUNT(DISTINCT p.topic) as topics_studied,
    MAX(p.created_at) as last_activity
FROM performance p
GROUP BY p.user_id;
