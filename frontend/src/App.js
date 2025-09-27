import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { LoadingSpinner } from './components/LoadingSpinner';

// Pages
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { TopicsPage } from './pages/TopicsPage';
import { QuizPage } from './pages/QuizPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ProfilePage } from './pages/ProfilePage';
import { ContentPage } from './pages/ContentPage';
import { LearningPathPage } from './pages/LearningPathPage';
import { TeacherDashboardPage } from './pages/TeacherDashboardPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Protected routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/topics" element={
              <ProtectedRoute>
                <Layout>
                  <TopicsPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/topics/:topicId" element={
              <ProtectedRoute>
                <Layout>
                  <ContentPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/quiz/:quizId" element={
              <ProtectedRoute>
                <Layout>
                  <QuizPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/learning-path" element={
              <ProtectedRoute>
                <Layout>
                  <LearningPathPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/analytics" element={
              <ProtectedRoute>
                <Layout>
                  <AnalyticsPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/profile" element={
              <ProtectedRoute>
                <Layout>
                  <ProfilePage />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/teacher" element={
              <ProtectedRoute requiredRole="teacher">
                <Layout>
                  <TeacherDashboardPage />
                </Layout>
              </ProtectedRoute>
            } />
            
            {/* Redirect unknown routes to dashboard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
