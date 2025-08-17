import React from 'react';

import { Toaster } from 'react-hot-toast';
import {
  BrowserRouter as Router,
  Route,
  Routes,
} from 'react-router-dom';

import {
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import RegisterPage from './pages/RegisterPage';
import RestroomDetailPage from './pages/RestroomDetailPage';

// Create a client with optimized settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-primary-50 via-primary-100 to-primary-200 relative overflow-hidden">
          {/* Animated background elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-40 -right-40 w-80 h-80 bg-psychedelic-purple rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
            <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-psychedelic-pink rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float animation-delay-2000"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-psychedelic-orange rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-float animation-delay-4000"></div>
          </div>

          {/* Main app content */}
          <div className="relative z-10">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout>
                    <HomePage />
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

              <Route path="/restroom/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <RestroomDetailPage />
                  </Layout>
                </ProtectedRoute>
              } />

              {/* 404 Page */}
              <Route path="*" element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-6xl font-bold text-gradient mb-4">404</h1>
                    <p className="text-xl text-primary-700 mb-8">Oops! This restroom doesn't exist.</p>
                    <a href="/" className="btn-psychedelic">
                      Go Home
                    </a>
                  </div>
                </div>
              } />
            </Routes>
          </div>

          {/* Toast notifications with custom styling */}
          <Toaster
            position="top-right"
            reverseOrder={false}
            gutter={8}
            toastOptions={{
              duration: 4000,
              style: {
                background: 'rgba(255, 255, 255, 0.95)',
                color: '#5d4e3a',
                border: '1px solid #d2bab0',
                borderRadius: '0.75rem',
                backdropFilter: 'blur(10px)',
                boxShadow: '0 10px 40px rgba(161, 128, 114, 0.15)',
              },
              success: {
                iconTheme: {
                  primary: '#84CC16',
                  secondary: '#fff',
                },
                style: {
                  border: '1px solid #84CC16',
                },
              },
              error: {
                iconTheme: {
                  primary: '#EF4444',
                  secondary: '#fff',
                },
                style: {
                  border: '1px solid #EF4444',
                },
              },
              loading: {
                iconTheme: {
                  primary: '#8B5CF6',
                  secondary: '#fff',
                },
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;