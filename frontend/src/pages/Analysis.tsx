/**
 * Analysis - Анализ резюме v3
 * Design: Dark Industrial + Data Dashboard
 *
 * Product-driven redesign:
 * - Tier A/B/C как главный элемент принятия решения
 * - 4 композитные оценки с визуальными dot indicators
 * - Confidence level для доверия к оценке
 * - Interview Questions для подготовки к собеседованию
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, ExternalLink, Phone, Square, Play, ChevronDown, ChevronUp, AlertCircle, MessageSquare, Shield, TrendingUp, Briefcase, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/services/api';
import { Vacancy, AnalysisResult, AnalysisFilter, CandidateTier, ConfidenceLevel, AIScores } from '@/types';
import { useApp } from '@/store/AppContext';
import { LimitExceededModal } from '@/components/LimitExceededModal';

interface AnalysisWithApplication extends AnalysisResult {
  application?: {
    candidate_name?: string;
    candidate_email?: string;
    candidate_phone?: string;
    resume_url?: string;
    created_at?: string;
  };
}

// === HELPER COMPONENTS ===

// Tier Badge - главный элемент принятия решения
const TierBadge: React.FC<{ tier?: CandidateTier; size?: 'sm' | 'md' | 'lg' }> = ({ tier, size = 'md' }) => {
  const styles = {
    A: 'bg-emerald-500 text-white shadow-emerald-500/30',
    B: 'bg-blue-500 text-white shadow-blue-500/30',
    C: 'bg-zinc-600 text-zinc-300 shadow-zinc-600/20',
  };
  const sizes = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-10 h-10 text-base',
  };

  if (!tier) return null;

  return (
    <div className={`${sizes[size]} ${styles[tier]} rounded-lg font-bold flex items-center justify-center shadow-lg`}>
      {tier}
    </div>
  );
};

// Score Dots - визуализация оценки 1-5
const ScoreDots: React.FC<{ score: number; label: string; icon?: React.ReactNode }> = ({ score, label, icon }) => {
  const clampedScore = Math.max(1, Math.min(5, score || 0));

  return (
    <div className="flex items-center gap-2">
      {icon && <span className="text-zinc-500">{icon}</span>}
      <div className="flex-1 min-w-0">
        <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1 truncate">{label}</div>
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-colors ${
                i <= clampedScore
                  ? clampedScore >= 4 ? 'bg-emerald-500' : clampedScore >= 3 ? 'bg-amber-500' : 'bg-red-500'
                  : 'bg-zinc-700'
              }`}
            />
          ))}
          <span className="text-xs text-zinc-400 ml-1 tabular-nums">{clampedScore}/5</span>
        </div>
      </div>
    </div>
  );
};

// Confidence Badge
const ConfidenceBadge: React.FC<{ level?: ConfidenceLevel }> = ({ level }) => {
  if (!level) return null;

  const styles = {
    high: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    low: 'bg-red-500/10 text-red-400 border-red-500/20',
  };
  const labels = {
    high: 'Высокая уверенность',
    medium: 'Средняя уверенность',
    low: 'Низкая уверенность',
  };

  return (
    <span className={`px-2 py-0.5 rounded text-[10px] border ${styles[level]}`}>
      {labels[level]}
    </span>
  );
};

// Helper to get scores from raw_result or scores field
const getScores = (r: AnalysisWithApplication): AIScores | null => {
  if (r.scores) return r.scores;
  if (r.raw_result?.scores) return r.raw_result.scores as AIScores;
  return null;
};

// Helper to get tier
const getTier = (r: AnalysisWithApplication): CandidateTier | undefined => {
  if (r.tier) return r.tier;
  if (r.raw_result?.tier) return r.raw_result.tier as CandidateTier;
  // Fallback: calculate from score
  if (r.score !== undefined) {
    if (r.score >= 82) return 'A';
    if (r.score >= 58) return 'B';
    return 'C';
  }
  return undefined;
};

// Helper to get confidence
const getConfidence = (r: AnalysisWithApplication): ConfidenceLevel | undefined => {
  if (r.confidence) return r.confidence;
  if (r.raw_result?.confidence) return r.raw_result.confidence as ConfidenceLevel;
  return undefined;
};

// Helper to get interview questions
const getInterviewQuestions = (r: AnalysisWithApplication): string[] => {
  if (r.interview_questions?.length) return r.interview_questions;
  if (r.raw_result?.interview_questions?.length) return r.raw_result.interview_questions;
  return [];
};

// Helper to get summary
const getSummary = (r: AnalysisWithApplication): string | undefined => {
  if (r.summary) return r.summary;
  if (r.raw_result?.summary) return r.raw_result.summary;
  if (r.raw_result?.summary_one_line) return r.raw_result.summary_one_line;
  return undefined;
};

// Helper to get green flags
const getGreenFlags = (r: AnalysisWithApplication): string[] => {
  if (r.green_flags?.length) return r.green_flags;
  if (r.raw_result?.green_flags?.length) return r.raw_result.green_flags;
  return [];
};

const Analysis: React.FC = () => {
  const app = useApp();
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [selectedVacancy, setSelectedVacancy] = useState<string>('all');
  const [results, setResults] = useState<AnalysisWithApplication[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tierFilter, setTierFilter] = useState<string>('all'); // NEW: Tier filter
  const [recommendationFilter, setRecommendationFilter] = useState<string>('all');
  const [applicationsStats, setApplicationsStats] = useState<any>(null);
  const [dashboardStats, setDashboardStats] = useState<any>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [limitModalOpen, setLimitModalOpen] = useState(false);
  const [limitExceededInfo, setLimitExceededInfo] = useState<any>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [limits, setLimits] = useState<any>(null);

  // ========== ИСПРАВЛЕННЫЙ POLLING ==========
  // Используем useRef для сохранения данных между рендерами
  const pollingDataRef = useRef<{
    initialAnalyzed: number | null;
    intervalId: NodeJS.Timeout | null;
    lastProgress: number;
    noProgressSince: number | null;  // Таймстамп когда перестал быть прогресс
  }>({ initialAnalyzed: null, intervalId: null, lastProgress: 0, noProgressSince: null });

  const isAnalyzing = app.activeAnalysis !== null && app.activeAnalysis.vacancyId === selectedVacancy;
  const analysisProgress = app.activeAnalysis || { total: 0, analyzed: 0, startTime: 0, vacancyId: '' };

  // Загрузка данных
  useEffect(() => { loadVacancies(); loadLimits(); }, []);
  useEffect(() => { loadResults(); }, [selectedVacancy, tierFilter, recommendationFilter]);
  useEffect(() => {
    if (selectedVacancy !== 'all') {
      loadApplicationsStats();
      loadDashboardStats();
    } else {
      setApplicationsStats(null);
      setDashboardStats(null);
    }
  }, [selectedVacancy]);

  // ИСПРАВЛЕННЫЙ useEffect для polling
  useEffect(() => {
    // Если нет активного анализа - очищаем
    if (!app.activeAnalysis) {
      pollingDataRef.current.initialAnalyzed = null;
      pollingDataRef.current.lastProgress = 0;
      pollingDataRef.current.noProgressSince = null;
      if (pollingDataRef.current.intervalId) {
        clearInterval(pollingDataRef.current.intervalId);
        pollingDataRef.current.intervalId = null;
      }
      return;
    }

    const vacancyId = app.activeAnalysis.vacancyId;
    const targetTotal = app.activeAnalysis.total;

    const pollStats = async () => {
      try {
        const stats = await apiClient.getApplicationsStats(vacancyId);
        const currentAnalyzed = stats.analyzed_applications;

        // При первом вызове запоминаем начальное значение
        if (pollingDataRef.current.initialAnalyzed === null) {
          pollingDataRef.current.initialAnalyzed = currentAnalyzed;
        }

        // Вычисляем прогресс ОТНОСИТЕЛЬНО старта
        const newlyAnalyzed = currentAnalyzed - pollingDataRef.current.initialAnalyzed;
        const safeProgress = Math.max(0, Math.min(newlyAnalyzed, targetTotal));

        app.updateAnalysisProgress({ analyzed: safeProgress });

        // Отслеживаем прогресс - если нет изменений 30 сек, завершаем
        const now = Date.now();
        if (safeProgress > pollingDataRef.current.lastProgress) {
          pollingDataRef.current.lastProgress = safeProgress;
          pollingDataRef.current.noProgressSince = null;
        } else if (pollingDataRef.current.noProgressSince === null) {
          pollingDataRef.current.noProgressSince = now;
        }

        // Таймаут 30 секунд без прогресса - завершаем анализ
        const NO_PROGRESS_TIMEOUT = 30000;
        const noProgressTime = pollingDataRef.current.noProgressSince 
          ? now - pollingDataRef.current.noProgressSince 
          : 0;

        // Проверяем завершение: успех ИЛИ таймаут
        const isComplete = stats.unanalyzed_applications === 0 || safeProgress >= targetTotal;
        const isTimeout = noProgressTime >= NO_PROGRESS_TIMEOUT;

        if (isComplete || isTimeout) {
          // Останавливаем polling
          if (pollingDataRef.current.intervalId) {
            clearInterval(pollingDataRef.current.intervalId);
            pollingDataRef.current.intervalId = null;
          }
          pollingDataRef.current.initialAnalyzed = null;
          pollingDataRef.current.lastProgress = 0;
          pollingDataRef.current.noProgressSince = null;
          app.stopAnalysis();
          loadResults();
          loadApplicationsStats();
          loadDashboardStats();
          loadLimits();
          
          // Если завершили по таймауту и было 0 прогресса - все уже проанализированы
          if (isTimeout && safeProgress === 0) {
            console.log('[Analysis] Все отклики уже были проанализированы ранее');
          }
        }
      } catch (err) {
        console.error('[Analysis] Polling error:', err);
      }
    };

    // Очищаем предыдущий интервал если был
    if (pollingDataRef.current.intervalId) {
      clearInterval(pollingDataRef.current.intervalId);
    }

    // Запускаем новый polling
    pollStats(); // Сразу первый вызов
    pollingDataRef.current.intervalId = setInterval(pollStats, 3000);

    // Cleanup при размонтировании
    return () => {
      if (pollingDataRef.current.intervalId) {
        clearInterval(pollingDataRef.current.intervalId);
        pollingDataRef.current.intervalId = null;
      }
    };
  }, [app.activeAnalysis?.vacancyId, app.activeAnalysis?.total]);

  const loadLimits = async () => {
    try {
      const data = await apiClient.checkLimits();
      setLimits(data);
    } catch (err) {
      console.error('Error loading limits:', err);
    }
  };

  const loadVacancies = async () => {
    try {
      const data = await apiClient.getVacancies({ active_only: true });
      setVacancies(Array.isArray(data) ? data : []);
    } catch (err) {
      setVacancies([]);
    }
  };

  const loadResults = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const filters: AnalysisFilter = { limit: 100 };
      if (selectedVacancy !== 'all') filters.vacancy_id = selectedVacancy;
      if (recommendationFilter !== 'all') filters.recommendation = recommendationFilter as any;
      let data = await apiClient.getAnalysisResults(filters);
      data = Array.isArray(data) ? data : [];

      // Локальная фильтрация по Tier (если API не поддерживает)
      if (tierFilter !== 'all') {
        data = data.filter((r: AnalysisWithApplication) => getTier(r) === tierFilter);
      }

      setResults(data);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Ошибка загрузки');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadApplicationsStats = async () => {
    try {
      if (selectedVacancy === 'all') return setApplicationsStats(null);
      const stats = await apiClient.getApplicationsStats(selectedVacancy);
      setApplicationsStats(stats);
    } catch (err) {
      setApplicationsStats(null);
    }
  };

  const loadDashboardStats = async () => {
    try {
      if (selectedVacancy === 'all') return setDashboardStats(null);
      const stats = await apiClient.getVacancyAnalysisStats(selectedVacancy);
      setDashboardStats(stats);
    } catch (err) {
      setDashboardStats(null);
    }
  };

  const handleStopAnalysis = () => {
    if (pollingDataRef.current.intervalId) {
      clearInterval(pollingDataRef.current.intervalId);
      pollingDataRef.current.intervalId = null;
    }
    pollingDataRef.current.initialAnalyzed = null;
    pollingDataRef.current.lastProgress = 0;
    pollingDataRef.current.noProgressSince = null;
    app.stopAnalysis();
    loadResults();
    loadApplicationsStats();
    loadDashboardStats();
  };

  const handleAnalyzeNew = async () => {
    if (selectedVacancy === 'all') {
      setError('Выберите вакансию');
      return;
    }

    const toAnalyze = applicationsStats?.unanalyzed_applications || 0;
    if (toAnalyze === 0) {
      setError('Нет откликов для анализа');
      return;
    }

    // Проверяем лимит
    const remaining = limits?.analyses_remaining || 0;
    if (!limits?.is_unlimited && remaining <= 0) {
      setLimitExceededInfo(limits);
      setLimitModalOpen(true);
      return;
    }

    // Анализируем столько, сколько позволяет лимит
    const actualToAnalyze = limits?.is_unlimited ? toAnalyze : Math.min(toAnalyze, remaining);

    setError(null);
    // Сбрасываем все данные поллинга перед стартом
    pollingDataRef.current.initialAnalyzed = null;
    pollingDataRef.current.lastProgress = 0;
    pollingDataRef.current.noProgressSince = null;

    app.startAnalysis({
      vacancyId: selectedVacancy,
      total: actualToAnalyze,
      analyzed: 0,
      startTime: Date.now()
    });

    try {
      await apiClient.startAnalysisNewApplications(selectedVacancy, undefined, actualToAnalyze);
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail;
      if (errorDetail?.error === 'LIMIT_EXCEEDED') {
        setLimitExceededInfo(errorDetail.subscription);
        setLimitModalOpen(true);
      } else {
        setError(errorDetail?.message || 'Ошибка запуска анализа');
      }
      app.stopAnalysis();
    }
  };

  const handleDownloadExcel = async () => {
    if (selectedVacancy === 'all') return;
    setIsDownloading(true);
    try {
      const filter = recommendationFilter !== 'all' ? recommendationFilter : undefined;
      const blob = await apiClient.downloadExcelReport(selectedVacancy, filter);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_${selectedVacancy}_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Ошибка скачивания');
    } finally {
      setIsDownloading(false);
    }
  };

  const toggleExpanded = (id: string) => {
    const newSet = new Set(expandedResults);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setExpandedResults(newSet);
  };

  const getRecommendationStyle = (rec?: string) => {
    switch (rec) {
      case 'hire': return 'status-hire';
      case 'interview': return 'status-interview';
      case 'maybe': return 'status-maybe';
      case 'reject': return 'status-reject';
      default: return 'bg-zinc-800 text-zinc-400';
    }
  };

  const getRecommendationText = (rec?: string) => {
    switch (rec) {
      case 'hire': return 'Нанять';
      case 'interview': return 'Собеседование';
      case 'maybe': return 'Возможно';
      case 'reject': return 'Отклонить';
      default: return '—';
    }
  };

  const statsData = dashboardStats ? {
    total: dashboardStats.total_analyzed || 0,
    hire: dashboardStats.hire_count || 0,
    interview: dashboardStats.interview_count || 0,
    maybe: dashboardStats.maybe_count || 0,
    reject: dashboardStats.reject_count || 0,
    avgScore: Math.round(dashboardStats.avg_score || 0),
  } : { total: 0, hire: 0, interview: 0, maybe: 0, reject: 0, avgScore: 0 };

  const progressPercent = analysisProgress.total > 0
    ? Math.round((analysisProgress.analyzed / analysisProgress.total) * 100)
    : 0;

  const elapsed = Date.now() - analysisProgress.startTime;
  const speed = analysisProgress.analyzed > 0
    ? ((analysisProgress.analyzed / (elapsed / 1000)) * 60).toFixed(1)
    : '0';

  const getTimeRemaining = () => {
    if (analysisProgress.analyzed === 0) return 'Расчёт...';
    const avg = elapsed / analysisProgress.analyzed;
    const remaining = (analysisProgress.total - analysisProgress.analyzed) * avg;
    const min = Math.floor(remaining / 60000);
    const sec = Math.floor((remaining % 60000) / 1000);
    return min > 0 ? `~${min} мин` : `~${sec} сек`;
  };

  // Лимиты - ИСПРАВЛЕННАЯ логика отображения
  const limitsRemaining = limits?.analyses_remaining ?? 0;
  const limitsTotal = limits?.analyses_limit ?? 20;
  const limitsUsed = limits?.analyses_used ?? 0;
  const isUnlimited = limits?.is_unlimited ?? false;

  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div {...fadeIn} className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">Анализ резюме</h1>
          <p className="text-sm text-zinc-500 mt-1">AI-оценка кандидатов</p>
        </div>
        {selectedVacancy !== 'all' && applicationsStats?.analyzed_applications > 0 && (
          <Button
            onClick={handleDownloadExcel}
            disabled={isDownloading}
            variant="outline"
            size="sm"
            className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
          >
            <Download className="h-4 w-4 mr-2" />
            Excel
          </Button>
        )}
      </motion.div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3"
          >
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            {error}
            <button onClick={() => setError(null)} className="ml-auto hover:text-red-300">×</button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ИСПРАВЛЕННЫЕ Лимиты - понятный блок */}
      {limits && !isUnlimited && (
        <motion.div {...fadeIn}>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-6">
                {/* Основной показатель - сколько ОСТАЛОСЬ */}
                <div className="flex-shrink-0">
                  <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-1">
                    Доступно анализов
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className={`text-3xl font-semibold tabular-nums ${
                      limitsRemaining <= 5 ? 'text-red-400' :
                      limitsRemaining <= 10 ? 'text-amber-400' :
                      'text-zinc-100'
                    }`}>
                      {limitsRemaining}
                    </span>
                    <span className="text-sm text-zinc-600">/ {limitsTotal}</span>
                  </div>
                </div>

                {/* Прогресс-бар - показывает ИСПОЛЬЗОВАННОЕ */}
                <div className="flex-1">
                  <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        limitsRemaining <= 5 ? 'bg-red-500' :
                        limitsRemaining <= 10 ? 'bg-amber-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${((limitsTotal - limitsRemaining) / limitsTotal) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-1.5 text-[11px] text-zinc-600">
                    <span>Использовано: {limitsUsed}</span>
                    {limits.reset_date && (
                      <span>Обновление: {new Date(limits.reset_date).toLocaleDateString('ru-RU')}</span>
                    )}
                  </div>
                </div>

                {/* Кнопка улучшить - если мало осталось */}
                {limitsRemaining <= 10 && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 flex-shrink-0"
                    onClick={() => window.open('/pricing', '_blank')}
                  >
                    Увеличить
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Filters */}
      <motion.div {...fadeIn} className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
          <SelectTrigger className="h-11 bg-card border-zinc-800">
            <SelectValue placeholder="Выберите вакансию" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">Все вакансии</SelectItem>
            {vacancies.map(v => (
              <SelectItem key={v.id} value={v.id}>{v.title}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* NEW: Tier Filter - главный фильтр для HR */}
        <Select value={tierFilter} onValueChange={setTierFilter}>
          <SelectTrigger className="h-11 bg-card border-zinc-800">
            <SelectValue placeholder="Фильтр по Tier" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">Все Tier</SelectItem>
            <SelectItem value="A">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 bg-emerald-500 rounded text-white text-xs font-bold flex items-center justify-center">A</span>
                <span>Лучшие кандидаты</span>
              </div>
            </SelectItem>
            <SelectItem value="B">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 bg-blue-500 rounded text-white text-xs font-bold flex items-center justify-center">B</span>
                <span>Хорошие кандидаты</span>
              </div>
            </SelectItem>
            <SelectItem value="C">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 bg-zinc-600 rounded text-zinc-300 text-xs font-bold flex items-center justify-center">C</span>
                <span>Слабые кандидаты</span>
              </div>
            </SelectItem>
          </SelectContent>
        </Select>

        <Select value={recommendationFilter} onValueChange={setRecommendationFilter}>
          <SelectTrigger className="h-11 bg-card border-zinc-800">
            <SelectValue placeholder="Фильтр по статусу" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">Все результаты</SelectItem>
            <SelectItem value="hire">Нанять</SelectItem>
            <SelectItem value="interview">Собеседование</SelectItem>
            <SelectItem value="maybe">Возможно</SelectItem>
            <SelectItem value="reject">Отклонить</SelectItem>
          </SelectContent>
        </Select>
      </motion.div>

      {/* Stats + Control */}
      {selectedVacancy !== 'all' && applicationsStats && (
        <motion.div {...fadeIn} className="space-y-4">
          {/* Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-px bg-zinc-800 border border-zinc-800 rounded-lg overflow-hidden">
            <div className="bg-card p-5">
              <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
                Всего откликов
              </div>
              <div className="text-3xl font-semibold tracking-tight tabular-nums">
                {applicationsStats.total_applications}
              </div>
            </div>
            <div className="bg-card p-5">
              <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
                Проанализировано
              </div>
              <div className="text-3xl font-semibold tracking-tight tabular-nums text-green-500">
                {applicationsStats.analyzed_applications}
              </div>
            </div>
            <div className="bg-card p-5">
              <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
                Ожидает анализа
              </div>
              <div className="text-3xl font-semibold tracking-tight tabular-nums text-amber-500">
                {applicationsStats.unanalyzed_applications}
              </div>
            </div>
            <div className="bg-card p-5">
              <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
                Средний балл
              </div>
              <div className="text-3xl font-semibold tracking-tight tabular-nums">
                {statsData.avgScore}
                <span className="text-lg text-zinc-500 font-normal">/100</span>
              </div>
            </div>
          </div>

          {/* Analysis Control - УПРОЩЁННЫЙ */}
          {!isAnalyzing ? (
            <Card>
              <CardContent className="p-5">
                {applicationsStats.unanalyzed_applications > 0 ? (
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-zinc-400 mb-1">
                        {applicationsStats.unanalyzed_applications} {
                          applicationsStats.unanalyzed_applications === 1 ? 'резюме ожидает' :
                          applicationsStats.unanalyzed_applications < 5 ? 'резюме ожидают' : 'резюме ожидают'
                        } анализа
                      </div>
                      {!isUnlimited && limitsRemaining < applicationsStats.unanalyzed_applications && (
                        <div className="text-xs text-amber-400">
                          Лимит позволяет проанализировать {limitsRemaining} из {applicationsStats.unanalyzed_applications}
                        </div>
                      )}
                    </div>
                    <Button
                      onClick={handleAnalyzeNew}
                      className="h-11 px-6 bg-zinc-100 text-zinc-900 hover:bg-white font-medium"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Запустить анализ
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-2 text-zinc-500">
                    Все резюме проанализированы
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            /* Progress Card */
            <Card>
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className="text-sm font-medium text-zinc-200">Анализ выполняется</div>
                    <div className="text-xs text-zinc-500 mt-0.5">
                      {analysisProgress.analyzed} из {analysisProgress.total} резюме
                    </div>
                  </div>
                  <div className="text-3xl font-semibold tabular-nums">
                    {progressPercent}%
                  </div>
                </div>

                {/* Progress bar */}
                <div className="h-3 bg-zinc-800 rounded-full overflow-hidden mb-4">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${progressPercent}%` }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                    className="h-full bg-green-500 rounded-full"
                  />
                </div>

                <div className="flex items-center justify-between text-xs text-zinc-500 mb-4">
                  <span>Осталось: {getTimeRemaining()}</span>
                  <span>{speed} рез/мин</span>
                </div>

                <Button
                  onClick={handleStopAnalysis}
                  variant="outline"
                  className="w-full border-zinc-700 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
                >
                  <Square className="h-4 w-4 mr-2 fill-current" />
                  Остановить
                </Button>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}

      {/* Distribution */}
      {selectedVacancy !== 'all' && statsData.total > 0 && (
        <motion.div {...fadeIn}>
          <Card>
            <CardHeader className="pb-0">
              <CardTitle className="text-[13px] font-medium uppercase tracking-wide">
                Распределение
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-4 gap-4">
                {[
                  { label: 'Нанять', value: statsData.hire, color: 'bg-green-500' },
                  { label: 'Собеседование', value: statsData.interview, color: 'bg-blue-500' },
                  { label: 'Возможно', value: statsData.maybe, color: 'bg-amber-500' },
                  { label: 'Отклонить', value: statsData.reject, color: 'bg-red-500' },
                ].map((item) => (
                  <div key={item.label} className="text-center">
                    <div className="flex items-center justify-center gap-2 mb-1">
                      <div className={`w-2 h-2 rounded-sm ${item.color}`} />
                      <span className="text-xs text-zinc-500">{item.label}</span>
                    </div>
                    <div className="text-2xl font-semibold tabular-nums">{item.value}</div>
                    <div className="text-[11px] text-zinc-600">
                      {statsData.total > 0 ? Math.round((item.value / statsData.total) * 100) : 0}%
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* No vacancy hint */}
      {selectedVacancy === 'all' && (
        <motion.div {...fadeIn} className="text-center py-12">
          <p className="text-zinc-500">Выберите вакансию для запуска анализа</p>
        </motion.div>
      )}

      {/* Results Table - v3 with Tier, Score Dots, Interview Questions */}
      <motion.div {...fadeIn}>
        <Card>
          <CardHeader className="pb-0 flex flex-row items-center justify-between">
            <CardTitle className="text-[13px] font-medium uppercase tracking-wide">
              Результаты анализа
            </CardTitle>
            <span className="text-xs text-zinc-500 tabular-nums">{results.length}</span>
          </CardHeader>
          <CardContent className="pt-4 px-0">
            {isLoading ? (
              <div className="p-12 text-center text-zinc-500">Загрузка...</div>
            ) : results.length === 0 ? (
              <div className="p-12 text-center">
                <p className="text-zinc-400 mb-1">Нет результатов</p>
                <p className="text-xs text-zinc-600">Запустите анализ или измените фильтры</p>
              </div>
            ) : (
              <div>
                {results.map((r) => {
                  const tier = getTier(r);
                  const scores = getScores(r);
                  const confidence = getConfidence(r);
                  const interviewQuestions = getInterviewQuestions(r);
                  const summary = getSummary(r);
                  const greenFlags = getGreenFlags(r);

                  return (
                    <div key={r.id} className="border-b border-zinc-800/50 last:border-b-0">
                      {/* Card Header - Collapsed View */}
                      <div
                        className="px-5 py-4 flex items-center gap-4 cursor-pointer hover:bg-zinc-900/50 transition-colors"
                        onClick={() => toggleExpanded(r.id)}
                      >
                        {/* Tier Badge - главный элемент */}
                        <TierBadge tier={tier} size="lg" />

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-[13px] font-medium truncate">
                              {r.application?.candidate_name || 'Без имени'}
                            </span>
                            {r.application?.resume_url && (
                              <a
                                href={r.application.resume_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="text-zinc-600 hover:text-zinc-400"
                              >
                                <ExternalLink className="h-3.5 w-3.5" />
                              </a>
                            )}
                            {/* Confidence Badge */}
                            <ConfidenceBadge level={confidence} />
                          </div>
                          {/* Summary - короткое описание вместо телефона */}
                          {summary ? (
                            <div className="text-xs text-zinc-500 mt-0.5 truncate">
                              {summary}
                            </div>
                          ) : r.application?.candidate_phone && (
                            <div className="flex items-center gap-1.5 text-xs text-zinc-500 mt-0.5">
                              <Phone className="h-3 w-3" />
                              {r.application.candidate_phone}
                            </div>
                          )}
                        </div>

                        {/* Score */}
                        <div className="text-right mr-2">
                          <div className="text-lg font-semibold tabular-nums">{r.score || '—'}</div>
                          <div className="text-[10px] text-zinc-500">баллов</div>
                        </div>

                        {/* Status */}
                        <span className={`px-2.5 py-1 rounded text-[11px] font-medium ${getRecommendationStyle(r.recommendation)}`}>
                          {getRecommendationText(r.recommendation)}
                        </span>

                        {/* Chevron */}
                        {expandedResults.has(r.id) ? (
                          <ChevronUp className="h-4 w-4 text-zinc-500" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-zinc-500" />
                        )}
                      </div>

                      {/* Expanded View - v3 with Score Dots and Interview Questions */}
                      <AnimatePresence>
                        {expandedResults.has(r.id) && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                          >
                            <div className="px-5 pb-5 pt-2 ml-[52px] space-y-4">
                              {/* === NEW: 4 Score Dots === */}
                              {scores && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-lg bg-zinc-800/30 border border-zinc-700/30">
                                  <ScoreDots
                                    score={scores.relevance}
                                    label="Релевантность"
                                    icon={<Target className="h-3.5 w-3.5" />}
                                  />
                                  <ScoreDots
                                    score={scores.expertise}
                                    label="Экспертиза"
                                    icon={<Briefcase className="h-3.5 w-3.5" />}
                                  />
                                  <ScoreDots
                                    score={scores.trajectory}
                                    label="Траектория"
                                    icon={<TrendingUp className="h-3.5 w-3.5" />}
                                  />
                                  <ScoreDots
                                    score={scores.stability}
                                    label="Стабильность"
                                    icon={<Shield className="h-3.5 w-3.5" />}
                                  />
                                </div>
                              )}

                              {/* Legacy Metrics (fallback if no scores) */}
                              {!scores && (
                                <div className="grid grid-cols-3 gap-3">
                                  <div className="p-3 rounded-lg bg-zinc-800/50">
                                    <div className="text-[11px] text-zinc-500 mb-1">Навыки</div>
                                    <div className="flex items-center gap-2">
                                      <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-green-500 rounded-full" style={{ width: `${r.skills_match || 0}%` }} />
                                      </div>
                                      <span className="text-sm font-medium tabular-nums">{r.skills_match || 0}%</span>
                                    </div>
                                  </div>
                                  <div className="p-3 rounded-lg bg-zinc-800/50">
                                    <div className="text-[11px] text-zinc-500 mb-1">Опыт</div>
                                    <div className="flex items-center gap-2">
                                      <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${r.experience_match || 0}%` }} />
                                      </div>
                                      <span className="text-sm font-medium tabular-nums">{r.experience_match || 0}%</span>
                                    </div>
                                  </div>
                                  <div className="p-3 rounded-lg bg-zinc-800/50">
                                    <div className="text-[11px] text-zinc-500 mb-1">Зарплата</div>
                                    <div className="text-sm font-medium">
                                      {r.salary_match === 'match' ? 'Совпадает' :
                                       r.salary_match === 'higher' ? 'Выше' :
                                       r.salary_match === 'lower' ? 'Ниже' : 'Не указана'}
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* === NEW: Interview Questions — killer feature! === */}
                              {interviewQuestions.length > 0 && (
                                <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20">
                                  <div className="flex items-center gap-2 mb-3">
                                    <MessageSquare className="h-4 w-4 text-blue-400" />
                                    <span className="text-[11px] font-medium text-blue-400 uppercase tracking-wider">
                                      Вопросы для интервью
                                    </span>
                                  </div>
                                  <ul className="space-y-2">
                                    {interviewQuestions.map((q, i) => (
                                      <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
                                        <span className="text-blue-400 mt-0.5">•</span>
                                        {q}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {/* Tags - Pros/Cons/Flags */}
                              <div className="space-y-3">
                                {/* Green Flags (NEW) */}
                                {greenFlags.length > 0 && (
                                  <div>
                                    <div className="text-[11px] text-emerald-500 mb-2">✓ Зелёные флаги</div>
                                    <div className="flex flex-wrap gap-1.5">
                                      {greenFlags.map((f, i) => (
                                        <span key={i} className="px-2 py-0.5 text-xs bg-emerald-500/10 text-emerald-400 rounded border border-emerald-500/20">
                                          {f}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Strengths/Pros */}
                                {(r.strengths?.length > 0 || r.pros?.length > 0) && (
                                  <div>
                                    <div className="text-[11px] text-green-500 mb-2">+ Плюсы</div>
                                    <div className="flex flex-wrap gap-1.5">
                                      {(r.pros || r.strengths || []).map((s, i) => (
                                        <span key={i} className="px-2 py-0.5 text-xs bg-green-500/10 text-green-400 rounded">
                                          {s}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Weaknesses/Cons */}
                                {(r.weaknesses?.length > 0 || r.cons?.length > 0) && (
                                  <div>
                                    <div className="text-[11px] text-amber-500 mb-2">− Минусы</div>
                                    <div className="flex flex-wrap gap-1.5">
                                      {(r.cons || r.weaknesses || []).map((w, i) => (
                                        <span key={i} className="px-2 py-0.5 text-xs bg-amber-500/10 text-amber-400 rounded">
                                          {w}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Red Flags */}
                                {r.red_flags?.length > 0 && (
                                  <div>
                                    <div className="text-[11px] text-red-500 mb-2">⚠ Красные флаги</div>
                                    <div className="flex flex-wrap gap-1.5">
                                      {r.red_flags.map((f, i) => (
                                        <span key={i} className="px-2 py-0.5 text-xs bg-red-500/10 text-red-400 rounded border border-red-500/20">
                                          {f}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Contact Info + Resume Link */}
                              <div className="flex items-center gap-4 pt-2 border-t border-zinc-800/50">
                                {r.application?.candidate_phone && (
                                  <a
                                    href={`tel:${r.application.candidate_phone}`}
                                    className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    <Phone className="h-3.5 w-3.5" />
                                    {r.application.candidate_phone}
                                  </a>
                                )}
                                {r.application?.resume_url && (
                                  <a
                                    href={r.application.resume_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    <ExternalLink className="h-3.5 w-3.5" />
                                    Резюме на HH.ru
                                  </a>
                                )}
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      <LimitExceededModal
        isOpen={limitModalOpen}
        onClose={() => setLimitModalOpen(false)}
        subscriptionInfo={limitExceededInfo}
      />
    </div>
  );
};

export default Analysis;
