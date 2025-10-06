import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { ToastProvider } from './contexts/ToastContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// Main Pages
import Dashboard from './pages/Dashboard';
import DashboardNew from './pages/DashboardNew';
import Signals from './pages/Signals';
import Positions from './pages/Positions';
import Analytics from './pages/Analytics';
import Watchlist from './pages/Watchlist';
import Settings from './pages/Settings';

// Layout
import Layout from './components/layout/Layout';
import ModernLayout from './components/ModernLayout';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <WebSocketProvider>
            <ToastProvider>
              <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <ModernLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<DashboardNew />} />
                <Route path="signals" element={<Signals />} />
                <Route path="positions" element={<Positions />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="watchlist" element={<Watchlist />} />
                <Route path="settings" element={<Settings />} />
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </ToastProvider>
          </WebSocketProvider>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
