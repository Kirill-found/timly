/**
 * TypeScript типы для Timly Frontend
 * Синхронизированы с backend Pydantic схемами
 */

// Пользователь и аутентификация
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'admin';
  company_name?: string;
  has_hh_token: boolean;
  token_verified: boolean;
  created_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  company_name?: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
}

// Вакансии
export interface Vacancy {
  id: string;
  hh_vacancy_id: string;
  title: string;
  description?: string;
  key_skills: string[];
  salary?: {
    from?: number;
    to?: number;
    currency: string;
  };
  experience?: string;
  employment?: string;
  schedule?: string;
  area?: string;
  applications_count: number;
  new_applications_count: number;
  is_active: boolean;
  published_at?: string;
  last_synced_at?: string;
  created_at?: string;
}

// Отклики на вакансии
export interface Application {
  id: string;
  vacancy_id: string;
  hh_application_id: string;
  hh_resume_id?: string;
  candidate_name?: string;
  candidate_email?: string;
  candidate_phone?: string;
  resume_url?: string;
  is_duplicate: boolean;
  analyzed_at?: string;
  created_at?: string;
}

// Результаты AI анализа
export interface AnalysisResult {
  id: string;
  application_id: string;
  score?: number;
  skills_match?: number;
  experience_match?: number;
  salary_match?: 'match' | 'higher' | 'lower' | 'unknown';
  strengths: string[];
  weaknesses: string[];
  red_flags: string[];
  recommendation?: 'hire' | 'interview' | 'maybe' | 'reject';
  reasoning?: string;
  ai_model?: string;
  ai_tokens_used?: number;
  ai_cost_cents?: number;
  processing_time_ms?: number;
  created_at?: string;
  // Данные кандидата из связанного отклика
  application?: {
    candidate_name?: string;
    candidate_email?: string;
    candidate_phone?: string;
    resume_url?: string;
    created_at?: string;
  };
  // Альтернативные поля для совместимости с разными API ответами
  candidate_name?: string;
  candidate_email?: string;
  candidate_phone?: string;
  resume_url?: string;
  analyzed_at?: string;
  summary?: string;
}

// Статистика анализа
export interface AnalysisStats {
  vacancy_id: string;
  total_analyzed: number;
  avg_score?: number;
  hire_count: number;
  interview_count: number;
  maybe_count: number;
  reject_count: number;
  last_analysis_at?: string;
}

// Синхронизация с HH.ru
export interface SyncJob {
  id: string;
  status: 'pending' | 'processing' | 'running' | 'completed' | 'failed';
  vacancies_synced: number;
  applications_synced: number;
  errors: string[];
  started_at?: string;
  completed_at?: string;
  created_at?: string;
}

export interface SyncJobRequest {
  sync_vacancies: boolean;
  sync_applications: boolean;
  force_full_sync: boolean;
}

// Фильтры и запросы
export interface AnalysisFilter {
  vacancy_id?: string;
  min_score?: number;
  max_score?: number;
  recommendation?: 'hire' | 'interview' | 'maybe' | 'reject';
  has_red_flags?: boolean;
  analyzed_after?: string;
  limit?: number;
  offset?: number;
}

export interface ExportRequest {
  vacancy_id: string;
  include_resume_data: boolean;
  min_score?: number;
  recommendation?: string;
}

// API ответы
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  success?: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  limit: number;
}

// Состояния приложения
export interface AppState {
  loading: boolean;
  error: string | null;
  user: User | null;
  isAuthenticated: boolean;
}

export interface VacanciesState {
  vacancies: Vacancy[];
  currentVacancy: Vacancy | null;
  loading: boolean;
  error: string | null;
}

export interface AnalysisState {
  results: AnalysisResult[];
  stats: AnalysisStats | null;
  loading: boolean;
  error: string | null;
}

// Компоненты UI
export interface TableColumn {
  key: string;
  title: string;
  dataIndex?: string;
  width?: number;
  fixed?: 'left' | 'right';
  render?: (value: any, record: any, index: number) => React.ReactNode;
  sorter?: boolean | ((a: any, b: any) => number);
  filters?: Array<{ text: string; value: any }>;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'number';
  required?: boolean;
  placeholder?: string;
  options?: Array<{ label: string; value: any }>;
  rules?: any[];
}

// Подписки и тарификация
export type PlanType = 'free' | 'starter' | 'professional' | 'enterprise';
export type SubscriptionStatus = 'active' | 'expired' | 'cancelled' | 'trial';

export interface SubscriptionPlan {
  id: string;
  plan_type: PlanType;
  name: string;
  description?: string;
  pricing: {
    monthly: number;
    yearly: number;
    currency: string;
    yearly_discount: number;
  };
  limits: {
    active_vacancies: number;
    analyses_per_month: number;
    exports_per_month: number;
  };
  features: {
    basic_analysis?: boolean;
    advanced_ai?: boolean;
    priority_support?: boolean;
    api_access?: boolean;
    custom_integrations?: boolean;
    dedicated_manager?: boolean;
    [key: string]: boolean | undefined;
  };
  display_order: number;
  // Обратная совместимость со старой структурой
  price_monthly?: number;
  price_yearly?: number;
  max_active_vacancies?: number;
  max_analyses_per_month?: number;
  max_export_per_month?: number;
  is_popular?: boolean;
  created_at?: string;
}

export interface Subscription {
  id: string;
  user_id: string;
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  is_active: boolean;
  period: {
    started_at: string;
    expires_at: string;
    days_remaining: number;
  };
  usage: {
    analyses: {
      used: number;
      limit: number;
      percentage: number;
    };
    exports: {
      used: number;
      limit: number;
      percentage: number;
    };
    last_reset: string;
  };
  // Обратная совместимость со старой структурой
  plan_id?: string;
  analyses_used_this_month?: number;
  exports_used_this_month?: number;
  last_reset_at?: string;
  current_period_start?: string;
  current_period_end?: string;
  cancel_at_period_end?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface UsageStatistics {
  total_analyses: number;
  total_exports: number;
  analyses_by_day: { date: string; count: number }[];
  exports_by_day: { date: string; count: number }[];
  top_vacancies: { vacancy_id: string; vacancy_title: string; analyses_count: number }[];
}

export interface UpgradeSubscriptionRequest {
  new_plan_type: PlanType;
  duration_months: number;
}

export interface LimitsCheck {
  can_analyze: boolean;
  can_export: boolean;
  can_add_vacancy: boolean;
  messages: {
    analyses?: string;
    exports?: string;
    vacancies?: string;
  };
}

// Уведомления
export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface NotificationMessage {
  type: NotificationType;
  title: string;
  description?: string;
  duration?: number;
}