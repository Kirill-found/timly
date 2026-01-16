/**
 * Analysis - AI Resume Analyzer v7.0 (Hybrid Expert)
 * Design: Dark Industrial + Data Dashboard
 *
 * v7.0 Features:
 * - Verdict-based evaluation (High/Medium/Low/Mismatch)
 * - Must-haves validation with visual status
 * - Holistic analysis with career trajectory
 * - Reasoning for HR as primary explanation
 * - Interview questions with context
 */
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download, ExternalLink, Phone, Square, Play, ChevronDown, ChevronUp,
  AlertCircle, MessageSquare, CheckCircle2, HelpCircle, XCircle,
  TrendingUp, TrendingDown, Minus, User, FileText, Sparkles
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/services/api';
import {
  Vacancy, AnalysisResult, AnalysisFilter, Verdict, MustHave,
  HolisticAnalysis, InterviewQuestion
} from '@/types';
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

// === v7.0 VERDICT BADGE ===
const VerdictBadge: React.FC<{ verdict?: Verdict; size?: 'sm' | 'md' | 'lg' }> = ({ verdict, size = 'md' }) => {
  const config = {
    High: {
      bg: 'bg-emerald-500/15',
      border: 'border-emerald-500/40',
      text: 'text-emerald-400',
      glow: 'shadow-emerald-500/20',
      label: 'Рекомендую',
      icon: <CheckCircle2 className="w-3.5 h-3.5" />
    },
    Medium: {
      bg: 'bg-blue-500/15',
      border: 'border-blue-500/40',
      text: 'text-blue-400',
      glow: 'shadow-blue-500/20',
      label: 'На рассмотрение',
      icon: <HelpCircle className="w-3.5 h-3.5" />
    },
    Low: {
      bg: 'bg-amber-500/15',
      border: 'border-amber-500/40',
      text: 'text-amber-400',
      glow: 'shadow-amber-500/20',
      label: 'Сомнительно',
      icon: <AlertCircle className="w-3.5 h-3.5" />
    },
    Mismatch: {
      bg: 'bg-red-500/15',
      border: 'border-red-500/40',
      text: 'text-red-400',
      glow: 'shadow-red-500/20',
      label: 'Не подходит',
      icon: <XCircle className="w-3.5 h-3.5" />
    }
  };

  const c = verdict ? config[verdict] : config.Low;

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px] gap-1',
    md: 'px-3 py-1 text-xs gap-1.5',
    lg: 'px-4 py-1.5 text-sm gap-2'
  };

  return (
    <div className={`
      inline-flex items-center ${sizes[size]} rounded-lg font-medium
      ${c.bg} ${c.border} ${c.text} border shadow-lg ${c.glow}
      transition-all duration-200
    `}>
      {c.icon}
      <span>{c.label}</span>
    </div>
  );
};

// === MUST-HAVE STATUS ICON ===
const MustHaveIcon: React.FC<{ status: 'yes' | 'maybe' | 'no' }> = ({ status }) => {
  const config = {
    yes: { icon: <CheckCircle2 className="w-4 h-4" />, color: 'text-emerald-400' },
    maybe: { icon: <HelpCircle className="w-4 h-4" />, color: 'text-amber-400' },
    no: { icon: <XCircle className="w-4 h-4" />, color: 'text-red-400' }
  };
  const c = config[status];
  return <span className={c.color}>{c.icon}</span>;
};

// === MUST-HAVES BLOCK ===
const MustHavesBlock: React.FC<{ mustHaves: MustHave[] }> = ({ mustHaves }) => {
  if (!mustHaves?.length) return null;

  const hasAnyNo = mustHaves.some(m => m.status === 'no');

  return (
    <div className={`
      p-4 rounded-xl border
      ${hasAnyNo ? 'bg-red-500/5 border-red-500/20' : 'bg-zinc-800/30 border-zinc-700/30'}
    `}>
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className={`w-4 h-4 ${hasAnyNo ? 'text-red-400' : 'text-zinc-400'}`} />
        <span className={`text-[11px] font-semibold uppercase tracking-wider ${hasAnyNo ? 'text-red-400' : 'text-zinc-400'}`}>
          Ключевые требования
        </span>
      </div>
      <div className="space-y-2.5">
        {mustHaves.map((mh, i) => (
          <div key={i} className="flex items-start gap-3">
            <MustHaveIcon status={mh.status} />
            <div className="flex-1 min-w-0">
              <div className="text-sm text-zinc-200 leading-snug">{mh.requirement}</div>
              {mh.evidence && (
                <div className="text-xs text-zinc-500 mt-0.5 italic">"{mh.evidence}"</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// === REASONING BLOCK (главное для HR) ===
const ReasoningBlock: React.FC<{ reasoning?: string; verdict?: Verdict }> = ({ reasoning, verdict }) => {
  if (!reasoning) return null;

  const borderColor = {
    High: 'border-l-emerald-500',
    Medium: 'border-l-blue-500',
    Low: 'border-l-amber-500',
    Mismatch: 'border-l-red-500'
  }[verdict || 'Medium'];

  return (
    <div className={`
      p-4 rounded-r-xl bg-zinc-800/40 border-l-4 ${borderColor}
    `}>
      <div className="flex items-center gap-2 mb-2">
        <FileText className="w-4 h-4 text-zinc-400" />
        <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
          Заключение для HR
        </span>
      </div>
      <p className="text-sm text-zinc-300 leading-relaxed">{reasoning}</p>
    </div>
  );
};

// === INTERVIEW QUESTIONS v7.0 ===
const InterviewQuestionsBlock: React.FC<{
  questions?: InterviewQuestion[];
  legacyQuestions?: string[];
}> = ({ questions, legacyQuestions }) => {
  // Поддержка обоих форматов
  const hasV7Questions = questions && questions.length > 0;
  const hasLegacyQuestions = legacyQuestions && legacyQuestions.length > 0;

  if (!hasV7Questions && !hasLegacyQuestions) return null;

  return (
    <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
      <div className="flex items-center gap-2 mb-3">
        <MessageSquare className="w-4 h-4 text-blue-400" />
        <span className="text-[11px] font-semibold uppercase tracking-wider text-blue-400">
          Вопросы для интервью
        </span>
      </div>

      {hasV7Questions ? (
        <div className="space-y-3">
          {questions!.map((q, i) => (
            <div key={i} className="pl-3 border-l-2 border-blue-500/30">
              <div className="text-sm text-zinc-200">{q.question}</div>
              <div className="text-xs text-blue-400/70 mt-1 flex items-center gap-1">
                <span className="opacity-60">Проверяем:</span> {q.checks}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <ul className="space-y-2">
          {legacyQuestions!.map((q, i) => (
            <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              {typeof q === 'string' ? q : (q as any).question || JSON.stringify(q)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

// === GROWTH PATTERN BADGE ===
const GrowthPatternBadge: React.FC<{ pattern?: string }> = ({ pattern }) => {
  if (!pattern) return null;

  const config: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
    'растёт': { icon: <TrendingUp className="w-3 h-3" />, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    'стабилен': { icon: <Minus className="w-3 h-3" />, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    'деградирует': { icon: <TrendingDown className="w-3 h-3" />, color: 'text-red-400', bg: 'bg-red-500/10' },
    'непонятно': { icon: <HelpCircle className="w-3 h-3" />, color: 'text-zinc-400', bg: 'bg-zinc-500/10' }
  };

  const c = config[pattern] || config['непонятно'];

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] ${c.color} ${c.bg}`}>
      {c.icon}
      <span>Карьера: {pattern}</span>
    </span>
  );
};

// === SALARY FIT BADGE ===
const SalaryFitBadge: React.FC<{ status?: string }> = ({ status }) => {
  if (!status || status === '—') return null;

  const isMatch = status.includes('вилке') || status.includes('ниже');
  const isHigh = status.includes('выше');

  return (
    <span className={`
      px-2 py-0.5 rounded text-[10px]
      ${isMatch ? 'bg-emerald-500/10 text-emerald-400' :
        isHigh ? 'bg-amber-500/10 text-amber-400' :
        'bg-zinc-500/10 text-zinc-400'}
    `}>
      ₽ {status}
    </span>
  );
};

// === HELPERS ===
const getVerdict = (r: AnalysisWithApplication): Verdict | undefined => {
  if (r.verdict) return r.verdict;
  if (r.raw_result?.verdict) return r.raw_result.verdict as Verdict;
  // Fallback from recommendation
  if (r.recommendation === 'hire') return 'High';
  if (r.recommendation === 'interview') return 'Medium';
  if (r.recommendation === 'maybe') return 'Low';
  if (r.recommendation === 'reject') return 'Mismatch';
  return undefined;
};

const getMustHaves = (r: AnalysisWithApplication): MustHave[] => {
  if (r.must_haves?.length) return r.must_haves;
  if (r.raw_result?.must_haves?.length) return r.raw_result.must_haves;
  return [];
};

const getHolisticAnalysis = (r: AnalysisWithApplication): HolisticAnalysis | null => {
  if (r.holistic_analysis) return r.holistic_analysis;
  if (r.raw_result?.holistic_analysis) return r.raw_result.holistic_analysis;
  return null;
};

const getReasoningForHR = (r: AnalysisWithApplication): string | undefined => {
  if (r.reasoning_for_hr) return r.reasoning_for_hr;
  if (r.raw_result?.reasoning_for_hr) return r.raw_result.reasoning_for_hr;
  // Fallback to verdict_reason
  if (r.raw_result?.verdict_reason) return r.raw_result.verdict_reason;
  return r.summary || r.reasoning;
};

const getInterviewQuestionsV7 = (r: AnalysisWithApplication): InterviewQuestion[] => {
  if (r.interview_questions_v7?.length) return r.interview_questions_v7;
  if (r.raw_result?.interview_questions?.length) {
    const qs = r.raw_result.interview_questions;
    // Check if v7 format
    if (qs[0]?.checks !== undefined) return qs;
  }
  return [];
};

const getLegacyInterviewQuestions = (r: AnalysisWithApplication): string[] => {
  if (r.interview_questions?.length) return r.interview_questions;
  if (r.raw_result?.interview_questions?.length) {
    const qs = r.raw_result.interview_questions;
    // Check if legacy format (strings or objects without checks)
    if (typeof qs[0] === 'string') return qs;
    if (qs[0]?.question && qs[0]?.checks === undefined) {
      return qs.map((q: any) => q.question);
    }
  }
  return [];
};

const getSalaryFit = (r: AnalysisWithApplication): string => {
  if (r.salary_fit?.status) return r.salary_fit.status;
  if (r.raw_result?.salary_fit?.status) return r.raw_result.salary_fit.status;
  return '—';
};

const getStrengths = (r: AnalysisWithApplication): string[] => {
  return r.strengths || r.pros || r.raw_result?.strengths || [];
};

const getConcerns = (r: AnalysisWithApplication): string[] => {
  return r.concerns || r.cons || r.weaknesses || r.raw_result?.concerns || [];
};

// === MAIN COMPONENT ===
const Analysis: React.FC = () => {
  const app = useApp();
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [selectedVacancy, setSelectedVacancy] = useState<string>('all');
  const [results, setResults] = useState<AnalysisWithApplication[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verdictFilter, setVerdictFilter] = useState<string>('all');
  const [applicationsStats, setApplicationsStats] = useState<any>(null);
  const [dashboardStats, setDashboardStats] = useState<any>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [limitModalOpen, setLimitModalOpen] = useState(false);
  const [limitExceededInfo, setLimitExceededInfo] = useState<any>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [limits, setLimits] = useState<any>(null);

  // Polling state
  const pollingDataRef = useRef<{
    initialAnalyzed: number | null;
    intervalId: NodeJS.Timeout | null;
    lastProgress: number;
    noProgressSince: number | null;
  }>({ initialAnalyzed: null, intervalId: null, lastProgress: 0, noProgressSince: null });

  const isAnalyzing = app.activeAnalysis !== null && app.activeAnalysis.vacancyId === selectedVacancy;
  const analysisProgress = app.activeAnalysis || { total: 0, analyzed: 0, startTime: 0, vacancyId: '' };

  // Effects
  useEffect(() => { loadVacancies(); loadLimits(); }, []);
  useEffect(() => { loadResults(); }, [selectedVacancy, verdictFilter]);
  useEffect(() => {
    if (selectedVacancy !== 'all') {
      loadApplicationsStats();
      loadDashboardStats();
    } else {
      setApplicationsStats(null);
      setDashboardStats(null);
    }
  }, [selectedVacancy]);

  // Polling effect
  useEffect(() => {
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

        if (pollingDataRef.current.initialAnalyzed === null) {
          pollingDataRef.current.initialAnalyzed = currentAnalyzed;
        }

        const newlyAnalyzed = currentAnalyzed - pollingDataRef.current.initialAnalyzed;
        const safeProgress = Math.max(0, Math.min(newlyAnalyzed, targetTotal));

        app.updateAnalysisProgress({ analyzed: safeProgress });

        const now = Date.now();
        if (safeProgress > pollingDataRef.current.lastProgress) {
          pollingDataRef.current.lastProgress = safeProgress;
          pollingDataRef.current.noProgressSince = null;
        } else if (pollingDataRef.current.noProgressSince === null) {
          pollingDataRef.current.noProgressSince = now;
        }

        const NO_PROGRESS_TIMEOUT = 30000;
        const noProgressTime = pollingDataRef.current.noProgressSince
          ? now - pollingDataRef.current.noProgressSince
          : 0;

        const isComplete = stats.unanalyzed_applications === 0 || safeProgress >= targetTotal;
        const isTimeout = noProgressTime >= NO_PROGRESS_TIMEOUT;

        if (isComplete || isTimeout) {
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
        }
      } catch (err) {
        console.error('[Analysis] Polling error:', err);
      }
    };

    if (pollingDataRef.current.intervalId) {
      clearInterval(pollingDataRef.current.intervalId);
    }

    pollStats();
    pollingDataRef.current.intervalId = setInterval(pollStats, 3000);

    return () => {
      if (pollingDataRef.current.intervalId) {
        clearInterval(pollingDataRef.current.intervalId);
        pollingDataRef.current.intervalId = null;
      }
    };
  }, [app.activeAnalysis?.vacancyId, app.activeAnalysis?.total]);

  // API calls
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
      let data = await apiClient.getAnalysisResults(filters);
      data = Array.isArray(data) ? data : [];

      // Filter by verdict locally
      if (verdictFilter !== 'all') {
        data = data.filter((r: AnalysisWithApplication) => getVerdict(r) === verdictFilter);
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

    const remaining = limits?.analyses_remaining || 0;
    if (!limits?.is_unlimited && remaining <= 0) {
      setLimitExceededInfo(limits);
      setLimitModalOpen(true);
      return;
    }

    const actualToAnalyze = limits?.is_unlimited ? toAnalyze : Math.min(toAnalyze, remaining);

    setError(null);
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
      const blob = await apiClient.downloadExcelReport(selectedVacancy);
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

  // Computed values
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

  const limitsRemaining = limits?.analyses_remaining ?? 0;
  const limitsTotal = limits?.analyses_limit ?? 20;
  const limitsUsed = limits?.analyses_used ?? 0;
  const isUnlimited = limits?.is_unlimited ?? false;

  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  };

  // Count verdicts for stats
  const verdictCounts = results.reduce((acc, r) => {
    const v = getVerdict(r) || 'Low';
    acc[v] = (acc[v] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div {...fadeIn} className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">AI-анализ резюме</h1>
          <p className="text-sm text-zinc-500 mt-1">v7.0 Hybrid Expert</p>
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

      {/* Limits */}
      {limits && !isUnlimited && (
        <motion.div {...fadeIn}>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-6">
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
      <motion.div {...fadeIn} className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

        <Select value={verdictFilter} onValueChange={setVerdictFilter}>
          <SelectTrigger className="h-11 bg-card border-zinc-800">
            <SelectValue placeholder="Фильтр по вердикту" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">Все вердикты</SelectItem>
            <SelectItem value="High">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Рекомендую</span>
              </div>
            </SelectItem>
            <SelectItem value="Medium">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-blue-400" />
                <span>На рассмотрение</span>
              </div>
            </SelectItem>
            <SelectItem value="Low">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-400" />
                <span>Сомнительно</span>
              </div>
            </SelectItem>
            <SelectItem value="Mismatch">
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-red-400" />
                <span>Не подходит</span>
              </div>
            </SelectItem>
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
                Рекомендую
              </div>
              <div className="text-3xl font-semibold tracking-tight tabular-nums text-emerald-400">
                {verdictCounts['High'] || 0}
              </div>
            </div>
          </div>

          {/* Analysis Control */}
          {!isAnalyzing ? (
            <Card>
              <CardContent className="p-5">
                {applicationsStats.unanalyzed_applications > 0 ? (
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-zinc-400 mb-1">
                        {applicationsStats.unanalyzed_applications} резюме ожидают анализа
                      </div>
                      {!isUnlimited && limitsRemaining < applicationsStats.unanalyzed_applications && (
                        <div className="text-xs text-amber-400">
                          Лимит: {limitsRemaining} из {applicationsStats.unanalyzed_applications}
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
            <Card>
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div className="text-sm font-medium text-zinc-200">Анализ выполняется</div>
                    <div className="text-xs text-zinc-500 mt-0.5">
                      {analysisProgress.analyzed} из {analysisProgress.total} резюме
                    </div>
                  </div>
                  <div className="text-3xl font-semibold tabular-nums">{progressPercent}%</div>
                </div>
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

      {/* Verdict Distribution */}
      {selectedVacancy !== 'all' && results.length > 0 && (
        <motion.div {...fadeIn}>
          <Card>
            <CardHeader className="pb-0">
              <CardTitle className="text-[13px] font-medium uppercase tracking-wide">
                Распределение вердиктов
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-4 gap-4">
                {[
                  { key: 'High', label: 'Рекомендую', color: 'bg-emerald-500', textColor: 'text-emerald-400' },
                  { key: 'Medium', label: 'На рассмотрение', color: 'bg-blue-500', textColor: 'text-blue-400' },
                  { key: 'Low', label: 'Сомнительно', color: 'bg-amber-500', textColor: 'text-amber-400' },
                  { key: 'Mismatch', label: 'Не подходит', color: 'bg-red-500', textColor: 'text-red-400' },
                ].map((item) => (
                  <div key={item.key} className="text-center">
                    <div className="flex items-center justify-center gap-2 mb-1">
                      <div className={`w-2 h-2 rounded-sm ${item.color}`} />
                      <span className="text-xs text-zinc-500">{item.label}</span>
                    </div>
                    <div className={`text-2xl font-semibold tabular-nums ${item.textColor}`}>
                      {verdictCounts[item.key] || 0}
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

      {/* Results */}
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
                  const verdict = getVerdict(r);
                  const mustHaves = getMustHaves(r);
                  const holistic = getHolisticAnalysis(r);
                  const reasoningForHR = getReasoningForHR(r);
                  const interviewQuestionsV7 = getInterviewQuestionsV7(r);
                  const legacyQuestions = getLegacyInterviewQuestions(r);
                  const salaryFit = getSalaryFit(r);
                  const strengths = getStrengths(r);
                  const concerns = getConcerns(r);

                  return (
                    <div key={r.id} className="border-b border-zinc-800/50 last:border-b-0">
                      {/* Collapsed View */}
                      <div
                        className="px-5 py-4 flex items-center gap-4 cursor-pointer hover:bg-zinc-900/50 transition-colors"
                        onClick={() => toggleExpanded(r.id)}
                      >
                        {/* Verdict Badge */}
                        <VerdictBadge verdict={verdict} size="md" />

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
                            <GrowthPatternBadge pattern={holistic?.growth_pattern} />
                            <SalaryFitBadge status={salaryFit} />
                          </div>
                          {/* Career summary */}
                          {holistic?.career_summary && (
                            <div className="text-xs text-zinc-500 mt-0.5 truncate">
                              {holistic.career_summary}
                            </div>
                          )}
                        </div>

                        {/* Phone */}
                        {r.application?.candidate_phone && (
                          <a
                            href={`tel:${r.application.candidate_phone}`}
                            onClick={(e) => e.stopPropagation()}
                            className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300"
                          >
                            <Phone className="h-3.5 w-3.5" />
                            <span className="hidden md:inline">{r.application.candidate_phone}</span>
                          </a>
                        )}

                        {/* Chevron */}
                        {expandedResults.has(r.id) ? (
                          <ChevronUp className="h-4 w-4 text-zinc-500" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-zinc-500" />
                        )}
                      </div>

                      {/* Expanded View */}
                      <AnimatePresence>
                        {expandedResults.has(r.id) && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                          >
                            <div className="px-5 pb-5 pt-2 space-y-4">
                              {/* Reasoning for HR - главный блок */}
                              <ReasoningBlock reasoning={reasoningForHR} verdict={verdict} />

                              {/* Must-haves */}
                              <MustHavesBlock mustHaves={mustHaves} />

                              {/* Interview Questions */}
                              <InterviewQuestionsBlock
                                questions={interviewQuestionsV7}
                                legacyQuestions={legacyQuestions}
                              />

                              {/* Strengths & Concerns */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {strengths.length > 0 && (
                                  <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                                    <div className="text-[11px] font-semibold uppercase tracking-wider text-emerald-400 mb-2">
                                      + Сильные стороны
                                    </div>
                                    <ul className="space-y-1.5">
                                      {strengths.slice(0, 5).map((s, i) => (
                                        <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
                                          <span className="text-emerald-400 mt-0.5">•</span>
                                          {s}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {concerns.length > 0 && (
                                  <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
                                    <div className="text-[11px] font-semibold uppercase tracking-wider text-amber-400 mb-2">
                                      − Сомнения
                                    </div>
                                    <ul className="space-y-1.5">
                                      {concerns.slice(0, 5).map((c, i) => (
                                        <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
                                          <span className="text-amber-400 mt-0.5">•</span>
                                          {c}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>

                              {/* Red Flags */}
                              {r.red_flags?.length > 0 && (
                                <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20">
                                  <div className="text-[11px] font-semibold uppercase tracking-wider text-red-400 mb-2">
                                    ⚠ Красные флаги
                                  </div>
                                  <div className="flex flex-wrap gap-1.5">
                                    {r.red_flags.map((f, i) => (
                                      <span key={i} className="px-2 py-0.5 text-xs bg-red-500/10 text-red-400 rounded border border-red-500/20">
                                        {f}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Contact + Resume */}
                              <div className="flex items-center gap-4 pt-2 border-t border-zinc-800/50">
                                {r.application?.candidate_phone && (
                                  <a
                                    href={`tel:${r.application.candidate_phone}`}
                                    className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200"
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
