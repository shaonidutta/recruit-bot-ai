import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from '../pages/auth/LoginPage.jsx';
import SignupPage from '../pages/auth/SignupPage.jsx';
import DashboardPage from '../pages/dashboard/DashboardPage.jsx';
import ProtectedRoute from './ProtectedRoute.jsx';
import { ROUTES } from '../utils/constants.js';

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path={ROUTES.LOGIN} element={<LoginPage />} />
      <Route path={ROUTES.SIGNUP} element={<SignupPage />} />
      
      {/* Protected Routes */}
      <Route 
        path={ROUTES.DASHBOARD} 
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />
      
      {/* Default redirect */}
      <Route path="/" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
      
      {/* Catch all - redirect to dashboard */}
      <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
    </Routes>
  );
};

export default AppRoutes;
