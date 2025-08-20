import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { cn } from '../../utils/cn';

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: '📊',
    description: 'Overview & metrics'
  },
  {
    name: 'Jobs',
    href: '/jobs',
    icon: '🎯',
    description: 'Job discoveries'
  },
  {
    name: 'Candidates',
    href: '/candidates',
    icon: '👥',
    description: 'Candidate profiles'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: '⚙️',
    description: 'Configuration'
  }
];

const DashboardSidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  return (
    <div className={cn(
      "fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl border-r border-slate-200 transform transition-transform duration-300 ease-in-out",
      "lg:translate-x-0 lg:fixed lg:h-screen",
      isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
    )}>
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-6 border-b border-slate-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">Recruitment</h1>
            <p className="text-xs text-slate-500">Agent</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="mt-6 px-3">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || 
                           (item.href === '/dashboard' && location.pathname === '/');
            
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={cn(
                  'group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 border-r-2 border-blue-500'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                )}
              >
                <span className="text-lg mr-3">{item.icon}</span>
                <div className="flex-1">
                  <div className="font-medium">{item.name}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{item.description}</div>
                </div>
                {isActive && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                )}
              </NavLink>
            );
          })}
        </div>
      </nav>

      {/* Status Indicator */}
      <div className="absolute bottom-6 left-3 right-3">
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-green-800">AI System Active</span>
          </div>
          <p className="text-xs text-green-600 mt-1">
            Discovering jobs 24/7
          </p>
        </div>
      </div>
    </div>
  );
};

export default DashboardSidebar;
