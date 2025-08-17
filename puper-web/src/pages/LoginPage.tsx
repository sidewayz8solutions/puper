import React, { useState } from 'react';

import {
  Eye,
  EyeOff,
  LogIn,
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import {
  Link,
  useNavigate,
} from 'react-router-dom';
import { z } from 'zod';

import { zodResolver } from '@hookform/resolvers/zod';

import { authAPI } from '../lib/api';
import { useAuthStore } from '../lib/store';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

const LoginPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      const response = await authAPI.login(data);
      const { access_token, user } = response.data;
      
      login(user, access_token);
      toast.success('Welcome back!');
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-primary-100 to-primary-200 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-6">
            <PuperLogo size="xl" showText={false} />
          </div>
          <h1 className="text-4xl font-display font-bold text-primary-800 mb-2">
            Welcome to Puper
          </h1>
          <p className="text-primary-600">
            The Waze of Public Restrooms
          </p>
        </div>

        {/* Login Form */}
        <div className="card">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-primary-700 mb-2">
                Username
              </label>
              <input
                {...register('username')}
                type="text"
                id="username"
                className="input-primary"
                placeholder="Enter your username"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-error">{errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-primary-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  className="input-primary pr-10"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-primary-400 hover:text-primary-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-error">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-psychedelic w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>Sign In</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-primary-600">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="font-medium text-psychedelic-purple hover:text-psychedelic-pink transition-colors"
              >
                Sign up
              </Link>
            </p>
          </div>
        </div>

        {/* Features Preview */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          <div className="glass p-4 rounded-lg">
            <div className="w-8 h-8 bg-psychedelic-purple rounded-lg flex items-center justify-center mx-auto mb-2">
              <span className="text-white text-sm">🗺️</span>
            </div>
            <p className="text-xs text-primary-700 font-medium">Smart Maps</p>
          </div>
          
          <div className="glass p-4 rounded-lg">
            <div className="w-8 h-8 bg-psychedelic-pink rounded-lg flex items-center justify-center mx-auto mb-2">
              <span className="text-white text-sm">⭐</span>
            </div>
            <p className="text-xs text-primary-700 font-medium">Reviews</p>
          </div>
          
          <div className="glass p-4 rounded-lg">
            <div className="w-8 h-8 bg-psychedelic-orange rounded-lg flex items-center justify-center mx-auto mb-2">
              <span className="text-white text-sm">🏆</span>
            </div>
            <p className="text-xs text-primary-700 font-medium">Rewards</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
