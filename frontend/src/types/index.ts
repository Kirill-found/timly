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

// Композитные оценки AI (v2 - legacy)
export interface AIScores {
  relevance: number;   // Релевантность позиции (1-5)
  expertise: number;   // Экспертиза в навыках (1-5)
  trajectory: number;  // Карьерная траектория (1-5)
  stability: number;   // Стабильность и риски (1-5)
}

// ==================== AI Analyzer v7.0 Types ====================

// Вердикт v7.0 (заменяет числовой score)
export type Verdict = 'High' | 'Medium' | 'Low' | 'Mismatch';

// Must-have требование
export interface MustHave {
  requirement: string;
  status: 'yes' | 'maybe' | 'no';
  evidence: string | null;
  reasoning: string;
}

// Холистический анализ кандидата
export interface HolisticAnalysis {
  career_summary: string;
  relevance_assessment: string;
  growth_pattern: 'растёт' | 'стабилен' | 'деградирует' | 'непонятно';
}

// Анализ вакансии
export interface VacancyAnalysis {
  position_type: 'operations' | 'growth' | 'launch';
  niche_specifics: string;
  what_critical: string;
  what_learnable: string;
}

// Вопрос для интервью v7.0
export interface InterviewQuestion {
  question: string;
  checks: string;
}

// Salary fit v7.0
export interface SalaryFit {
  status: string;
  comment?: string;
}

// Анализ навыков
export interface SkillsAnalysis {
  matching: string[];     // Совпадающие навыки
  missing: string[];      // Недостающие навыки
  match_percent: number;  // Процент совпадения (0-100)
}

// Уровень уверенности AI в оценке
export type ConfidenceLevel = 'high' | 'medium' | 'low';

// Tier кандидата (A - лучшие, B - хорошие, C - слабые)
export type CandidateTier = 'A' | 'B' | 'C';

// Приоритет кандидата v7.2
export type Priority = 'top' | 'strong' | 'basic';

// Результаты AI анализа (v7.2 - Hybrid Expert + Priority)
export interface AnalysisResult {
  id: string;
  application_id: string;

  // === ПОЛЯ v7.2 (Priority + One-liner) ===
  verdict?: Verdict;                       // High/Medium/Low/Mismatch
  priority?: Priority;                     // top/strong/basic — приоритет внутри вердикта
  one_liner?: string;                      // Одно предложение: почему этот кандидат
  must_haves?: MustHave[];                 // Проверка ключевых требований
  holistic_analysis?: HolisticAnalysis;    // Холистический анализ
  vacancy_analysis?: VacancyAnalysis;      // Анализ вакансии
  reasoning_for_hr?: string;               // Развёрнутое объяснение для HR
  interview_questions_v7?: InterviewQuestion[]; // Вопросы с checks
  salary_fit?: SalaryFit;                  // Соответствие зарплаты
  concerns?: string[];                     // Сомнения/риски

  // === ПОЛЯ v2 (legacy) ===
  tier?: CandidateTier;                    // Tier A/B/C
  scores?: AIScores;                       // 4 оценки по 1-5
  confidence?: ConfidenceLevel;            // Уверенность AI
  skills_analysis?: SkillsAnalysis;        // Детальный анализ навыков
  pros?: string[];                         // Плюсы (конкретные факты)
  cons?: string[];                         // Минусы (конкретные факты)
  green_flags?: string[];                  // Зелёные флаги (бонусы)
  interview_questions?: string[];          // Вопросы для интервью (старый формат)
  summary?: string;                        // Короткое резюме (10-15 слов)

  // === Обратная совместимость (v1) ===
  score?: number;                          // rank_score 0-100
  skills_match?: number;                   // % совпадения навыков
  experience_match?: number;               // % совпадения опыта
  salary_match?: 'match' | 'higher' | 'lower' | 'unknown';
  strengths: string[];                     // = pros
  weaknesses: string[];                    // = cons
  red_flags: string[];
  recommendation?: 'hire' | 'interview' | 'maybe' | 'reject';
  reasoning?: string;                      // Длинное обоснование

  // Метаданные AI
  ai_model?: string;
  ai_tokens_used?: number;
  ai_cost_cents?: number;
  processing_time_ms?: number;

  // Полный ответ AI (для отладки)
  raw_result?: Record<string, any>;

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
  tier?: CandidateTier;  // Фильтр по Tier A/B/C
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
  plan_type: PlanType;
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

// ==================== Поиск по базе резюме ====================

export type SearchStatus = 'draft' | 'running' | 'completed' | 'analyzing' | 'done' | 'failed';

export interface SearchFilters {
  area?: string;
  experience?: string;
  salary_from?: number;
  salary_to?: number;
  age_from?: number;
  age_to?: number;
  gender?: string;
  education_level?: string;
  job_search_status?: string;
  relocation?: string;
}

export interface ResumeSearch {
  id: string;
  user_id: string;
  vacancy_id?: string;
  name: string;
  description?: string;
  search_query: string;
  filters: SearchFilters;
  status: SearchStatus;
  total_found: number;
  processed_count: number;
  analyzed_count: number;
  error_message?: string;
  last_run_at?: string;
  created_at: string;
  updated_at: string;
}

export interface SearchCandidate {
  id: string;
  search_id: string;
  hh_resume_id: string;
  full_name: string;
  first_name?: string;
  last_name?: string;
  title?: string;
  age?: number;
  gender?: string;
  area?: string;
  salary?: number;
  currency: string;
  experience_years?: number;
  skills: string[];
  // AI анализ
  is_analyzed: boolean;
  ai_score?: number;
  ai_recommendation?: 'hire' | 'consider' | 'reject';
  ai_summary?: string;
  ai_strengths: string[];
  ai_weaknesses: string[];
  analyzed_at?: string;
  // Статус
  is_favorite: boolean;
  is_contacted: boolean;
  notes?: string;
  created_at: string;
}

export interface SearchCandidateDetail extends SearchCandidate {
  resume_data: Record<string, any>;
  ai_analysis_data: Record<string, any>;
}

export interface CreateSearchRequest {
  name: string;
  description?: string;
  search_query: string;
  vacancy_id?: string;
  filters?: SearchFilters;
}

export interface SearchStats {
  total_candidates: number;
  analyzed_count: number;
  hire_count: number;
  consider_count: number;
  reject_count: number;
  favorites_count: number;
  contacted_count: number;
  avg_score?: number;
}

export interface DictionaryItem {
  id: string;
  name: string;
}

export interface SearchDictionaries {
  experience: DictionaryItem[];
  education_level: DictionaryItem[];
  gender: DictionaryItem[];
  job_search_status: DictionaryItem[];
  relocation: DictionaryItem[];
  order_by: DictionaryItem[];
  areas: DictionaryItem[];
}