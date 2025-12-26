/**
 * Analysis - Анализ резюме
 * Design: Dark Industrial - единый стиль с Dashboard
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Brain,
  Download,
  ExternalLink,
  Phone,
  Square,
  Clock,
  Zap,
  ChevronDown,
  ChevronUp,
  Settings,
  ArrowRight
} from 'lucide-react';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/services/api';
import { Vacancy, AnalysisResult, AnalysisFilter } from '@/types';
import { useApp } from '@/store/AppContext';
import { AnalysisLimitsDisplay } from '@/components/AnalysisLimitsDisplay';
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

const Analysis: React.FC = () => {
  const app = useApp();
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [selectedVacancy, setSelectedVacancy] = useState<string>('all');
  const [results, setResults] = useState<AnalysisWithApplication[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendationFilter, setRecommendationFilter] = useState<string>('all');
  const [applicationsStats, setApplicationsStats] = useState<any>(null);
  const [dashboardStats, setDashboardStats] = useState<any>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [analysisLimit, setAnalysisLimit] = useState<number>(100);
  const [limitModalOpen, setLimitModalOpen] = useState(false);
  const [limitExceededInfo, setLimitExceededInfo] = useState<any>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());

  const isAnalyzing = app.activeAnalysis !== null && app.activeAnalysis.vacancyId === selectedVacancy;
  const analysisProgress = app.activeAnalysis || { total: 0, analyzed: 0, startTime: 0, vacancyId: '' };

  // Загрузка вакансий
  useEffect(() => {
    loadVacancies();
  }, []);

  // Загрузка результатов при изменении фильтров
  useEffect(() => {
    loadResults();
  }, [selectedVacancy, recommendationFilter]);

  // Polling для анализа
  useEffect(() => {
    if (!app.activeAnalysis) return;

    const pollStats = async () => {
      try {
        const stats = await apiClient.getApplicationsStats(app.activeAnalysis!.vacancyId);
        app.updateAnalysisProgress({ analyzed: stats.analyzed_applications });

        if (stats.unanalyzed_applications === 0 || stats.analyzed_applications >= app.activeAnalysis!.total) {
          app.stopAnalysis();
          loadResults();
          loadApplicationsStats();
          loadDashboardStats();
        }
      } catch (err) {
        console.error('[Analysis] Polling error:', err);
      }
    };

    app.startGlobalPolling(pollStats, 3000, 300000);
  }, [app.activeAnalysis?.vacancyId]);

  // Загрузка статистики
  useEffect(() => {
    if (selectedVacancy !== 'all') {
      loadApplicationsStats();
      loadDashboardStats();
    } else {
      setApplicationsStats(null);
      setDashboardStats(null);
    }
  }, [selectedVacancy]);

  const loadVacancies = async () => {
    try {
      const data = await apiClient.getVacancies({ active_only: true });
      setVacancies(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error loading vacancies:', err);
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

      const data = await apiClient.getAnalysisResults(filters);
      setResults(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error loading results:', err);
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
    setError(null);

    const toAnalyze = Math.ceil((applicationsStats?.unanalyzed_applications || 0) * analysisLimit / 100);
    app.startAnalysis({
      vacancyId: selectedVacancy,
      total: toAnalyze,
      analyzed: 0,
      startTime: Date.now()
    });

    try {
      await apiClient.startAnalysisNewApplications(selectedVacancy, undefined, toAnalyze);
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
    } catch (err: any) {
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
      case 'interview': return 'bg-blue-500/15 text-blue-500';
      case 'maybe': return 'bg-amber-500/15 text-amber-500';
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

  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  };

  const statsData = dashboardStats ? {
    total: dashboardStats.total_analyzed || 0,
    hire: dashboardStats.hire_count || 0,
    interview: dashboardStats.interview_count || 0,
    maybe: dashboardStats.maybe_count || 0,
    reject: dashboardStats.reject_count || 0,
    avgScore: Math.round(dashboardStats.avg_score || 0),
  } : { total: 0, hire: 0, interview: 0, maybe: 0, reject: 0, avgScore: 0 };

  // Расчёт времени
  const getTimeRemaining = () => {
    if (analysisProgress.analyzed === 0) return 'Расчёт...';
    const elapsed = Date.now() - analysisProgress.startTime;
    const avg = elapsed / analysisProgress.analyzed;
    const remaining = (analysisProgress.total - analysisProgress.analyzed) * avg;
    const min = Math.floor(remaining / 60000);
    const sec = Math.floor((remaining % 60000) / 1000);
    return min > 0 ? `≈ ${min} мин ${sec} сек` : `≈ ${sec} сек`;
  };

  const speed = analysisProgress.analyzed > 0
    ? ((analysisProgress.analyzed / ((Date.now() - analysisProgress.startTime) / 1000)) * 60).toFixed(1)
    : '0';

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div {...fadeIn} className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">Анализ резюме</h1>
          <p className="text-sm text-zinc-500 mt-1">AI оценка кандидатов</p>
        </div>
        {selectedVacancy !== 'all' && applicationsStats?.analyzed_applications > 0 && (
          <Button
            onClick={handleDownloadExcel}
            disabled={isDownloading}
            variant="ghost"
            className="h-9 px-3 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 border border-zinc-700"
          >
            <Download className="h-4 w-4 mr-2" />
            <span className="text-xs">Excel</span>
          </Button>
        )}
      </motion.div>

      {/* Error */}
      {error && (
        <motion.div {...fadeIn} className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
          <p className="text-sm text-red-400">{error}</p>
        </motion.div>
      )}

      {/* Limits */}
      <AnalysisLimitsDisplay />

      {/* Filters */}
      <motion.div {...fadeIn} className="grid grid-cols-2 gap-4">
        <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
          <SelectTrigger className="bg-card border-zinc-800 text-zinc-200">
            <SelectValue placeholder="Выберите вакансию" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">Все вакансии</SelectItem>
            {vacancies.map(v => (
              <SelectItem key={v.id} value={v.id}>{v.title}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={recommendationFilter} onValueChange={setRecommendationFilter}>
          <SelectTrigger className="bg-card border-zinc-800 text-zinc-200">
            <SelectValue placeholder="Рекомендация" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">Все</SelectItem>
            <SelectItem value="hire">Нанять</SelectItem>
            <SelectItem value="interview">Собеседование</SelectItem>
            <SelectItem value="maybe">Возможно</SelectItem>
            <SelectItem value="reject">Отклонить</SelectItem>
          </SelectContent>
        </Select>
      </motion.div>

      {/* No vacancy selected */}
      {selectedVacancy === 'all' && (
        <motion.div {...fadeIn} className="flex items-center gap-3 text-sm text-zinc-500">
          <Brain className="h-4 w-4" />
          <span>Выберите вакансию для запуска анализа</span>
        </motion.div>
      )}

      {/* Analysis panel */}
      {selectedVacancy !== 'all' && applicationsStats && (
        <motion.div {...fadeIn}>
          {/* Stats grid */}
          <div className="grid grid-cols-3 gap-px bg-zinc-800 border border-zinc-800 rounded-lg overflow-hidden mb-4">
            <div className="bg-card p-5">
              <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
                Всего
              </div>
              <div className="text-3xl font-semibold tabular-nums">
                {applicationsStats.total_applications}
              </div>
            </div>
            <div className="bg-card p-5">
              <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
                Проанализировано
              </div>
              <div className="text-3xl font-semibold tabular-nums">
                {applicationsStats.analyzed_applications}
              </div>
            </div>
            <div className="bg-card p-5">
              <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
                Новых
              </div>
              <div className="text-3xl font-semibold tabular-nums">
                {applicationsStats.unanalyzed_applications}
              </div>
            </div>
          </div>

          {/* Slider */}
          {applicationsStats.unanalyzed_applications > 0 && !isAnalyzing && (
            <div className="mb-4 p-4 bg-card border border-zinc-800 rounded-lg">
              <div className="flex justify-between items-center mb-3">
                <span className="text-sm text-zinc-400">
                  Анализировать: {Math.ceil(applicationsStats.unanalyzed_applications * analysisLimit / 100)} из {applicationsStats.unanalyzed_applications}
                </span>
                <span className="text-lg font-semibold tabular-nums">{analysisLimit}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={analysisLimit}
                onChange={(e) => setAnalysisLimit(Number(e.target.value))}
                className="w-full h-1.5 bg-zinc-800 rounded-full appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #a1a1a1 0%, #a1a1a1 ${analysisLimit}%, #27272a ${analysisLimit}%, #27272a 100%)`
                }}
              />
              <div className="flex gap-2 mt-3">
                {[25, 50, 75, 100].map(p => (
                  <button
                    key={p}
                    onClick={() => setAnalysisLimit(p)}
                    className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                      analysisLimit === p
                        ? 'bg-zinc-100 text-zinc-900'
                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                    }`}
                  >
                    {p}%
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Start button */}
          <Button
            onClick={handleAnalyzeNew}
            disabled={isAnalyzing || applicationsStats.unanalyzed_applications === 0}
            className="w-full h-12 bg-zinc-100 text-zinc-900 hover:bg-zinc-200 disabled:opacity-50"
          >
            <Brain className="h-5 w-5 mr-2" />
            {isAnalyzing
              ? 'Анализирую...'
              : applicationsStats.unanalyzed_applications > 0
                ? `Проанализировать ${Math.ceil(applicationsStats.unanalyzed_applications * analysisLimit / 100)} резюме`
                : 'Все проанализировано'}
          </Button>

          {/* Progress */}
          {isAnalyzing && analysisProgress.total > 0 && (
            <div className="mt-4 p-4 bg-card border border-zinc-800 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center">
                    <Brain className="h-4 w-4 text-zinc-400" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-zinc-200">
                      {analysisProgress.analyzed} из {analysisProgress.total}
                    </div>
                    <div className="text-xs text-zinc-500">резюме</div>
                  </div>
                </div>
                <div className="text-2xl font-semibold tabular-nums">
                  {Math.round((analysisProgress.analyzed / analysisProgress.total) * 100)}%
                </div>
              </div>

              <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden mb-3">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(analysisProgress.analyzed / analysisProgress.total) * 100}%` }}
                  transition={{ duration: 0.5 }}
                  className="h-full bg-zinc-400 rounded-full"
                />
              </div>

              <div className="flex items-center justify-between text-xs text-zinc-500 mb-3">
                <div className="flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5" />
                  <span>{getTimeRemaining()}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Zap className="h-3.5 w-3.5" />
                  <span>{speed} рез/мин</span>
                </div>
              </div>

              <Button
                onClick={handleStopAnalysis}
                variant="ghost"
                size="sm"
                className="w-full h-8 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 border border-zinc-700"
              >
                <Square className="h-3 w-3 mr-1.5 fill-current" />
                Остановить
              </Button>
            </div>
          )}
        </motion.div>
      )}

      {/* Stats row */}
      {selectedVacancy !== 'all' && statsData.total > 0 && (
        <motion.div {...fadeIn} className="grid grid-cols-5 gap-px bg-zinc-800 border border-zinc-800 rounded-lg overflow-hidden">
          <div className="bg-card p-4 text-center">
            <div className="text-xl font-semibold tabular-nums">{statsData.avgScore}</div>
            <div className="text-[10px] text-zinc-500 mt-1">ср. балл</div>
          </div>
          <div className="bg-card p-4 text-center">
            <div className="text-xl font-semibold tabular-nums text-green-500">{statsData.hire}</div>
            <div className="text-[10px] text-zinc-500 mt-1">нанять</div>
          </div>
          <div className="bg-card p-4 text-center">
            <div className="text-xl font-semibold tabular-nums text-blue-500">{statsData.interview}</div>
            <div className="text-[10px] text-zinc-500 mt-1">собесед.</div>
          </div>
          <div className="bg-card p-4 text-center">
            <div className="text-xl font-semibold tabular-nums text-amber-500">{statsData.maybe}</div>
            <div className="text-[10px] text-zinc-500 mt-1">возможно</div>
          </div>
          <div className="bg-card p-4 text-center">
            <div className="text-xl font-semibold tabular-nums text-red-500">{statsData.reject}</div>
            <div className="text-[10px] text-zinc-500 mt-1">отклонить</div>
          </div>
        </motion.div>
      )}

      {/* Results */}
      <motion.div {...fadeIn}>
        <Card>
          <CardContent className="p-0">
            <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
              <div className="text-[13px] font-medium uppercase tracking-wide text-zinc-400">
                Результаты
              </div>
              <span className="text-xs text-zinc-500">{results.length}</span>
            </div>

            {isLoading ? (
              <div className="p-12 text-center text-zinc-500 text-sm">
                Загрузка...
              </div>
            ) : results.length === 0 ? (
              <div className="p-12 text-center">
                <div className="w-14 h-14 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center mx-auto mb-4">
                  <Brain className="h-6 w-6 text-zinc-500" />
                </div>
                <p className="text-zinc-400 text-sm mb-1">Нет результатов</p>
                <p className="text-zinc-600 text-xs">Запустите анализ или измените фильтры</p>
              </div>
            ) : (
              <div className="divide-y divide-zinc-800/50">
                {results.map((r) => (
                  <div key={r.id} className="hover:bg-zinc-900/50 transition-colors">
                    {/* Main row */}
                    <div
                      className="px-5 py-4 flex items-center justify-between cursor-pointer"
                      onClick={() => toggleExpanded(r.id)}
                    >
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        <div className="w-8 h-8 rounded-md bg-zinc-800 flex items-center justify-center text-[10px] font-medium text-zinc-500 flex-shrink-0">
                          {r.application?.candidate_name?.split(' ').map(n => n[0]).join('').slice(0, 2) || '??'}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-[13px] font-medium text-zinc-200 truncate">
                              {r.application?.candidate_name || 'Без имени'}
                            </span>
                            {r.application?.resume_url && (
                              <a
                                href={r.application.resume_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="text-zinc-500 hover:text-zinc-300"
                              >
                                <ExternalLink className="h-3.5 w-3.5" />
                              </a>
                            )}
                          </div>
                          {r.application?.candidate_phone && (
                            <div className="flex items-center gap-1 text-xs text-zinc-500 mt-0.5">
                              <Phone className="h-3 w-3" />
                              <span>{r.application.candidate_phone}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <span className="text-lg font-semibold tabular-nums">{r.score || '—'}</span>
                        <span className={`text-[11px] font-medium px-2 py-1 rounded ${getRecommendationStyle(r.recommendation)}`}>
                          {getRecommendationText(r.recommendation)}
                        </span>
                        {expandedResults.has(r.id) ? (
                          <ChevronUp className="h-4 w-4 text-zinc-500" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-zinc-500" />
                        )}
                      </div>
                    </div>

                    {/* Expanded details */}
                    {expandedResults.has(r.id) && (
                      <div className="px-5 pb-4 space-y-3">
                        {/* Metrics */}
                        <div className="grid grid-cols-3 gap-4 text-xs">
                          <div>
                            <span className="text-zinc-500">Навыки:</span>
                            <span className="ml-2 text-zinc-300">{r.skills_match || 0}%</span>
                          </div>
                          <div>
                            <span className="text-zinc-500">Опыт:</span>
                            <span className="ml-2 text-zinc-300">{r.experience_match || 0}%</span>
                          </div>
                          <div>
                            <span className="text-zinc-500">Зарплата:</span>
                            <span className="ml-2 text-zinc-300">
                              {r.salary_match === 'match' ? 'ОК' : r.salary_match === 'higher' ? '↑' : r.salary_match === 'lower' ? '↓' : '—'}
                            </span>
                          </div>
                        </div>

                        {/* Strengths */}
                        {r.strengths && r.strengths.length > 0 && (
                          <div>
                            <span className="text-[10px] uppercase tracking-wide text-green-500">Сильные стороны</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {r.strengths.map((s, i) => (
                                <span key={i} className="text-xs px-2 py-0.5 bg-green-500/10 text-green-400 rounded">
                                  {s}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Weaknesses */}
                        {r.weaknesses && r.weaknesses.length > 0 && (
                          <div>
                            <span className="text-[10px] uppercase tracking-wide text-amber-500">Слабые стороны</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {r.weaknesses.map((w, i) => (
                                <span key={i} className="text-xs px-2 py-0.5 bg-amber-500/10 text-amber-400 rounded">
                                  {w}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Red flags */}
                        {r.red_flags && r.red_flags.length > 0 && (
                          <div>
                            <span className="text-[10px] uppercase tracking-wide text-red-500">Риски</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {r.red_flags.map((f, i) => (
                                <span key={i} className="text-xs px-2 py-0.5 bg-red-500/10 text-red-400 rounded">
                                  {f}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Reasoning */}
                        {r.reasoning && (
                          <div className="text-xs text-zinc-400 p-3 bg-zinc-900 rounded">
                            {r.reasoning}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
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
