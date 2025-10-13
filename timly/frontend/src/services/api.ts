/**
 * Сервис для работы с API
 */
import axios, { AxiosInstance } from 'axios';

// Базовая конфигурация axios
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерсептор для добавления токена к запросам
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерсептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен истёк или невалидный
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Типы данных
export interface User {
  id: string;
  email: string;
  company_name?: string;
  token_verified: boolean;
  created_at: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData extends LoginData {
  company_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Vacancy {
  id: string;
  hh_vacancy_id: string;
  title: string;
  company_name?: string;
  last_synced_at?: string;
  created_at: string;
  applications_count?: number;
}

export interface Application {
  id: string;
  hh_application_id: string;
  hh_resume_id?: string;
  candidate_name?: string;
  candidate_email?: string;
  candidate_phone?: string;
  score?: number;
  ai_summary?: string;
  status: string;
  processed_at?: string;
  created_at: string;
}

export interface AnalysisResult {
  score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  recommendation: string;
  key_skills_match?: {
    matched: string[];
    missing: string[];
  };
}

// API методы

// Аутентификация
export const authAPI = {
  login: (data: LoginData) => api.post<TokenResponse>('/auth/login', data),
  register: (data: RegisterData) => api.post<TokenResponse>('/auth/register', data),
  getMe: () => api.get<User>('/auth/me'),
};

// Настройки
export const settingsAPI = {
  updateHHToken: (token: string) => 
    api.post('/settings/hh-token', { hh_token: token }),
  verifyHHToken: () => 
    api.get<{ has_token: boolean; token_verified: boolean; message: string }>('/settings/hh-token/verify'),
  deleteHHToken: () => 
    api.delete('/settings/hh-token'),
};

// Вакансии
export const vacanciesAPI = {
  sync: (force_update = false) => 
    api.post<{ message: string; synced_count: number }>('/vacancies/sync', { force_update }),
  getList: () => 
    api.get<Vacancy[]>('/vacancies/'),
  getApplications: (vacancyId: string) => 
    api.get<Application[]>(`/vacancies/${vacancyId}/applications`),
  analyze: (vacancyId: string, analyzeAll = false) => 
    api.post(`/vacancies/${vacancyId}/analyze`, { 
      vacancy_id: vacancyId,
      analyze_all: analyzeAll 
    }),
};

export default api;