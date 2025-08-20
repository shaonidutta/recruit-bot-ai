import React, { createContext, useContext, useReducer, useEffect, useCallback, useMemo } from 'react';
import { authService } from '../api/services/authService.js';

const AuthContext = createContext(null);

// Auth reducer following React best practices
const authReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.accessToken || action.payload.token,
        isAuthenticated: true,
        loading: false,
        error: null
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null
      };
    case 'SET_ERROR':
      return { 
        ...state, 
        error: action.payload, 
        loading: false 
      };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
};

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: true,
  error: null
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Login function with useCallback for optimization
  const login = useCallback(async (email, password) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const data = await authService.login(email, password);

      // After successful login, fetch fresh user data from auth/me
      const freshUserData = await authService.verifyToken();
      if (freshUserData) {
        dispatch({ type: 'LOGIN_SUCCESS', payload: freshUserData });
        return freshUserData;
      } else {
        dispatch({ type: 'LOGIN_SUCCESS', payload: data });
        return data;
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  }, []);

  // Register function with useCallback for optimization
  const register = useCallback(async (userData) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const data = await authService.register(userData);

      // After successful registration, fetch fresh user data from auth/me
      const freshUserData = await authService.verifyToken();
      if (freshUserData) {
        dispatch({ type: 'LOGIN_SUCCESS', payload: freshUserData });
        return freshUserData;
      } else {
        dispatch({ type: 'LOGIN_SUCCESS', payload: data });
        return data;
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  }, []);

  // Logout function with useCallback for optimization
  const logout = useCallback(() => {
    authService.logout();
    dispatch({ type: 'LOGOUT' });
  }, []);

  // Clear error function
  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  // Refresh user data from auth/me endpoint
  const refreshUserData = useCallback(async () => {
    try {
      const userData = await authService.verifyToken();
      if (userData) {
        dispatch({ type: 'LOGIN_SUCCESS', payload: userData });
        return userData;
      }
      return null;
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      dispatch({ type: 'LOGOUT' });
      return null;
    }
  }, []);

  // Check for existing token on app load
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const userData = authService.getCurrentUser();

        if (userData) {
          // Always verify token with backend and get fresh user data
          const verifiedData = await authService.verifyToken();
          if (verifiedData) {
            dispatch({ type: 'LOGIN_SUCCESS', payload: verifiedData });
          } else {
            // Token is invalid, clear storage and set loading to false
            authService.logout();
            dispatch({ type: 'SET_LOADING', payload: false });
          }
        } else {
          dispatch({ type: 'SET_LOADING', payload: false });
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        // Clear any invalid tokens
        authService.logout();
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    initializeAuth();
  }, []);

  // Memoize context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    ...state,
    login,
    register,
    logout,
    clearError,
    refreshUserData
  }), [state, login, register, logout, clearError, refreshUserData]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for using auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
