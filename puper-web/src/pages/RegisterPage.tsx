import React, { useState } from 'react';

import {
  Eye,
  EyeOff,
  UserPlus,
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

const registerSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Invalid email address'),
  full_name: z.string().min(1, 'Full name is required'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type RegisterForm = z.infer<typeof registerSchema>;

const RegisterPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    try {
      const { confirmPassword, ...registerData } = data;
      const response = await authAPI.register(registerData);
      const { access_token, user } = response.data;
      
      login(user, access_token);
      toast.success('Welcome to Puper!');
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed');
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
            Join Puper
          </h1>
          <p className="text-primary-600">
            Start your restroom discovery journey
          </p>
        </div>

        {/* Register Form */}
        <div className="card">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-primary-700 mb-2">
                Full Name
              </label>
              <input
                {...register('full_name')}
                type="text"
                id="full_name"
                className="input-primary"
                placeholder="Enter your full name"
              />
              {errors.full_name && (
                <p className="mt-1 text-sm text-error">{errors.full_name.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-primary-700 mb-2">
                Username
              </label>
              <input
                {...register('username')}
                type="text"
                id="username"
                className="input-primary"
                placeholder="Choose a username"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-error">{errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-primary-700 mb-2">
                Email
              </label>
              <input
                {...register('email')}
                type="email"
                id="email"
                className="input-primary"
                placeholder="Enter your email"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-error">{errors.email.message}</p>
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
                  placeholder="Create a password"
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

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-primary-700 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  {...register('confirmPassword')}
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  className="input-primary pr-10"
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-primary-400 hover:text-primary-600"
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-error">{errors.confirmPassword.message}</p>
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
                  <UserPlus className="w-5 h-5" />
                  <span>Create Account</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-primary-600">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-medium text-psychedelic-purple hover:text-psychedelic-pink transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Benefits */}
        <div className="mt-8 space-y-3">
          <div className="glass p-3 rounded-lg flex items-center space-x-3">
            <div className="w-8 h-8 bg-psychedelic-lime rounded-lg flex items-center justify-center">
              <span className="text-white text-sm">🎯</span>
            </div>
            <p className="text-sm text-primary-700">Find restrooms anywhere, anytime</p>
          </div>
          
          <div className="glass p-3 rounded-lg flex items-center space-x-3">
            <div className="w-8 h-8 bg-psychedelic-cyan rounded-lg flex items-center justify-center">
              <span className="text-white text-sm">🏆</span>
            </div>
            <p className="text-sm text-primary-700">Earn points and badges for contributions</p>
          </div>
          
          <div className="glass p-3 rounded-lg flex items-center space-x-3">
            <div className="w-8 h-8 bg-psychedelic-yellow rounded-lg flex items-center justify-center">
              <span className="text-white text-sm">👥</span>
            </div>
            <p className="text-sm text-primary-700">Join a community of helpful travelers</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
