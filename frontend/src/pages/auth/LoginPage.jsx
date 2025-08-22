import React, { useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import LoginForm from './components/LoginForm.jsx';
import Logo from '../../components/ui/Logo.jsx';
import { useAuth } from '../../context/AuthContext.jsx';
import { ROUTES } from '../../utils/constants.js';

const LoginPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || ROUTES.DASHBOARD;
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-600/5"></div>
      <div className="absolute top-0 left-0 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 animate-pulse-slow"></div>
      <div className="absolute bottom-0 right-0 w-72 h-72 bg-purple-600/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 animate-pulse-slow" style={{animationDelay: '1s'}}></div>

      <div className="max-w-md w-full space-y-8 relative z-10">
        {/* Header */}
        <div className="text-center animate-fade-in">
          <div className="flex justify-center mb-4">
            <Logo size="lg" />
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Superhuman speed and scale in recruitment
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-white/90 backdrop-blur-sm py-8 px-6 shadow-xl rounded-2xl border border-white/20 animate-slide-up" style={{animationDelay: '0.2s'}}>
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Welcome Back
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Sign in to your account to continue
            </p>
          </div>
          <LoginForm />
        </div>

        {/* Signup Link */}
        <div className="text-center animate-slide-up" style={{animationDelay: '0.4s'}}>
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <Link
              to={ROUTES.SIGNUP}
              className="font-medium text-blue-600 hover:text-blue-500 transition-all duration-200 hover:scale-105 inline-block"
            >
              Sign up here
            </Link>
          </p>
        </div>

        {/* Back to Landing */}
        <div className="text-center animate-slide-up" style={{animationDelay: '0.6s'}}>
          <Link
            to={ROUTES.LANDING}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
