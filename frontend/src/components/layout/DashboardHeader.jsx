import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

const DashboardHeader = ({ onMenuClick }) => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b border-slate-200 h-16">
      <div className="flex items-center justify-between h-full px-4 lg:px-6">
        {/* Left side - Mobile menu + Live Badge */}
        <div className="flex items-center space-x-4">
          {/* Mobile menu button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <Badge variant="success" className="animate-pulse">
            Live
          </Badge>
        </div>

        {/* Right side - User menu */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <div className="relative">
            <button className="p-2 text-slate-400 hover:text-slate-600 transition-colors">
              <span className="text-lg">🔔</span>
              <Badge 
                variant="destructive" 
                className="absolute -top-1 -right-1 w-5 h-5 text-xs flex items-center justify-center p-0"
              >
                3
              </Badge>
            </button>
          </div>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-slate-900">
                {user?.name}
              </p>
              <p className="text-xs text-slate-500">
                {user?.email}
              </p>
            </div>
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-sm">
                {user?.name?.charAt(0)?.toUpperCase() || '?'}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={logout}
              className="text-slate-600 hover:text-slate-900"
            >
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;
