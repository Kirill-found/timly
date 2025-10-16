/**
 * Главный компонент приложения Timly
 * Роутинг и провайдеры состояния
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import { AuthProvider } from '@/store/AuthContext';
import { AppProvider } from '@/store/AppContext';

// Страницы
import Landing from '@/pages/Landing';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import Sync from '@/pages/Sync';
import Analysis from '@/pages/Analysis';
import Settings from '@/pages/Settings';
import Export from '@/pages/Export';
import Results from '@/pages/Results';
import HHCallback from '@/pages/HHCallback';
import HHCallbackPublic from '@/pages/HHCallbackPublic';
import Pricing from '@/pages/Pricing';
import Admin from '@/pages/Admin';

// Компоненты
import ProtectedRoute from '@/components/Auth/ProtectedRoute';
import AppLayout from '@/components/Layout/AppLayout';
import { DataLoader } from '@/components/DataLoader';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppProvider>
        <DataLoader />
        <Router>
          <Routes>
            {/* Публичные страницы */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/auth/hh-callback" element={<HHCallbackPublic />} />

            {/* Временные страницы-заглушки */}

            <Route
              path="/demo"
              element={
                <div className="min-h-screen bg-background flex items-center justify-center p-24">
                  <div className="text-center space-y-4">
                    <h2 className="text-2xl font-semibold">Демо Timly</h2>
                    <p className="text-muted-foreground">Интерактивное демо будет реализовано</p>
                    <a href="/" className="text-primary hover:underline">← На главную</a>
                  </div>
                </div>
              }
            />

            {/* Защищенные страницы */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Dashboard />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/analysis"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Analysis />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/sync"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Sync />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Settings />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/settings/hh-callback"
              element={
                <ProtectedRoute>
                  <HHCallback />
                </ProtectedRoute>
              }
            />

            <Route
              path="/export"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Export />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/results"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Results />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/pricing"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Pricing />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin"
              element={
                <ProtectedRoute adminOnly>
                  <AppLayout>
                    <Admin />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* 404 и редиректы */}
            <Route path="/404" element={
              <div className="min-h-screen bg-background flex items-center justify-center p-24">
                <div className="text-center space-y-4">
                  <h1 className="text-4xl font-bold">404</h1>
                  <p className="text-muted-foreground">Страница не найдена</p>
                  <a href="/" className="text-primary hover:underline">← На главную</a>
                </div>
              </div>
            } />

            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </Router>
      </AppProvider>
    </AuthProvider>
  );
};

export default App;