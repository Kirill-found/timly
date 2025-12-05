/**
 * API клиент для Timly Frontend
 * Axios конфигурация и базовые методы для работы с API
 */
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  ApiResponse,
  LoginRequest,
  RegisterRequest,
  AuthToken,
  User,
  Vacancy,
  Application,
  AnalysisResult,
  SyncJob,
  SyncJobRequest,
  AnalysisFilter,
  AnalysisStats,
  ExportRequest,
  SubscriptionPlan,
  Subscription,
  UsageStatistics,
  UpgradeSubscriptionRequest,
  LimitsCheck
} from '@/types';

// Базовая конфигурация API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/api\/?$/, '') || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor для добавления токена авторизации
    this.client.interceptors.request.use((config) => {
      const token = this.getAuthToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('[ApiClient] Request with token to:', config.url);
      } else {
        console.log('[ApiClient] Request WITHOUT token to:', config.url);
      }
      return config;
    });

    // Interceptor для обработки ответов с автоматическим обновлением токена
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Если получили 401 и это не повторный запрос
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          console.log('[ApiClient] Got 401, attempting token refresh');

          try {
            // Попытка обновить access токен используя refresh токен
            const refreshToken = this.getRefreshToken();
            if (refreshToken) {
              console.log('[ApiClient] Refresh token found, refreshing...');
              await this.refreshAccessToken();
              console.log('[ApiClient] Token refreshed successfully, retrying request');
              // Повторяем оригинальный запрос с новым токеном
              return this.client(originalRequest);
            } else {
              console.log('[ApiClient] No refresh token found');
            }
          } catch (refreshError) {
            // Если обновление токена не удалось - выходим
            console.error('[ApiClient] Token refresh failed:', refreshError);
            this.removeAuthToken();
            this.removeRefreshToken();
            console.log('[ApiClient] Redirecting to /login');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        // Для всех остальных ошибок или если refresh токена нет
        if (error.response?.status === 401) {
          console.log('[ApiClient] 401 error, no retry possible, redirecting to /login');
          this.removeAuthToken();
          this.removeRefreshToken();
          window.location.href = '/login';
        }

        return Promise.reject(error);
      }
    );
  }

  // Управление токенами через localStorage
  private getAuthToken(): string | null {
    try {
      const token = localStorage.getItem('timly_access_token');
      if (token) {
        console.log('[ApiClient] Access token found in localStorage');
      } else {
        console.log('[ApiClient] No access token in localStorage');
      }
      return token;
    } catch (e) {
      console.error('[ApiClient] Failed to get access token:', e);
      return null;
    }
  }

  private setAuthToken(token: string): void {
    try {
      localStorage.setItem('timly_access_token', token);
      console.log('[ApiClient] Access token saved to localStorage');
    } catch (e) {
      console.error('[ApiClient] Failed to save access token:', e);
    }
  }

  private removeAuthToken(): void {
    try {
      localStorage.removeItem('timly_access_token');
      console.log('[ApiClient] Access token removed from localStorage');
    } catch (e) {
      console.error('[ApiClient] Failed to remove access token:', e);
    }
  }

  private getRefreshToken(): string | null {
    try {
      return localStorage.getItem('timly_refresh_token');
    } catch {
      return null;
    }
  }

  private setRefreshToken(token: string): void {
    try {
      localStorage.setItem('timly_refresh_token', token);
    } catch (e) {
      console.error('Failed to save refresh token:', e);
    }
  }

  private removeRefreshToken(): void {
    try {
      localStorage.removeItem('timly_refresh_token');
    } catch (e) {
      console.error('Failed to remove refresh token:', e);
    }
  }

  // Аутентификация
  async login(credentials: LoginRequest): Promise<AuthToken> {
    const response = await this.client.post<ApiResponse<AuthToken>>('/api/auth/login', credentials);
    const token = response.data.data!;
    this.setAuthToken(token.access_token);
    if (token.refresh_token) {
      this.setRefreshToken(token.refresh_token);
    }
    return token;
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await this.client.post<ApiResponse<User>>('/api/auth/register', userData);
    return response.data.data!;
  }

  async getProfile(): Promise<User> {
    const response = await this.client.get<ApiResponse<User>>('/api/auth/me');
    return response.data.data!;
  }

  async logout(): Promise<void> {
    await this.client.post('/api/auth/logout');
    this.removeAuthToken();
    this.removeRefreshToken();
  }

  async refreshAccessToken(): Promise<AuthToken> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.client.post<AuthToken>('/api/auth/refresh', {
      refresh_token: refreshToken
    });

    const token = response.data;
    this.setAuthToken(token.access_token);

    return token;
  }

  // HH.ru токен
  async updateHHToken(token: string): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/api/settings/hh-token', {
      token: token
    });
    return response.data;
  }

  async testHHConnection(): Promise<ApiResponse> {
    const response = await this.client.get<ApiResponse>('/api/hh/test-connection');
    return response.data;
  }

  async exchangeHHCode(code: string): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/api/hh/oauth/exchange', null, {
      params: { code }
    });
    return response.data;
  }

  // Вакансии
  async getVacancies(params?: {
    limit?: number;
    offset?: number;
    active_only?: boolean;
  }): Promise<Vacancy[]> {
    const response = await this.client.get<ApiResponse<any>>('/api/hh/vacancies', { params });
    // API возвращает { data: { vacancies: [...], total: N } }
    const data = response.data.data;
    if (data && data.vacancies && Array.isArray(data.vacancies)) {
      return data.vacancies;
    }
    return [];
  }

  async getVacancy(vacancyId: string): Promise<Vacancy> {
    const response = await this.client.get<ApiResponse<Vacancy>>(`/api/hh/vacancies/${vacancyId}`);
    return response.data.data!;
  }

  async getVacancyApplications(
    vacancyId: string,
    params?: {
      limit?: number;
      offset?: number;
      analyzed_only?: boolean;
    }
  ): Promise<Application[]> {
    const response = await this.client.get<ApiResponse<Application[]>>(
      `/api/hh/vacancies/${vacancyId}/applications`,
      { params }
    );
    return response.data.data || [];
  }

  // Синхронизация
  async startSync(config: SyncJobRequest): Promise<SyncJob> {
    const response = await this.client.post<ApiResponse<SyncJob>>('/api/hh/sync', config);
    return response.data.data!;
  }

  async getSyncStatus(jobId: string): Promise<SyncJob> {
    const response = await this.client.get<ApiResponse<SyncJob>>(`/api/hh/sync/${jobId}`);
    return response.data.data!;
  }

  async getSyncHistory(limit: number = 20): Promise<SyncJob[]> {
    const response = await this.client.get<ApiResponse<SyncJob[]>>('/api/hh/sync/history', {
      params: { limit }
    });
    return response.data.data || [];
  }

  // AI Анализ
  async startAnalysis(applicationIds: string[]): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/api/analysis/start', {
      application_ids: applicationIds,
      force_reanalysis: false
    });
    return response.data;
  }

  async getAnalysisResults(filters?: AnalysisFilter): Promise<AnalysisResult[]> {
    const response = await this.client.get<ApiResponse<any>>('/api/analysis/results', {
      params: filters
    });
    // API возвращает { results: [...], total: ..., limit: ..., offset: ... }
    return response.data.data?.results || [];
  }

  async getAnalysisResult(analysisId: string): Promise<AnalysisResult> {
    const response = await this.client.get<ApiResponse<AnalysisResult>>(`/api/analysis/results/${analysisId}`);
    return response.data.data!;
  }

  async getVacancyAnalysisStats(vacancyId: string): Promise<AnalysisStats> {
    const response = await this.client.get<ApiResponse<AnalysisStats>>(`/api/analysis/vacancy/${vacancyId}/stats`);
    return response.data.data!;
  }

  async getDashboard(): Promise<ApiResponse> {
    const response = await this.client.get<ApiResponse>('/api/analysis/dashboard');
    return response.data;
  }

  // Новые методы для инкрементального анализа
  async getApplicationsStats(vacancyId?: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>('/api/applications/stats', {
      params: vacancyId ? { vacancy_id: vacancyId } : {}
    });
    return response.data.data;
  }

  async getUnanalyzedApplications(vacancyId?: string, collectionId: string = 'response', limit: number = 100): Promise<Application[]> {
    const response = await this.client.get<ApiResponse<any>>('/api/applications/unanalyzed', {
      params: {
        vacancy_id: vacancyId,
        collection_id: collectionId,
        limit
      }
    });
    return response.data.data?.applications || [];
  }

  async startAnalysisNewApplications(vacancyId: string, collectionFilter?: string, limit?: number): Promise<ApiResponse> {
    const params: any = { vacancy_id: vacancyId };
    if (collectionFilter) {
      params.collection_filter = collectionFilter;
    }
    if (limit !== undefined && limit > 0) {
      params.limit = limit;
    }

    const response = await this.client.post<ApiResponse>('/api/analysis/start-new', null, {
      params
    });
    return response.data;
  }

  async reanalyzeAllApplications(vacancyId: string): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/api/analysis/reanalyze-all', null, {
      params: { vacancy_id: vacancyId }
    });
    return response.data;
  }

  async downloadExcelReport(vacancyId: string, recommendation?: string, minScore?: number): Promise<Blob> {
    const params: any = { vacancy_id: vacancyId };

    if (recommendation && recommendation !== 'all') {
      params.recommendation = recommendation;
    }

    if (minScore && minScore > 0) {
      params.min_score = minScore;
    }

    const response = await this.client.get(`/api/analysis/export/excel`, {
      params,
      responseType: 'blob'
    });
    return response.data;
  }

  // Экспорт
  async requestExport(config: ExportRequest): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/api/analysis/export', config);
    return response.data;
  }

  async getExportStatus(exportJobId: string): Promise<ApiResponse> {
    const response = await this.client.get<ApiResponse>(`/api/analysis/export/${exportJobId}/status`);
    return response.data;
  }

  async downloadExport(exportJobId: string): Promise<Blob> {
    const response = await this.client.get(`/api/analysis/export/${exportJobId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Dashboard
  async getDashboardStats(): Promise<any> {
    const response = await this.client.get<ApiResponse>('/api/analysis/dashboard');
    return response.data.data;
  }

  // Настройки
  async getSettings(): Promise<ApiResponse> {
    const response = await this.client.get<ApiResponse>('/api/settings');
    return response.data;
  }

  async updateSettings(settings: any): Promise<ApiResponse> {
    const response = await this.client.put<ApiResponse>('/api/settings', settings);
    return response.data;
  }

  // Подписки и тарификация
  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    const response = await this.client.get<ApiResponse<any>>('/api/subscription/plans');
    // Backend возвращает { data: { plans: [...] } }
    const plansData = response.data.data?.plans || response.data.data || [];
    return Array.isArray(plansData) ? plansData : [];
  }

  async getCurrentSubscription(): Promise<Subscription> {
    const response = await this.client.get<ApiResponse<any>>('/api/subscription/current');
    // Backend возвращает { data: { subscription: {...} } }
    const subscriptionData = response.data.data?.subscription || response.data.data;
    return subscriptionData;
  }

  async upgradeSubscription(request: UpgradeSubscriptionRequest): Promise<Subscription> {
    const response = await this.client.post<ApiResponse<Subscription>>('/api/subscription/upgrade', request);
    return response.data.data!;
  }

  async cancelSubscription(): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>('/api/subscription/cancel');
    return response.data;
  }

  async getUsageStatistics(days: number = 30): Promise<UsageStatistics> {
    const response = await this.client.get<ApiResponse<UsageStatistics>>('/api/subscription/usage', {
      params: { days }
    });
    return response.data.data!;
  }

  async checkLimits(): Promise<LimitsCheck> {
    const response = await this.client.get<ApiResponse<LimitsCheck>>('/api/subscription/limits/check');
    return response.data.data!;
  }

  // Payment
  async createPayment(planType: string, durationMonths: number, returnUrl?: string): Promise<{
    payment_id: string;
    yookassa_payment_id: string;
    confirmation_url: string;
    amount: number;
    currency: string;
    status: string;
  }> {
    const response = await this.client.post<ApiResponse<any>>('/api/payment/create', {
      plan_type: planType,
      duration_months: durationMonths,
      return_url: returnUrl
    });
    return response.data.data!;
  }

  // Утилиты
  async healthCheck(): Promise<ApiResponse> {
    const response = await this.client.get<ApiResponse>('/health');
    return response.data;
  }

  // Публичные методы для управления токеном
  public setToken(token: string): void {
    this.setAuthToken(token);
  }

  public clearToken(): void {
    this.removeAuthToken();
    this.removeRefreshToken();
  }

  public hasToken(): boolean {
    return this.getAuthToken() !== null;
  }

  public hasRefreshToken(): boolean {
    return this.getRefreshToken() !== null;
  }

  // ==================== Поиск по базе резюме ====================

  async getResumeSearches(params?: {
    status_filter?: string;
    vacancy_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ searches: any[]; total: number }> {
    const response = await this.client.get<ApiResponse<any>>('/api/resume-search/searches', { params });
    return response.data.data || { searches: [], total: 0 };
  }

  async createResumeSearch(data: {
    name: string;
    description?: string;
    search_query: string;
    vacancy_id?: string;
    filters?: any;
  }): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>('/api/resume-search/searches', data);
    return response.data.data;
  }

  async getResumeSearch(searchId: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/api/resume-search/searches/${searchId}`);
    return response.data.data;
  }

  async updateResumeSearch(searchId: string, data: any): Promise<any> {
    const response = await this.client.put<ApiResponse<any>>(`/api/resume-search/searches/${searchId}`, data);
    return response.data.data;
  }

  async deleteResumeSearch(searchId: string): Promise<void> {
    await this.client.delete(`/api/resume-search/searches/${searchId}`);
  }

  async runResumeSearch(searchId: string, maxResults: number = 100): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>(`/api/resume-search/searches/${searchId}/run`, {
      max_results: maxResults
    });
    return response.data.data;
  }

  async getSearchCandidates(searchId: string, params?: {
    analyzed_only?: boolean;
    recommendation?: string;
    min_score?: number;
    favorites_only?: boolean;
    order_by?: string;
    page?: number;
    per_page?: number;
  }): Promise<{ candidates: any[]; total: number; page: number; per_page: number }> {
    const response = await this.client.get<ApiResponse<any>>(`/api/resume-search/searches/${searchId}/candidates`, { params });
    return response.data.data || { candidates: [], total: 0, page: 0, per_page: 20 };
  }

  async getSearchCandidate(searchId: string, candidateId: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/api/resume-search/searches/${searchId}/candidates/${candidateId}`);
    return response.data.data;
  }

  async updateSearchCandidate(searchId: string, candidateId: string, data: {
    is_favorite?: boolean;
    is_contacted?: boolean;
    notes?: string;
  }): Promise<any> {
    const response = await this.client.put<ApiResponse<any>>(`/api/resume-search/searches/${searchId}/candidates/${candidateId}`, data);
    return response.data.data;
  }

  async analyzeSearchCandidates(searchId: string, params?: {
    candidate_ids?: string[];
    force_reanalysis?: boolean;
  }): Promise<any> {
    const response = await this.client.post<ApiResponse<any>>(`/api/resume-search/searches/${searchId}/analyze`, params || {});
    return response.data.data;
  }

  async getSearchStats(searchId: string): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>(`/api/resume-search/searches/${searchId}/stats`);
    return response.data.data;
  }

  async getSearchDictionaries(): Promise<any> {
    const response = await this.client.get<ApiResponse<any>>('/api/resume-search/dictionaries');
    return response.data.data;
  }

  // Публичные HTTP методы для прямых запросов
  public get<T = any>(url: string, config?: any): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config);
  }

  public post<T = any>(url: string, data?: any, config?: any): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  public put<T = any>(url: string, data?: any, config?: any): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config);
  }

  public patch<T = any>(url: string, data?: any, config?: any): Promise<AxiosResponse<T>> {
    return this.client.patch<T>(url, data, config);
  }

  public delete<T = any>(url: string, config?: any): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config);
  }
}

// Singleton instance
export const apiClient = new ApiClient();

// Экспорт для удобства
export default apiClient;