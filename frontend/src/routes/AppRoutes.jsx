import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "../pages/LandingPage.jsx";
import LoginPage from "../pages/auth/LoginPage.jsx";
import SignupPage from "../pages/auth/SignupPage.jsx";
import DashboardPage from "../pages/dashboard/DashboardPage.jsx";
import JobsPage from "../pages/jobs/JobsPage.jsx";
import CandidatesPage from "../pages/candidates/CandidatesPage.jsx";
import MatchesPage from "../pages/matches/MatchesPage.jsx";
import MatchTestPage from "../pages/MatchTestPage.jsx";
import ProtectedRoute from "./ProtectedRoute.jsx";
import { ROUTES } from "../utils/constants.js";

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
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

      <Route
        path={ROUTES.JOBS}
        element={
          <ProtectedRoute>
            <JobsPage />
          </ProtectedRoute>
        }
      />

      <Route
        path={ROUTES.CANDIDATES}
        element={
          <ProtectedRoute>
            <CandidatesPage />
          </ProtectedRoute>
        }
      />

      <Route
        path={ROUTES.MATCHES}
        element={
          <ProtectedRoute>
            <MatchesPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/match-test"
        element={
          <ProtectedRoute>
            <MatchTestPage />
          </ProtectedRoute>
        }
      />

      {/* Catch all - redirect to landing page */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
