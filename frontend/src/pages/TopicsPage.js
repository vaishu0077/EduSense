import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { 
  BookOpen, 
  Clock, 
  Users, 
  Star, 
  Search, 
  Filter,
  Play,
  Brain,
  TrendingUp
} from 'lucide-react';
import { api } from '../services/api';

export const TopicsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedGrade, setSelectedGrade] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');

  const { data: topics, isLoading, error } = useQuery(
    ['topics', { subject: selectedSubject, grade_level: selectedGrade }],
    () => api.content.getTopics({
      subject: selectedSubject || undefined,
      grade_level: selectedGrade || undefined,
    }),
    {
      select: (response) => response.data,
    }
  );

  const subjects = [
    'Mathematics', 'Science', 'English', 'History', 'Geography',
    'Physics', 'Chemistry', 'Biology', 'Computer Science', 'Art'
  ];

  const gradeLevels = [
    'Elementary', 'Middle School', 'High School', 'College'
  ];

  const difficulties = [
    'Easy', 'Medium', 'Hard'
  ];

  const filteredTopics = topics?.filter(topic => {
    const matchesSearch = topic.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         topic.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDifficulty = !selectedDifficulty || topic.difficulty_level === selectedDifficulty.toLowerCase();
    
    return matchesSearch && matchesDifficulty;
  }) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-8 h-8"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading topics</h3>
        <p className="text-gray-500">Please try again later</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Topics</h1>
          <p className="text-gray-600">
            Explore educational topics and start your learning journey
          </p>
        </div>
        <Link
          to="/learning-path"
          className="btn-primary flex items-center"
        >
          <Brain className="h-4 w-4 mr-2" />
          AI Learning Path
        </Link>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search topics..."
              className="input-field pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Subject Filter */}
          <select
            className="input-field"
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
          >
            <option value="">All Subjects</option>
            {subjects.map(subject => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>

          {/* Grade Level Filter */}
          <select
            className="input-field"
            value={selectedGrade}
            onChange={(e) => setSelectedGrade(e.target.value)}
          >
            <option value="">All Grades</option>
            {gradeLevels.map(grade => (
              <option key={grade} value={grade}>{grade}</option>
            ))}
          </select>

          {/* Difficulty Filter */}
          <select
            className="input-field"
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
          >
            <option value="">All Difficulties</option>
            {difficulties.map(difficulty => (
              <option key={difficulty} value={difficulty}>{difficulty}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Topics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTopics.map((topic) => (
          <div key={topic.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {topic.name}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  {topic.description || 'No description available'}
                </p>
              </div>
              <span className={`badge ${
                topic.difficulty_level === 'easy' ? 'badge-success' :
                topic.difficulty_level === 'medium' ? 'badge-warning' :
                'badge-error'
              }`}>
                {topic.difficulty_level}
              </span>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-center text-sm text-gray-500">
                <BookOpen className="h-4 w-4 mr-2" />
                {topic.subject}
              </div>
              <div className="flex items-center text-sm text-gray-500">
                <Users className="h-4 w-4 mr-2" />
                {topic.grade_level}
              </div>
              {topic.estimated_duration && (
                <div className="flex items-center text-sm text-gray-500">
                  <Clock className="h-4 w-4 mr-2" />
                  {topic.estimated_duration} minutes
                </div>
              )}
            </div>

            {topic.tags && topic.tags.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                  {topic.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="badge badge-secondary text-xs">
                      {tag}
                    </span>
                  ))}
                  {topic.tags.length > 3 && (
                    <span className="badge badge-secondary text-xs">
                      +{topic.tags.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}

            <div className="flex space-x-2">
              <Link
                to={`/topics/${topic.id}`}
                className="btn-primary flex-1 flex items-center justify-center"
              >
                <Play className="h-4 w-4 mr-2" />
                Start Learning
              </Link>
              <button className="btn-secondary flex items-center justify-center px-3">
                <Star className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredTopics.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No topics found</h3>
          <p className="text-gray-500 mb-4">
            Try adjusting your search criteria or check back later for new content.
          </p>
          <button
            onClick={() => {
              setSearchTerm('');
              setSelectedSubject('');
              setSelectedGrade('');
              setSelectedDifficulty('');
            }}
            className="btn-primary"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <BookOpen className="h-8 w-8 text-primary-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{topics?.length || 0}</h3>
          <p className="text-gray-600">Total Topics</p>
        </div>
        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">
            {topics?.filter(t => t.difficulty_level === 'easy').length || 0}
          </h3>
          <p className="text-gray-600">Beginner Friendly</p>
        </div>
        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <Brain className="h-8 w-8 text-purple-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">
            {new Set(topics?.map(t => t.subject)).size || 0}
          </h3>
          <p className="text-gray-600">Subjects Covered</p>
        </div>
      </div>
    </div>
  );
};
