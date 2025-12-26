/**
 * Analysis - AI Resume Analysis Command Center
 * Design: Mission Control Terminal - data-dense, professional, with depth
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, ExternalLink, Phone, Square, ChevronRight } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/services/api';
import { Vacancy, AnalysisResult, AnalysisFilter } from '@/types';
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
  const [limits, setLimits] = useState<any>(null);

  const isAnalyzing = app.activeAnalysis !== null && app.activeAnalysis.vacancyId === selectedVacancy;
  const analysisProgress = app.activeAnalysis || { total: 0, analyzed: 0, startTime: 0, vacancyId: '' };

  useEffect(() => { loadVacancies(); loadLimits(); }, []);
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
          loadLimits();
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

  const getRecommendationStyle = (rec?: string) => {
    switch (rec) {
      case 'hire': return { bg: '#059669', text: '#34d399', label: 'Нанять' };
      case 'interview': return { bg: '#2563eb', text: '#60a5fa', label: 'Интервью' };
      case 'maybe': return { bg: '#d97706', text: '#fbbf24', label: 'Возможно' };
      case 'reject': return { bg: '#dc2626', text: '#f87171', label: 'Отказ' };
      default: return { bg: '#52525b', text: '#a1a1aa', label: '—' };
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

  const limitsUsagePercent = limits ? Math.round((limits.analyses_used / limits.analyses_limit) * 100) : 0;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-100 p-6">
      {/* Scan line effect */}
      <div className="fixed inset-0 pointer-events-none z-50 opacity-[0.02]"
        style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.03) 2px, rgba(255,255,255,0.03) 4px)'
        }}
      />

      <div className="max-w-[1400px] mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-end justify-between"
        >
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-zinc-500">
                System Online
              </span>
            </div>
            <h1 className="text-3xl font-light tracking-tight">
              Анализ <span className="text-zinc-500">резюме</span>
            </h1>
          </div>
          {selectedVacancy !== 'all' && applicationsStats?.analyzed_applications > 0 && (
            <button
              onClick={handleDownloadExcel}
              disabled={isDownloading}
              className="flex items-center gap-2 px-4 py-2 text-xs font-mono uppercase tracking-wider text-zinc-400 border border-zinc-800 hover:border-zinc-600 hover:text-zinc-200 transition-all"
            >
              <Download className="h-3.5 w-3.5" />
              Export
            </button>
          )}
        </motion.div>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="px-4 py-3 border-l-2 border-red-500 bg-red-500/5 text-red-400 text-sm font-mono"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Limits Gauge */}
        {limits && !limits.is_unlimited && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="relative p-5 border border-zinc-800/80 bg-zinc-900/30"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <div className="text-[10px] font-mono uppercase tracking-[0.15em] text-zinc-600">
                  Quota
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-extralight tabular-nums tracking-tighter">
                    {limits.analyses_remaining}
                  </span>
                  <span className="text-sm text-zinc-600">/ {limits.analyses_limit}</span>
                </div>
              </div>
              {limits.reset_date && (
                <div className="text-[10px] font-mono text-zinc-600">
                  Reset: {new Date(limits.reset_date).toLocaleDateString('ru-RU')}
                </div>
              )}
            </div>

            {/* Gauge bar */}
            <div className="relative h-1 bg-zinc-800 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${limitsUsagePercent}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className="absolute inset-y-0 left-0"
                style={{
                  background: limitsUsagePercent > 80
                    ? 'linear-gradient(90deg, #ef4444, #f87171)'
                    : limitsUsagePercent > 50
                    ? 'linear-gradient(90deg, #f59e0b, #fbbf24)'
                    : 'linear-gradient(90deg, #18181b, #3f3f46)'
                }}
              />
              {/* Tick marks */}
              {[25, 50, 75].map(tick => (
                <div
                  key={tick}
                  className="absolute top-0 bottom-0 w-px bg-zinc-700"
                  style={{ left: `${tick}%` }}
                />
              ))}
            </div>
          </motion.div>
        )}

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 gap-4"
        >
          <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
            <SelectTrigger className="h-12 bg-transparent border-zinc-800 hover:border-zinc-700 text-zinc-300 font-mono text-sm">
              <SelectValue placeholder="Вакансия" />
            </SelectTrigger>
            <SelectContent className="bg-zinc-900 border-zinc-800">
              <SelectItem value="all" className="font-mono">Все вакансии</SelectItem>
              {vacancies.map(v => (
                <SelectItem key={v.id} value={v.id} className="font-mono">{v.title}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={recommendationFilter} onValueChange={setRecommendationFilter}>
            <SelectTrigger className="h-12 bg-transparent border-zinc-800 hover:border-zinc-700 text-zinc-300 font-mono text-sm">
              <SelectValue placeholder="Статус" />
            </SelectTrigger>
            <SelectContent className="bg-zinc-900 border-zinc-800">
              <SelectItem value="all" className="font-mono">Все статусы</SelectItem>
              <SelectItem value="hire" className="font-mono">Нанять</SelectItem>
              <SelectItem value="interview" className="font-mono">Интервью</SelectItem>
              <SelectItem value="maybe" className="font-mono">Возможно</SelectItem>
              <SelectItem value="reject" className="font-mono">Отказ</SelectItem>
            </SelectContent>
          </Select>
        </motion.div>

        {/* Stats + Control Panel */}
        {selectedVacancy !== 'all' && applicationsStats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="grid grid-cols-12 gap-4"
          >
            {/* Left: Stats Grid */}
            <div className="col-span-8 grid grid-cols-4 gap-px bg-zinc-800/50">
              {[
                { label: 'Всего', value: applicationsStats.total_applications, color: '#a1a1aa' },
                { label: 'Обработано', value: applicationsStats.analyzed_applications, color: '#34d399' },
                { label: 'В очереди', value: applicationsStats.unanalyzed_applications, color: '#fbbf24' },
                { label: 'Ср. балл', value: statsData.avgScore, color: '#60a5fa' },
              ].map((stat, i) => (
                <div key={i} className="bg-[#0f0f0f] p-5">
                  <div className="text-[10px] font-mono uppercase tracking-[0.15em] text-zinc-600 mb-2">
                    {stat.label}
                  </div>
                  <div
                    className="text-3xl font-extralight tabular-nums"
                    style={{ color: stat.color }}
                  >
                    {stat.value}
                  </div>
                </div>
              ))}
            </div>

            {/* Right: Control */}
            <div className="col-span-4 bg-[#0f0f0f] border border-zinc-800/50 p-5 flex flex-col">
              {!isAnalyzing ? (
                <>
                  {applicationsStats.unanalyzed_applications > 0 && (
                    <>
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-zinc-600">
                          Batch Size
                        </span>
                        <span className="text-lg font-light tabular-nums">
                          {Math.ceil(applicationsStats.unanalyzed_applications * analysisLimit / 100)}
                        </span>
                      </div>

                      <input
                        type="range"
                        min="10"
                        max="100"
                        step="10"
                        value={analysisLimit}
                        onChange={(e) => setAnalysisLimit(Number(e.target.value))}
                        className="w-full h-1 mb-4 appearance-none cursor-pointer"
                        style={{
                          background: `linear-gradient(to right, #3f3f46 0%, #3f3f46 ${analysisLimit}%, #18181b ${analysisLimit}%, #18181b 100%)`
                        }}
                      />
                    </>
                  )}

                  <button
                    onClick={handleAnalyzeNew}
                    disabled={applicationsStats.unanalyzed_applications === 0}
                    className={`mt-auto py-4 font-mono text-sm uppercase tracking-[0.1em] transition-all ${
                      applicationsStats.unanalyzed_applications === 0
                        ? 'bg-zinc-900 text-zinc-700 cursor-not-allowed'
                        : 'bg-zinc-100 text-zinc-900 hover:bg-white'
                    }`}
                  >
                    {applicationsStats.unanalyzed_applications > 0 ? 'Запустить' : 'Очередь пуста'}
                  </button>
                </>
              ) : (
                /* Progress */
                <div className="flex flex-col h-full">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-zinc-600">
                      Processing
                    </span>
                    <span className="text-[10px] font-mono text-zinc-500">
                      {speed}/min
                    </span>
                  </div>

                  <div className="text-4xl font-extralight tabular-nums text-emerald-400 mb-3">
                    {progressPercent}%
                  </div>

                  <div className="flex-1 flex items-center">
                    <div className="w-full space-y-1">
                      {/* Progress blocks */}
                      <div className="flex gap-0.5">
                        {Array.from({ length: 20 }).map((_, i) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0.2 }}
                            animate={{
                              opacity: i < Math.floor(progressPercent / 5) ? 1 : 0.2,
                              backgroundColor: i < Math.floor(progressPercent / 5) ? '#34d399' : '#27272a'
                            }}
                            transition={{ duration: 0.3 }}
                            className="flex-1 h-6"
                          />
                        ))}
                      </div>
                      <div className="flex justify-between text-[9px] font-mono text-zinc-600">
                        <span>{analysisProgress.analyzed}</span>
                        <span>{analysisProgress.total}</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={handleStopAnalysis}
                    className="mt-3 py-2 border border-zinc-700 text-zinc-400 hover:border-red-500/50 hover:text-red-400 font-mono text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2"
                  >
                    <Square className="h-3 w-3 fill-current" />
                    Stop
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Distribution */}
        {selectedVacancy !== 'all' && statsData.total > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="flex gap-px"
          >
            {[
              { label: 'Hire', value: statsData.hire, total: statsData.total, color: '#059669' },
              { label: 'Interview', value: statsData.interview, total: statsData.total, color: '#2563eb' },
              { label: 'Maybe', value: statsData.maybe, total: statsData.total, color: '#d97706' },
              { label: 'Reject', value: statsData.reject, total: statsData.total, color: '#dc2626' },
            ].map((item, i) => {
              const percent = item.total > 0 ? Math.round((item.value / item.total) * 100) : 0;
              return (
                <div
                  key={i}
                  className="flex-1 bg-[#0f0f0f] p-4 relative overflow-hidden group"
                >
                  <div
                    className="absolute bottom-0 left-0 right-0 transition-all duration-500 opacity-20 group-hover:opacity-30"
                    style={{
                      height: `${percent}%`,
                      backgroundColor: item.color
                    }}
                  />
                  <div className="relative">
                    <div className="text-[9px] font-mono uppercase tracking-[0.15em] text-zinc-600 mb-1">
                      {item.label}
                    </div>
                    <div className="text-2xl font-extralight tabular-nums" style={{ color: item.color }}>
                      {item.value}
                    </div>
                    <div className="text-[10px] font-mono text-zinc-600">
                      {percent}%
                    </div>
                  </div>
                </div>
              );
            })}
          </motion.div>
        )}

        {/* No vacancy hint */}
        {selectedVacancy === 'all' && (
          <div className="py-20 text-center">
            <div className="text-zinc-600 font-mono text-sm">
              Выберите вакансию для анализа
            </div>
          </div>
        )}

        {/* Results */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="border border-zinc-800/50"
        >
          <div className="px-5 py-3 border-b border-zinc-800/50 flex items-center justify-between bg-[#0f0f0f]">
            <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-zinc-500">
              Results
            </span>
            <span className="text-[10px] font-mono text-zinc-600 tabular-nums">
              {results.length} records
            </span>
          </div>

          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-block w-4 h-4 border border-zinc-600 border-t-zinc-300 rounded-full animate-spin" />
            </div>
          ) : results.length === 0 ? (
            <div className="p-12 text-center text-zinc-600 font-mono text-sm">
              No data
            </div>
          ) : (
            <div>
              {results.map((r, idx) => {
                const style = getRecommendationStyle(r.recommendation);
                const isExpanded = expandedResults.has(r.id);

                return (
                  <motion.div
                    key={r.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.02 }}
                    className="border-b border-zinc-800/30 last:border-b-0"
                  >
                    <div
                      className="px-5 py-4 flex items-center gap-5 cursor-pointer hover:bg-zinc-900/50 transition-colors group"
                      onClick={() => toggleExpanded(r.id)}
                    >
                      {/* Score */}
                      <div className="w-16 text-center">
                        <div className="text-2xl font-extralight tabular-nums">
                          {r.score || '—'}
                        </div>
                      </div>

                      {/* Status indicator */}
                      <div
                        className="w-1 h-10 rounded-full"
                        style={{ backgroundColor: style.bg }}
                      />

                      {/* Name & Contact */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3">
                          <span className="font-medium truncate">
                            {r.application?.candidate_name || 'Unknown'}
                          </span>
                          {r.application?.resume_url && (
                            <a
                              href={r.application.resume_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              className="text-zinc-600 hover:text-zinc-400 transition-colors"
                            >
                              <ExternalLink className="h-3.5 w-3.5" />
                            </a>
                          )}
                        </div>
                        {r.application?.candidate_phone && (
                          <div className="flex items-center gap-1.5 text-xs text-zinc-600 mt-0.5 font-mono">
                            <Phone className="h-3 w-3" />
                            {r.application.candidate_phone}
                          </div>
                        )}
                      </div>

                      {/* Status badge */}
                      <div
                        className="px-3 py-1 text-[10px] font-mono uppercase tracking-wider"
                        style={{
                          backgroundColor: `${style.bg}15`,
                          color: style.text
                        }}
                      >
                        {style.label}
                      </div>

                      {/* Expand icon */}
                      <ChevronRight
                        className={`h-4 w-4 text-zinc-600 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                      />
                    </div>

                    {/* Expanded content */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <div className="px-5 pb-5 ml-[84px] border-l border-zinc-800/50">
                            {/* Metrics */}
                            <div className="grid grid-cols-3 gap-4 mb-4">
                              <div className="p-3 bg-zinc-900/50">
                                <div className="text-[9px] font-mono uppercase tracking-wider text-zinc-600 mb-2">
                                  Skills Match
                                </div>
                                <div className="flex items-center gap-3">
                                  <div className="flex-1 h-0.5 bg-zinc-800">
                                    <div
                                      className="h-full bg-emerald-500"
                                      style={{ width: `${r.skills_match || 0}%` }}
                                    />
                                  </div>
                                  <span className="text-sm font-mono tabular-nums">
                                    {r.skills_match || 0}%
                                  </span>
                                </div>
                              </div>
                              <div className="p-3 bg-zinc-900/50">
                                <div className="text-[9px] font-mono uppercase tracking-wider text-zinc-600 mb-2">
                                  Experience
                                </div>
                                <div className="flex items-center gap-3">
                                  <div className="flex-1 h-0.5 bg-zinc-800">
                                    <div
                                      className="h-full bg-blue-500"
                                      style={{ width: `${r.experience_match || 0}%` }}
                                    />
                                  </div>
                                  <span className="text-sm font-mono tabular-nums">
                                    {r.experience_match || 0}%
                                  </span>
                                </div>
                              </div>
                              <div className="p-3 bg-zinc-900/50">
                                <div className="text-[9px] font-mono uppercase tracking-wider text-zinc-600 mb-2">
                                  Salary
                                </div>
                                <div className="text-sm font-mono">
                                  {r.salary_match === 'match' ? 'Match' :
                                   r.salary_match === 'higher' ? 'Above' :
                                   r.salary_match === 'lower' ? 'Below' : 'N/A'}
                                </div>
                              </div>
                            </div>

                            {/* Tags */}
                            <div className="space-y-3">
                              {r.strengths && r.strengths.length > 0 && (
                                <div>
                                  <div className="text-[9px] font-mono uppercase tracking-wider text-emerald-500/70 mb-2">
                                    Strengths
                                  </div>
                                  <div className="flex flex-wrap gap-1">
                                    {r.strengths.map((s, i) => (
                                      <span
                                        key={i}
                                        className="px-2 py-0.5 text-[11px] font-mono bg-emerald-500/10 text-emerald-400/80"
                                      >
                                        {s}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {r.weaknesses && r.weaknesses.length > 0 && (
                                <div>
                                  <div className="text-[9px] font-mono uppercase tracking-wider text-amber-500/70 mb-2">
                                    Weaknesses
                                  </div>
                                  <div className="flex flex-wrap gap-1">
                                    {r.weaknesses.map((w, i) => (
                                      <span
                                        key={i}
                                        className="px-2 py-0.5 text-[11px] font-mono bg-amber-500/10 text-amber-400/80"
                                      >
                                        {w}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {r.red_flags && r.red_flags.length > 0 && (
                                <div>
                                  <div className="text-[9px] font-mono uppercase tracking-wider text-red-500/70 mb-2">
                                    Red Flags
                                  </div>
                                  <div className="flex flex-wrap gap-1">
                                    {r.red_flags.map((f, i) => (
                                      <span
                                        key={i}
                                        className="px-2 py-0.5 text-[11px] font-mono bg-red-500/10 text-red-400/80"
                                      >
                                        {f}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Reasoning */}
                            {r.reasoning && (
                              <div className="mt-4 p-4 bg-zinc-900/30 border-l-2 border-zinc-700">
                                <div className="text-[9px] font-mono uppercase tracking-wider text-zinc-600 mb-2">
                                  Analysis
                                </div>
                                <p className="text-sm text-zinc-400 leading-relaxed">
                                  {r.reasoning}
                                </p>
                              </div>
                            )}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </div>
          )}
        </motion.div>
      </div>

      <LimitExceededModal
        isOpen={limitModalOpen}
        onClose={() => setLimitModalOpen(false)}
        subscriptionInfo={limitExceededInfo}
      />

      {/* Custom range slider styles */}
      <style>{`
        input[type="range"]::-webkit-slider-thumb {
          -webkit-appearance: none;
          width: 12px;
          height: 12px;
          background: #fafafa;
          cursor: pointer;
        }
        input[type="range"]::-moz-range-thumb {
          width: 12px;
          height: 12px;
          background: #fafafa;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  );
};

export default Analysis;
