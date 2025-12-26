/**
 * Analysis - Анализ резюме
 * Design: Tech Terminal + Data Visualization
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Download,
  ExternalLink,
  Phone,
  Square,
  Clock,
  Zap,
  ChevronDown,
  ChevronUp,
  Play,
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

  useEffect(() => { loadVacancies(); }, []);
  useEffect(() => { loadResults(); }, [selectedVacancy, recommendationFilter]);

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

  const getRecommendationColor = (rec?: string) => {
    switch (rec) {
      case 'hire': return 'bg-emerald-500';
      case 'interview': return 'bg-blue-500';
      case 'maybe': return 'bg-amber-500';
      case 'reject': return 'bg-red-500';
      default: return 'bg-zinc-600';
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

  const getTimeRemaining = () => {
    if (analysisProgress.analyzed === 0) return 'Расчёт...';
    const elapsed = Date.now() - analysisProgress.startTime;
    const avg = elapsed / analysisProgress.analyzed;
    const remaining = (analysisProgress.total - analysisProgress.analyzed) * avg;
    const min = Math.floor(remaining / 60000);
    const sec = Math.floor((remaining % 60000) / 1000);
    return min > 0 ? `~${min}м ${sec}с` : `~${sec}с`;
  };

  const speed = analysisProgress.analyzed > 0
    ? ((analysisProgress.analyzed / ((Date.now() - analysisProgress.startTime) / 1000)) * 60).toFixed(1)
    : '0';

  const progressPercent = analysisProgress.total > 0
    ? Math.round((analysisProgress.analyzed / analysisProgress.total) * 100)
    : 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Анализ</h1>
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
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Limits */}
      <AnalysisLimitsDisplay />

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
          <SelectTrigger className="h-12 bg-zinc-900/50 border-zinc-700 text-zinc-100 focus:border-zinc-500">
            <SelectValue placeholder="Выберите вакансию" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-700">
            <SelectItem value="all">Все вакансии</SelectItem>
            {vacancies.map(v => (
              <SelectItem key={v.id} value={v.id}>{v.title}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={recommendationFilter} onValueChange={setRecommendationFilter}>
          <SelectTrigger className="h-12 bg-zinc-900/50 border-zinc-700 text-zinc-100 focus:border-zinc-500">
            <SelectValue placeholder="Фильтр" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-700">
            <SelectItem value="all">Все результаты</SelectItem>
            <SelectItem value="hire">Нанять</SelectItem>
            <SelectItem value="interview">Собеседование</SelectItem>
            <SelectItem value="maybe">Возможно</SelectItem>
            <SelectItem value="reject">Отклонить</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Analysis Panel */}
      {selectedVacancy !== 'all' && applicationsStats && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Stats Cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-5 rounded-xl bg-gradient-to-br from-zinc-800/80 to-zinc-900 border border-zinc-700/50">
              <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Всего</div>
              <div className="text-4xl font-bold mt-2 tabular-nums">{applicationsStats.total_applications}</div>
            </div>
            <div className="p-5 rounded-xl bg-gradient-to-br from-zinc-800/80 to-zinc-900 border border-zinc-700/50">
              <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Обработано</div>
              <div className="text-4xl font-bold mt-2 tabular-nums text-emerald-400">{applicationsStats.analyzed_applications}</div>
            </div>
            <div className="p-5 rounded-xl bg-gradient-to-br from-zinc-800/80 to-zinc-900 border border-zinc-700/50">
              <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider">Ожидает</div>
              <div className="text-4xl font-bold mt-2 tabular-nums text-amber-400">{applicationsStats.unanalyzed_applications}</div>
            </div>
          </div>

          {/* Slider */}
          {applicationsStats.unanalyzed_applications > 0 && !isAnalyzing && (
            <div className="p-5 rounded-xl bg-zinc-900/50 border border-zinc-800">
              <div className="flex justify-between items-baseline mb-4">
                <span className="text-sm text-zinc-400">
                  Анализировать <span className="text-zinc-100 font-semibold">{Math.ceil(applicationsStats.unanalyzed_applications * analysisLimit / 100)}</span> из {applicationsStats.unanalyzed_applications}
                </span>
                <span className="text-3xl font-bold tabular-nums">{analysisLimit}%</span>
              </div>

              <div className="relative mb-4">
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={analysisLimit}
                  onChange={(e) => setAnalysisLimit(Number(e.target.value))}
                  className="w-full h-2 rounded-full appearance-none cursor-pointer bg-zinc-800"
                  style={{
                    background: `linear-gradient(to right, #10b981 0%, #10b981 ${analysisLimit}%, #27272a ${analysisLimit}%, #27272a 100%)`
                  }}
                />
              </div>

              <div className="flex gap-2">
                {[25, 50, 75, 100].map(p => (
                  <button
                    key={p}
                    onClick={() => setAnalysisLimit(p)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                      analysisLimit === p
                        ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                    }`}
                  >
                    {p}%
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Start Button */}
          {!isAnalyzing ? (
            <button
              onClick={handleAnalyzeNew}
              disabled={applicationsStats.unanalyzed_applications === 0}
              className={`w-full py-5 rounded-xl font-semibold text-lg transition-all relative overflow-hidden group ${
                applicationsStats.unanalyzed_applications === 0
                  ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:from-emerald-500 hover:to-teal-500 shadow-lg shadow-emerald-500/20'
              }`}
            >
              <span className="relative z-10 flex items-center justify-center gap-3">
                <Play className="h-5 w-5" />
                {applicationsStats.unanalyzed_applications > 0
                  ? `Запустить анализ ${Math.ceil(applicationsStats.unanalyzed_applications * analysisLimit / 100)} резюме`
                  : 'Все резюме обработаны'}
              </span>
              {applicationsStats.unanalyzed_applications > 0 && (
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
              )}
            </button>
          ) : (
            /* Progress Panel */
            <div className="p-6 rounded-xl bg-gradient-to-br from-zinc-800/50 to-zinc-900 border border-zinc-700">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="text-lg font-semibold">Анализ выполняется</div>
                  <div className="text-sm text-zinc-400 mt-1">
                    {analysisProgress.analyzed} из {analysisProgress.total} резюме
                  </div>
                </div>
                <div className="text-4xl font-bold tabular-nums text-emerald-400">
                  {progressPercent}%
                </div>
              </div>

              {/* Progress Bar */}
              <div className="h-3 bg-zinc-800 rounded-full overflow-hidden mb-4">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercent}%` }}
                  transition={{ duration: 0.5, ease: 'easeOut' }}
                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full relative"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 animate-shimmer" />
                </motion.div>
              </div>

              <div className="flex items-center justify-between text-sm text-zinc-400 mb-4">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  {getTimeRemaining()}
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-amber-400" />
                  {speed} рез/мин
                </div>
              </div>

              <Button
                onClick={handleStopAnalysis}
                variant="outline"
                className="w-full border-red-500/30 text-red-400 hover:bg-red-500/10 hover:border-red-500/50"
              >
                <Square className="h-4 w-4 mr-2 fill-current" />
                Остановить
              </Button>
            </div>
          )}
        </motion.div>
      )}

      {/* No vacancy hint */}
      {selectedVacancy === 'all' && (
        <div className="text-center py-8 text-zinc-500">
          Выберите вакансию для запуска анализа
        </div>
      )}

      {/* Distribution Stats */}
      {selectedVacancy !== 'all' && statsData.total > 0 && (
        <div className="grid grid-cols-5 gap-3">
          {[
            { label: 'Средний балл', value: statsData.avgScore, color: 'text-zinc-100' },
            { label: 'Нанять', value: statsData.hire, color: 'text-emerald-400' },
            { label: 'Собеседование', value: statsData.interview, color: 'text-blue-400' },
            { label: 'Возможно', value: statsData.maybe, color: 'text-amber-400' },
            { label: 'Отклонить', value: statsData.reject, color: 'text-red-400' },
          ].map((stat, i) => (
            <div key={i} className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800 text-center">
              <div className={`text-2xl font-bold tabular-nums ${stat.color}`}>{stat.value}</div>
              <div className="text-[11px] text-zinc-500 mt-1 uppercase tracking-wide">{stat.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Results */}
      <Card className="border-zinc-800 bg-zinc-900/30">
        <CardContent className="p-0">
          <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between">
            <span className="text-sm font-medium text-zinc-300">Результаты анализа</span>
            <span className="text-xs text-zinc-500 tabular-nums">{results.length}</span>
          </div>

          {isLoading ? (
            <div className="p-12 text-center text-zinc-500">Загрузка...</div>
          ) : results.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-zinc-400 mb-1">Нет результатов</div>
              <div className="text-xs text-zinc-600">Запустите анализ или измените фильтры</div>
            </div>
          ) : (
            <div className="divide-y divide-zinc-800/50">
              {results.map((r) => (
                <div key={r.id} className="hover:bg-zinc-800/30 transition-colors">
                  <div
                    className="px-5 py-4 flex items-center gap-4 cursor-pointer"
                    onClick={() => toggleExpanded(r.id)}
                  >
                    {/* Color indicator */}
                    <div className={`w-1 h-12 rounded-full ${getRecommendationColor(r.recommendation)}`} />

                    {/* Avatar */}
                    <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-xs font-medium text-zinc-400 flex-shrink-0">
                      {r.application?.candidate_name?.split(' ').map(n => n[0]).join('').slice(0, 2) || '??'}
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-zinc-100 truncate">
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
                        <div className="flex items-center gap-1.5 text-xs text-zinc-500 mt-1">
                          <Phone className="h-3 w-3" />
                          {r.application.candidate_phone}
                        </div>
                      )}
                    </div>

                    {/* Score & Status */}
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="text-2xl font-bold tabular-nums">{r.score || '—'}</div>
                        <div className="text-[10px] text-zinc-500">баллов</div>
                      </div>
                      <div className={`px-3 py-1.5 rounded-lg text-xs font-medium ${
                        r.recommendation === 'hire' ? 'bg-emerald-500/15 text-emerald-400' :
                        r.recommendation === 'interview' ? 'bg-blue-500/15 text-blue-400' :
                        r.recommendation === 'maybe' ? 'bg-amber-500/15 text-amber-400' :
                        r.recommendation === 'reject' ? 'bg-red-500/15 text-red-400' :
                        'bg-zinc-700 text-zinc-400'
                      }`}>
                        {getRecommendationText(r.recommendation)}
                      </div>
                      {expandedResults.has(r.id) ? (
                        <ChevronUp className="h-5 w-5 text-zinc-500" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-zinc-500" />
                      )}
                    </div>
                  </div>

                  {/* Expanded */}
                  {expandedResults.has(r.id) && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="px-5 pb-5 ml-[60px]"
                    >
                      {/* Metrics */}
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="p-3 rounded-lg bg-zinc-800/50">
                          <div className="text-xs text-zinc-500 mb-1">Навыки</div>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                              <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${r.skills_match || 0}%` }} />
                            </div>
                            <span className="text-sm font-medium tabular-nums">{r.skills_match || 0}%</span>
                          </div>
                        </div>
                        <div className="p-3 rounded-lg bg-zinc-800/50">
                          <div className="text-xs text-zinc-500 mb-1">Опыт</div>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${r.experience_match || 0}%` }} />
                            </div>
                            <span className="text-sm font-medium tabular-nums">{r.experience_match || 0}%</span>
                          </div>
                        </div>
                        <div className="p-3 rounded-lg bg-zinc-800/50">
                          <div className="text-xs text-zinc-500 mb-1">Зарплата</div>
                          <div className="text-sm font-medium">
                            {r.salary_match === 'match' ? '✓ Совпадает' :
                             r.salary_match === 'higher' ? '↑ Выше' :
                             r.salary_match === 'lower' ? '↓ Ниже' : '— Не указана'}
                          </div>
                        </div>
                      </div>

                      {/* Tags */}
                      <div className="space-y-3">
                        {r.strengths && r.strengths.length > 0 && (
                          <div>
                            <div className="text-xs text-emerald-400 mb-2 font-medium">Сильные стороны</div>
                            <div className="flex flex-wrap gap-1.5">
                              {r.strengths.map((s, i) => (
                                <span key={i} className="px-2.5 py-1 text-xs bg-emerald-500/10 text-emerald-300 rounded-md border border-emerald-500/20">
                                  {s}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {r.weaknesses && r.weaknesses.length > 0 && (
                          <div>
                            <div className="text-xs text-amber-400 mb-2 font-medium">Слабые стороны</div>
                            <div className="flex flex-wrap gap-1.5">
                              {r.weaknesses.map((w, i) => (
                                <span key={i} className="px-2.5 py-1 text-xs bg-amber-500/10 text-amber-300 rounded-md border border-amber-500/20">
                                  {w}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {r.red_flags && r.red_flags.length > 0 && (
                          <div>
                            <div className="text-xs text-red-400 mb-2 font-medium">Риски</div>
                            <div className="flex flex-wrap gap-1.5">
                              {r.red_flags.map((f, i) => (
                                <span key={i} className="px-2.5 py-1 text-xs bg-red-500/10 text-red-300 rounded-md border border-red-500/20">
                                  {f}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Reasoning */}
                      {r.reasoning && (
                        <div className="mt-4 p-4 rounded-lg bg-zinc-800/30 border border-zinc-700/50 text-sm text-zinc-300 leading-relaxed">
                          {r.reasoning}
                        </div>
                      )}
                    </motion.div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <LimitExceededModal
        isOpen={limitModalOpen}
        onClose={() => setLimitModalOpen(false)}
        subscriptionInfo={limitExceededInfo}
      />

      {/* Shimmer animation */}
      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  );
};

export default Analysis;
