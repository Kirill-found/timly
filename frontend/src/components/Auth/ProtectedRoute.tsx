/**
 * Защищенный роут для аутентифицированных пользователей
 * Перенаправляет на страницу входа если пользователь не авторизован
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/store/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Показываем загрузчик пока проверяем аутентификацию
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="mt-4 text-muted-foreground">Проверка авторизации...</p>
      </div>
    );
  }

  // Если пользователь не авторизован - перенаправляем на логин
  if (!isAuthenticated || !user) {
    return (
      <Navigate
        to="/login"
        state={{ from: location }}
        replace
      />
    );
  }

  // Если авторизован - показываем защищенный контент
  return <>{children}</>;
};

export default ProtectedRoute;