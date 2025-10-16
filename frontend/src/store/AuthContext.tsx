/**
 * Контекст аутентификации для Timly
 * Управление состоянием пользователя и JWT токена
 */
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { User, LoginRequest, RegisterRequest, AuthToken } from '@/types';
import { apiClient } from '@/services/api';

// Типы для состояния аутентификации
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Типы действий
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: User }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'UPDATE_USER'; payload: Partial<User> };

// Начальное состояние
// isLoading: true - чтобы дать время на проверку токена при загрузке
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Reducer для управления состоянием
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };

    case 'LOGOUT':
      return {
        ...initialState,
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    case 'UPDATE_USER':
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload } : null,
      };

    default:
      return state;
  }
};

// Контекст
interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  updateHHToken: (token: string) => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Провайдер контекста
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Проверка текущей сессии при загрузке
  useEffect(() => {
    const initializeAuth = async () => {
      const hasToken = apiClient.hasToken();
      console.log('[AuthContext] Initializing auth, hasToken:', hasToken);

      if (hasToken) {
        try {
          const user = await apiClient.getProfile();
          console.log('[AuthContext] Profile loaded successfully:', user.email);
          dispatch({ type: 'AUTH_SUCCESS', payload: user });
        } catch (error: any) {
          console.error('[AuthContext] Failed to load profile:', error?.response?.status, error?.message);

          // Не удаляем токен сразу - даем refresh token шанс сработать
          // Токен будет удален interceptor'ом если refresh тоже не сработает
          if (error?.response?.status === 401) {
            console.log('[AuthContext] 401 error, will try refresh token via interceptor');
            dispatch({ type: 'AUTH_FAILURE', payload: 'Сессия истекла' });
          } else {
            // Для других ошибок (сеть, сервер) - оставляем токен
            console.log('[AuthContext] Non-auth error, keeping token');
            dispatch({ type: 'AUTH_FAILURE', payload: 'Ошибка загрузки профиля' });
          }
        }
      } else {
        // Если токена нет - сразу останавливаем загрузку
        console.log('[AuthContext] No token found, stopping loading');
        dispatch({ type: 'AUTH_FAILURE', payload: 'Не авторизован' });
      }
    };

    initializeAuth();
  }, []);

  // Метод входа
  const login = async (credentials: LoginRequest): Promise<void> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const tokenData = await apiClient.login(credentials);
      const user = await apiClient.getProfile();

      dispatch({ type: 'AUTH_SUCCESS', payload: user });
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || 'Ошибка входа в систему';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  // Метод регистрации
  const register = async (userData: RegisterRequest): Promise<void> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const user = await apiClient.register(userData);

      // После регистрации автоматически входим
      await login({ email: userData.email, password: userData.password });
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || 'Ошибка регистрации';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  // Метод выхода
  const logout = async (): Promise<void> => {
    try {
      await apiClient.logout();
    } catch (error) {
      // Игнорируем ошибки при выходе
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
    }
  };

  // Обновление профиля пользователя
  const refreshProfile = async (): Promise<void> => {
    try {
      const user = await apiClient.getProfile();
      dispatch({ type: 'UPDATE_USER', payload: user });
    } catch (error: any) {
      console.error('Profile refresh error:', error);
      // Если профиль не удалось загрузить, возможно токен недействителен
      if (error?.response?.status === 401) {
        dispatch({ type: 'LOGOUT' });
      }
    }
  };

  // Обновление HH.ru токена
  const updateHHToken = async (token: string): Promise<void> => {
    try {
      await apiClient.updateHHToken(token);
      // Обновляем профиль после успешного сохранения токена
      await refreshProfile();
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || 'Ошибка сохранения HH.ru токена';
      throw new Error(errorMessage);
    }
  };

  // Очистка ошибки
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshProfile,
    updateHHToken,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Хук для использования контекста
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;