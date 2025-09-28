-- Study Materials Database Schema
-- This extends the existing EduSense database with study materials functionality

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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_study_materials_user_id ON study_materials(user_id);
CREATE INDEX IF NOT EXISTS idx_study_materials_created_at ON study_materials(created_at);
CREATE INDEX IF NOT EXISTS idx_study_materials_starred ON study_materials(starred);
CREATE INDEX IF NOT EXISTS idx_study_materials_ai_analysis ON study_materials USING GIN(ai_analysis);

CREATE INDEX IF NOT EXISTS idx_material_folders_user_id ON material_folders(user_id);
CREATE INDEX IF NOT EXISTS idx_material_folders_parent ON material_folders(parent_folder_id);

CREATE INDEX IF NOT EXISTS idx_material_quizzes_material_id ON material_quizzes(material_id);
CREATE INDEX IF NOT EXISTS idx_material_quizzes_user_id ON material_quizzes(user_id);

CREATE INDEX IF NOT EXISTS idx_material_analytics_material_id ON material_analytics(material_id);
CREATE INDEX IF NOT EXISTS idx_material_analytics_user_id ON material_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_material_analytics_action ON material_analytics(action);

-- Create full-text search index for content
CREATE INDEX IF NOT EXISTS idx_study_materials_content_search ON study_materials USING GIN(to_tsvector('english', content));

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_study_materials_updated_at 
    BEFORE UPDATE ON study_materials 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to extract key topics from AI analysis
CREATE OR REPLACE FUNCTION extract_material_topics(analysis JSONB)
RETURNS TEXT[] AS $$
BEGIN
    IF analysis IS NULL THEN
        RETURN ARRAY[]::TEXT[];
    END IF;
    
    RETURN COALESCE(
        (analysis->>'key_topics')::TEXT[],
        ARRAY[]::TEXT[]
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create function to get material difficulty
CREATE OR REPLACE FUNCTION get_material_difficulty(analysis JSONB)
RETURNS TEXT AS $$
BEGIN
    IF analysis IS NULL THEN
        RETURN 'intermediate';
    END IF;
    
    RETURN COALESCE(
        analysis->>'difficulty_level',
        'intermediate'
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create function to get material subject
CREATE OR REPLACE FUNCTION get_material_subject(analysis JSONB)
RETURNS TEXT AS $$
BEGIN
    IF analysis IS NULL THEN
        RETURN 'general';
    END IF;
    
    RETURN COALESCE(
        analysis->>'subject_category',
        'general'
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create view for material statistics
CREATE OR REPLACE VIEW material_stats AS
SELECT 
    sm.user_id,
    COUNT(*) as total_materials,
    COUNT(*) FILTER (WHERE sm.starred = TRUE) as starred_materials,
    COUNT(*) FILTER (WHERE sm.ai_analysis IS NOT NULL) as analyzed_materials,
    AVG(sm.word_count) as avg_word_count,
    SUM(sm.word_count) as total_words,
    COUNT(DISTINCT get_material_subject(sm.ai_analysis)) as unique_subjects,
    COUNT(DISTINCT get_material_difficulty(sm.ai_analysis)) as unique_difficulties
FROM study_materials sm
GROUP BY sm.user_id;

-- Create view for recent materials
CREATE OR REPLACE VIEW recent_materials AS
SELECT 
    sm.*,
    get_material_subject(sm.ai_analysis) as subject,
    get_material_difficulty(sm.ai_analysis) as difficulty,
    extract_material_topics(sm.ai_analysis) as topics
FROM study_materials sm
ORDER BY sm.created_at DESC;

-- No hardcoded demo materials - only user-uploaded materials will be stored

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON study_materials TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON material_folders TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON material_folder_assignments TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON material_quizzes TO authenticated;
GRANT SELECT, INSERT ON material_analytics TO authenticated;

GRANT SELECT ON material_stats TO authenticated;
GRANT SELECT ON recent_materials TO authenticated;

-- Enable Row Level Security
ALTER TABLE study_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_folders ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_folder_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_analytics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view their own materials" ON study_materials
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own materials" ON study_materials
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own materials" ON study_materials
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own materials" ON study_materials
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own folders" ON material_folders
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own folders" ON material_folders
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own folders" ON material_folders
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own folders" ON material_folders
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own folder assignments" ON material_folder_assignments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM study_materials sm 
            WHERE sm.id = material_id AND sm.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own folder assignments" ON material_folder_assignments
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM study_materials sm 
            WHERE sm.id = material_id AND sm.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own folder assignments" ON material_folder_assignments
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM study_materials sm 
            WHERE sm.id = material_id AND sm.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view their own material quizzes" ON material_quizzes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own material quizzes" ON material_quizzes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own material analytics" ON material_analytics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own material analytics" ON material_analytics
    FOR INSERT WITH CHECK (auth.uid() = user_id);
