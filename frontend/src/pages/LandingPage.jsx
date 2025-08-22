import React, { useState, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import Logo from '../components/ui/Logo';
import { ROUTES } from '../utils/constants';
import { useAuth } from '../context/AuthContext';
import { Menu, X } from 'lucide-react';

const LandingPage = () => {
  const { isAuthenticated } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToSection = useCallback((sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    setMobileMenuOpen(false);
  }, []);

  // Memoize navigation items to prevent unnecessary re-renders
  const navigationItems = useMemo(() => [
    { id: 'features', label: 'Features' },
    { id: 'about', label: 'About' }
  ], []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="relative z-50 bg-white/90 backdrop-blur-md border-b border-gray-200/50 sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <Logo size="default" className="cursor-pointer" onClick={() => scrollToSection('hero')} />

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-8" role="navigation" aria-label="Main navigation">
              <button
                onClick={() => scrollToSection('features')}
                className="text-gray-600 hover:text-blue-600 transition-colors font-medium hover:scale-105 transform duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md px-2 py-1"
                aria-label="Navigate to Features section"
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection('about')}
                className="text-gray-600 hover:text-blue-600 transition-colors font-medium hover:scale-105 transform duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md px-2 py-1"
                aria-label="Navigate to About section"
              >
                About
              </button>
              <div className="flex items-center space-x-4">
                {isAuthenticated ? (
                  <Link to={ROUTES.DASHBOARD}>
                    <Button variant="default" size="sm" className="hover:scale-105 transform transition-all duration-200">
                      Dashboard
                    </Button>
                  </Link>
                ) : (
                  <>
                    <Link to={ROUTES.LOGIN}>
                      <Button variant="ghost" size="sm" className="hover:scale-105 transform transition-all duration-200">
                        Login
                      </Button>
                    </Link>
                    <Link to={ROUTES.SIGNUP}>
                      <Button variant="default" size="sm" className="hover:scale-105 transform transition-all duration-200">
                        Sign Up
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </nav>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-menu"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6" aria-hidden="true" />
              ) : (
                <Menu className="w-6 h-6" aria-hidden="true" />
              )}
            </button>
          </div>

          {/* Mobile Navigation Menu */}
          {mobileMenuOpen && (
            <div
              id="mobile-menu"
              className="md:hidden absolute top-full left-0 right-0 bg-white/95 backdrop-blur-md border-b border-gray-200/50 shadow-lg animate-slide-down"
              role="menu"
              aria-orientation="vertical"
            >
              <div className="px-4 py-6 space-y-4">
                <button
                  onClick={() => scrollToSection('features')}
                  className="block w-full text-left text-gray-600 hover:text-blue-600 transition-colors font-medium py-3 px-2 rounded-lg hover:bg-blue-50 active:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  role="menuitem"
                  tabIndex={0}
                >
                  Features
                </button>
                <button
                  onClick={() => scrollToSection('about')}
                  className="block w-full text-left text-gray-600 hover:text-blue-600 transition-colors font-medium py-3 px-2 rounded-lg hover:bg-blue-50 active:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  role="menuitem"
                  tabIndex={0}
                >
                  About
                </button>
                <div className="pt-4 border-t border-gray-200 space-y-3">
                  {isAuthenticated ? (
                    <Link to={ROUTES.DASHBOARD} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="default" size="sm" className="w-full touch-manipulation">
                        Dashboard
                      </Button>
                    </Link>
                  ) : (
                    <>
                      <Link to={ROUTES.LOGIN} onClick={() => setMobileMenuOpen(false)}>
                        <Button variant="ghost" size="sm" className="w-full touch-manipulation">
                          Login
                        </Button>
                      </Link>
                      <Link to={ROUTES.SIGNUP} onClick={() => setMobileMenuOpen(false)}>
                        <Button variant="default" size="sm" className="w-full touch-manipulation">
                          Sign Up
                        </Button>
                      </Link>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section id="hero" className="relative py-20 lg:py-32 overflow-hidden" aria-labelledby="hero-heading">
        {/* Animated Background decoration */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-600/5"></div>
        <div className="absolute top-0 left-0 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 animate-pulse-slow"></div>
        <div className="absolute bottom-0 right-0 w-72 h-72 bg-purple-600/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 animate-pulse-slow" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 animate-pulse-slow" style={{animationDelay: '2s'}}></div>

        {/* Floating elements */}
        <div className="absolute top-20 left-10 w-4 h-4 bg-blue-400/30 rounded-full animate-bounce" style={{animationDelay: '0.5s'}}></div>
        <div className="absolute top-40 right-20 w-6 h-6 bg-purple-400/30 rounded-full animate-bounce" style={{animationDelay: '1.5s'}}></div>
        <div className="absolute bottom-40 left-20 w-3 h-3 bg-indigo-400/30 rounded-full animate-bounce" style={{animationDelay: '2.5s'}}></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-4xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-sm font-medium mb-8 animate-fade-in">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
              Now with Advanced AI Matching
            </div>

            <h1 id="hero-heading" className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight animate-slide-up">
              AI-Powered
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Recruitment</span>
              <br className="hidden sm:block" />
              <span className="sm:hidden"> </span>at Scale
            </h1>

            <p className="text-lg sm:text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed animate-slide-up px-4 sm:px-0" style={{animationDelay: '0.2s'}}>
              Discover, match, and engage with top talent automatically. Our AI agents work 24/7 to find the perfect candidates for your roles.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12 animate-slide-up" style={{animationDelay: '0.4s'}}>
              {isAuthenticated ? (
                <Link to={ROUTES.DASHBOARD}>
                  <Button size="lg" className="px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 transform">
                    Go to Dashboard
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to={ROUTES.SIGNUP}>
                    <Button size="lg" className="px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 transform bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                      Get Started Free
                    </Button>
                  </Link>
                  <Link to={ROUTES.LOGIN}>
                    <Button variant="outline" size="lg" className="px-8 py-4 text-lg font-semibold hover:scale-105 transform transition-all duration-300 border-2 hover:border-blue-500 hover:text-blue-600">
                      Sign In
                    </Button>
                  </Link>
                </>
              )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto animate-slide-up" style={{animationDelay: '0.6s'}}>
              <div className="text-center group">
                <div className="text-3xl font-bold text-blue-600 mb-2 group-hover:scale-110 transition-transform duration-300">10,000+</div>
                <div className="text-gray-600 group-hover:text-gray-800 transition-colors">Jobs Processed</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-purple-600 mb-2 group-hover:scale-110 transition-transform duration-300">95%</div>
                <div className="text-gray-600 group-hover:text-gray-800 transition-colors">Match Accuracy</div>
              </div>
              <div className="text-center group">
                <div className="text-3xl font-bold text-indigo-600 mb-2 group-hover:scale-110 transition-transform duration-300">24/7</div>
                <div className="text-gray-600 group-hover:text-gray-800 transition-colors">AI Monitoring</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white" aria-labelledby="features-heading">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 id="features-heading" className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to revolutionize your recruitment process
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            {/* Job Scraping Feature */}
            <div className="group bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Smart Job Scraping</h3>
              <p className="text-gray-600 mb-4">
                Automatically discover and collect job postings from multiple platforms with AI-powered filtering.
              </p>
              <div className="flex items-center text-blue-600 text-sm font-medium group-hover:text-blue-700">
                Learn more
                <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Candidate Matching Feature */}
            <div className="group bg-white rounded-xl p-6 border border-gray-200 hover:border-purple-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Candidate Matching</h3>
              <p className="text-gray-600 mb-4">
                Advanced algorithms match candidates to roles based on skills, experience, and cultural fit.
              </p>
              <div className="flex items-center text-purple-600 text-sm font-medium group-hover:text-purple-700">
                Learn more
                <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Automated Outreach Feature */}
            <div className="group bg-white rounded-xl p-6 border border-gray-200 hover:border-indigo-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Automated Outreach</h3>
              <p className="text-gray-600 mb-4">
                Personalized email campaigns and follow-ups powered by AI to engage top candidates.
              </p>
              <div className="flex items-center text-indigo-600 text-sm font-medium group-hover:text-indigo-700">
                Learn more
                <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Analytics Feature */}
            <div className="group bg-white rounded-xl p-6 border border-gray-200 hover:border-green-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Real-time Analytics</h3>
              <p className="text-gray-600 mb-4">
                Comprehensive dashboards and insights to track performance and optimize your hiring process.
              </p>
              <div className="flex items-center text-green-600 text-sm font-medium group-hover:text-green-700">
                Learn more
                <svg className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Additional Features Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Lightning Fast</h3>
              <p className="text-gray-600">Process thousands of applications in minutes, not hours.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-teal-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Secure & Compliant</h3>
              <p className="text-gray-600">Enterprise-grade security with GDPR and SOC2 compliance.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-rose-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Easy Integration</h3>
              <p className="text-gray-600">Seamlessly connects with your existing HR tools and workflows.</p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              About AI Recruitment Agent
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We're revolutionizing recruitment with cutting-edge AI technology that automates the entire hiring pipeline.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                The Future of Recruitment is Here
              </h3>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-gray-600">
                    <strong className="text-gray-900">AI-Powered Matching:</strong> Our advanced algorithms analyze thousands of data points to find the perfect candidate-job fit.
                  </p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-gray-600">
                    <strong className="text-gray-900">24/7 Automation:</strong> Never miss a great candidate with our continuous monitoring and engagement system.
                  </p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-gray-600">
                    <strong className="text-gray-900">Scalable Solution:</strong> From startups to enterprises, our platform grows with your hiring needs.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl p-8 text-white">
                <div className="text-center">
                  <div className="text-4xl font-bold mb-2">500+</div>
                  <div className="text-blue-100 mb-6">Companies Trust Us</div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-2xl font-bold">98%</div>
                      <div className="text-blue-100">Success Rate</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">50%</div>
                      <div className="text-blue-100">Time Saved</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Company Info */}
            <div className="lg:col-span-2">
              <div className="mb-4">
                <Logo size="default" className="text-white" />
              </div>
              <p className="text-gray-400 mb-6 max-w-md">
                Revolutionizing recruitment with AI-powered automation. Find, match, and engage with top talent at unprecedented speed and accuracy.
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001 12.017.001z"/>
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0C5.374 0 0 5.373 0 12s5.374 12 12 12 12-5.373 12-12S18.626 0 12 0zm5.568 8.16c-.169 1.858-.896 3.433-2.001 4.72-1.454 1.688-3.494 2.559-5.568 2.559-1.382 0-2.691-.444-3.761-1.237-.151-.112-.151-.336.056-.336.207 0 1.551.112 2.304-.224.697-.336 1.278-.896 1.692-1.617-.697-.112-1.278-.448-1.692-1.057-.336-.448-.448-.896-.448-1.393 0-.224.056-.448.168-.672.224-.448.616-.784 1.057-.896.224-.056.448-.056.672-.056h.224c.784-.112 1.568-.56 2.136-1.169.448-.448.784-1.001.896-1.617.056-.336.056-.672 0-1.001-.112-.672-.448-1.278-.896-1.729-.224-.224-.504-.392-.784-.504-.168-.056-.336-.112-.504-.112-.336 0-.672.112-.952.28-.504.336-.84.896-.952 1.505-.056.336-.056.672.056.952.112.448.336.84.672 1.113.168.168.392.28.616.336.112.056.224.056.336.056.224 0 .448-.056.616-.168.336-.224.504-.616.504-1.001 0-.168-.056-.336-.112-.448-.112-.224-.28-.392-.504-.448-.112-.056-.224-.056-.336-.056-.168 0-.336.056-.448.168-.056.056-.112.168-.112.28 0 .112.056.168.112.224.056.056.168.056.224.056.056 0 .112 0 .112-.056 0-.056-.056-.056-.056-.112 0-.056.056-.112.112-.112.056 0 .112.056.112.112 0 .168-.112.336-.28.392-.112.056-.224.056-.336.056-.224 0-.448-.112-.616-.28-.336-.336-.448-.84-.336-1.278.168-.672.672-1.225 1.278-1.393.336-.112.728-.056 1.001.168.504.336.784.952.784 1.561 0 .784-.336 1.505-.896 1.953-.336.28-.784.392-1.225.336-.672-.112-1.225-.616-1.393-1.225-.112-.448-.056-.952.224-1.337.168-.224.392-.392.672-.448.168-.056.392-.056.56.056.224.168.336.448.336.728 0 .392-.224.728-.56.896-.224.112-.504.112-.728.056-.448-.112-.84-.448-1.001-.896-.112-.336-.112-.728.056-1.057.224-.504.672-.84 1.169-.896.336-.056.728.056.952.336.448.504.504 1.225.224 1.785-.168.336-.448.616-.784.728-.224.056-.504.056-.728-.056-.448-.224-.784-.672-.84-1.169-.056-.336.056-.728.28-.952.168-.168.392-.224.616-.224.336 0 .616.168.784.448.112.168.168.392.168.616 0 .448-.224.84-.616 1.001-.224.112-.504.056-.672-.112-.224-.224-.28-.56-.168-.84.056-.168.168-.28.336-.336.112-.056.224-.056.336.056.168.168.168.448.056.616-.056.112-.168.168-.28.168-.056 0-.112-.056-.112-.112 0-.056.056-.112.112-.112.056 0 .056-.056.056-.112 0-.056-.056-.056-.112-.056-.112 0-.168.112-.168.224 0 .224.168.392.392.392.336 0 .616-.28.616-.616 0-.504-.392-.896-.896-.896-.672 0-1.225.56-1.225 1.225 0 .896.728 1.617 1.617 1.617 1.113 0 2.001-.896 2.001-2.001 0-1.393-1.113-2.513-2.513-2.513-1.729 0-3.125 1.393-3.125 3.125 0 2.001 1.617 3.625 3.625 3.625 2.513 0 4.538-2.025 4.538-4.538 0-3.125-2.513-5.625-5.625-5.625C6.375 2.375 2.375 6.375 2.375 11.375c0 6.188 5.013 11.188 11.188 11.188 7.875 0 14.25-6.375 14.25-14.25C27.813 1.125 21.438-5.25 13.563-5.25z"/>
                  </svg>
                </a>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2">
                <li>
                  <button
                    onClick={() => scrollToSection('features')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    Features
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => scrollToSection('about')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    About
                  </button>
                </li>
                <li>
                  <Link to={ROUTES.LOGIN} className="text-gray-400 hover:text-white transition-colors">
                    Login
                  </Link>
                </li>
                <li>
                  <Link to={ROUTES.SIGNUP} className="text-gray-400 hover:text-white transition-colors">
                    Sign Up
                  </Link>
                </li>
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <ul className="space-y-2">
                <li className="text-gray-400">
                  <span className="block">Email:</span>
                  <a href="mailto:hello@airecruitment.com" className="hover:text-white transition-colors">
                    hello@airecruitment.com
                  </a>
                </li>
                <li className="text-gray-400">
                  <span className="block">Phone:</span>
                  <a href="tel:+1234567890" className="hover:text-white transition-colors">
                    +1 (234) 567-8900
                  </a>
                </li>
                <li className="text-gray-400">
                  <span className="block">Address:</span>
                  <span>123 AI Street<br />Tech City, TC 12345</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-gray-800 mt-12 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                © 2024 AI Recruitment Agent. All rights reserved.
              </p>
              <div className="flex space-x-6 mt-4 md:mt-0">
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
                  Privacy Policy
                </a>
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
                  Terms of Service
                </a>
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
                  Cookie Policy
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
