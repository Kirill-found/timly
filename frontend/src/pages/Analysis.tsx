/**
 * Analysis v7.2 — AI Resume Analyzer
 * Design: Dark Industrial + Minimal Data Cards
 *
 * Key changes:
 * - Priority stars (⭐⭐⭐ top / ⭐⭐ strong / ⭐ basic)
 * - One-liner explanation visible in list
 * - Actual salary from resume
 * - Cover letter indicator
 * - No scores, no progress bars, no fragmented pros/cons
 */
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download, ExternalLink, Phone, Square, Play, ChevronDown, ChevronUp,
  AlertCircle, MessageSquare, CheckCircle2, HelpCircle, XCircle,
  Star, FileText, Mail
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/services/api';
import {
  Vacancy, AnalysisResult, AnalysisFilter, Verdict, MustHave,
  HolisticAnalysis, InterviewQuestion, Priority
} from '@/types';
import { useApp } from '@/store/AppContext';
import { LimitExceededModal } from '@/components/LimitExceededModal';

interface AnalysisWithApplication extends AnalysisResult {
  application?: {
    candidate_name?: string;
    candidate_email?: string;
    candidate_phone?: string;
    resume_url?: string;
    resume_data?: any;
    created_at?: string;
  };
}

// === PRIORITY STARS ===
const PriorityStars: React.FC<{ priority?: Priority; verdict?: Verdict }> = ({ priority, verdict }) => {
  // Only show stars for High verdict
  if (verdict !== 'High') return null;

  const count = priority === 'top' ? 3 : priority === 'strong' ? 2 : 1;

  return (
    <div className="flex items-center gap-0.5">
      {[...Array(count)].map((_, i) => (
        <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
      ))}
      {[...Array(3 - count)].map((_, i) => (
        <Star key={i + count} className="w-4 h-4 text-zinc-700" />
      ))}
    </div>
  );
};

// === VERDICT BADGE (compact) ===
const VerdictBadge: React.FC<{ verdict?: Verdict }> = ({ verdict }) => {
  const config = {
    High: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', label: 'Рекомендую' },
    Medium: { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Рассмотреть' },
    Low: { bg: 'bg-amber-500/20', text: 'text-amber-400', label: 'Сомнительно' },
    Mismatch: { bg: 'bg-red-500/20', text: 'text-red-400', label: 'Не подходит' }
  };
  const c = verdict ? config[verdict] : config.Low;

  return (
    <span className={`px-2.5 py-1 rounded-md text-xs font-medium ${c.bg} ${c.text}`}>
      {c.label}
    </span>
  );
};

// === COVER LETTER INDICATOR ===
const CoverLetterBadge: React.FC<{ hasCoverLetter: boolean }> = ({ hasCoverLetter }) => {
  if (!hasCoverLetter) return null;
  return (
    <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-violet-500/15 text-violet-400 text-[10px]">
      <Mail className="w-3 h-3" />
      Письмо
    </span>
  );
};

// === SALARY DISPLAY ===
const SalaryDisplay: React.FC<{ salary?: number; currency?: string }> = ({ salary, currency = 'RUB' }) => {
  if (!salary) return <span className="text-zinc-600 text-sm">Зарплата не указана</span>;

  const formatted = new Intl.NumberFormat('ru-RU').format(salary);
  return (
    <span className="text-zinc-300 text-sm font-medium tabular-nums">
      {formatted} {currency === 'RUB' ? '₽' : currency}
    </span>
  );
};

// === MUST-HAVES (compact) ===
const MustHavesCompact: React.FC<{ mustHaves: MustHave[] }> = ({ mustHaves }) => {
  if (!mustHaves?.length) return null;

  const yesCount = mustHaves.filter(m => m.status === 'yes').length;
  const noCount = mustHaves.filter(m => m.status === 'no').length;
  const maybeCount = mustHaves.filter(m => m.status === 'maybe').length;

  return (
    <div className="flex items-center gap-3 text-xs">
      {yesCount > 0 && (
        <span className="flex items-center gap-1 text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5" /> {yesCount}
        </span>
      )}
      {maybeCount > 0 && (
        <span className="flex items-center gap-1 text-amber-400">
          <HelpCircle className="w-3.5 h-3.5" /> {maybeCount}
        </span>
      )}
      {noCount > 0 && (
        <span className="flex items-center gap-1 text-red-400">
          <XCircle className="w-3.5 h-3.5" /> {noCount}
        </span>
      )}
    </div>
  );
};

// === INTERVIEW QUESTIONS BLOCK ===
const InterviewQuestionsBlock: React.FC<{ questions?: InterviewQuestion[] }> = ({ questions }) => {
  if (!questions?.length) return null;

  return (
    <div className="space-y-3">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-blue-400">
        Вопросы для интервью
      </div>
      {questions.slice(0, 3).map((q, i) => (
        <div key={i} className="pl-3 border-l-2 border-blue-500/30">
          <div className="text-sm text-zinc-200">{q.question}</div>
          {q.checks && (
            <div className="text-xs text-zinc-500 mt-1">
              <span className="text-blue-400/70">Проверяем:</span> {q.checks}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

// === HELPERS ===
const getVerdict = (r: AnalysisWithApplication): Verdict | undefined => {
  if (r.verdict) return r.verdict;
  if (r.raw_result?.verdict) return r.raw_result.verdict as Verdict;
  return undefined;
};

const getPriority = (r: AnalysisWithApplication): Priority | undefined => {
  if (r.priority) return r.priority;
  if (r.raw_result?.priority) return r.raw_result.priority as Priority;
  return 'basic';
};

const getOneLiner = (r: AnalysisWithApplication): string | undefined => {
  if (r.one_liner) return r.one_liner;
  if (r.raw_result?.one_liner) return r.raw_result.one_liner;
  // Fallback to verdict_reason or reasoning_for_hr
  return r.raw_result?.verdict_reason || r.reasoning_for_hr;
};

const getMustHaves = (r: AnalysisWithApplication): MustHave[] => {
  if (r.must_haves?.length) return r.must_haves;
  if (r.raw_result?.must_haves?.length) return r.raw_result.must_haves;
  return [];
};

const getReasoningForHR = (r: AnalysisWithApplication): string | undefined => {
  if (r.reasoning_for_hr) return r.reasoning_for_hr;
  if (r.raw_result?.reasoning_for_hr) return r.raw_result.reasoning_for_hr;
  return r.reasoning;
};

const getInterviewQuestions = (r: AnalysisWithApplication): InterviewQuestion[] => {
  if (r.interview_questions_v7?.length) return r.interview_questions_v7;
  if (r.raw_result?.interview_questions?.length) {
    const qs = r.raw_result.interview_questions;
    if (qs[0]?.checks !== undefined) return qs;
  }
  return [];
};

const getSalaryFromResume = (r: AnalysisWithApplication): number | undefined => {
  const resumeData = r.application?.resume_data;
  if (!resumeData) return undefined;

  let resume = resumeData;
  if (typeof resume === 'string') {
    try { resume = JSON.parse(resume); } catch { return undefined; }
  }

  const salary = resume?.salary;
  if (!salary) return undefined;

  // salary.amount is usually NET, multiply by 1.15 for GROSS estimate
  const amount = salary.amount || salary.from || 0;
  return amount ? Math.round(amount * 1.15) : undefined;
};

const hasCoverLetter = (r: AnalysisWithApplication): boolean => {
  const resumeData = r.application?.resume_data;
  if (!resumeData) return false;

  let resume = resumeData;
  if (typeof resume === 'string') {
    try { resume = JSON.parse(resume); } catch { return false; }
  }

  const cover = resume?.cover_letter || resume?.message;
  return !!(cover && cover.trim().length > 10);
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
    } else {
      setApplicationsStats(null);
    }
  }, [selectedVacancy]);

  // Polling effect for analysis progress
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
          ? now - pollingDataRef.current.noProgressSince : 0;

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

      // Sort by score (which incorporates verdict + priority)
      data.sort((a: any, b: any) => {
        const scoreA = a.score || a.raw_result?.score || 0;
        const scoreB = b.score || b.raw_result?.score || 0;
        return scoreB - scoreA;
      });

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

  const verdictCounts = results.reduce((acc, r) => {
    const v = getVerdict(r) || 'Low';
    acc[v] = (acc[v] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.25 }
  };

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div {...fadeIn} className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">AI-анализ резюме</h1>
          <p className="text-xs text-zinc-600 mt-0.5">v7.2 Priority</p>
        </div>
        {selectedVacancy !== 'all' && applicationsStats?.analyzed_applications > 0 && (
          <Button
            onClick={handleDownloadExcel}
            disabled={isDownloading}
            variant="outline"
            size="sm"
            className="border-zinc-700 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
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
            className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2"
          >
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            {error}
            <button onClick={() => setError(null)} className="ml-auto hover:text-red-300 text-lg leading-none">&times;</button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filters */}
      <motion.div {...fadeIn} className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
          <SelectTrigger className="h-10 bg-zinc-900 border-zinc-800 text-sm">
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
          <SelectTrigger className="h-10 bg-zinc-900 border-zinc-800 text-sm">
            <SelectValue placeholder="Фильтр" />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-zinc-800">
            <SelectItem value="all">Все</SelectItem>
            <SelectItem value="High">Рекомендую</SelectItem>
            <SelectItem value="Medium">Рассмотреть</SelectItem>
            <SelectItem value="Low">Сомнительно</SelectItem>
            <SelectItem value="Mismatch">Не подходит</SelectItem>
          </SelectContent>
        </Select>
      </motion.div>

      {/* Stats + Analysis Control */}
      {selectedVacancy !== 'all' && applicationsStats && (
        <motion.div {...fadeIn} className="space-y-4">
          {/* Compact Stats */}
          <div className="flex items-center gap-6 p-4 bg-zinc-900/50 rounded-xl border border-zinc-800/50">
            <div>
              <div className="text-2xl font-semibold tabular-nums">{applicationsStats.total_applications}</div>
              <div className="text-[10px] uppercase tracking-wider text-zinc-600">откликов</div>
            </div>
            <div className="w-px h-10 bg-zinc-800" />
            <div>
              <div className="text-2xl font-semibold tabular-nums text-emerald-400">{verdictCounts['High'] || 0}</div>
              <div className="text-[10px] uppercase tracking-wider text-zinc-600">рекомендую</div>
            </div>
            <div>
              <div className="text-2xl font-semibold tabular-nums text-blue-400">{verdictCounts['Medium'] || 0}</div>
              <div className="text-[10px] uppercase tracking-wider text-zinc-600">рассмотреть</div>
            </div>
            <div className="flex-1" />
            {applicationsStats.unanalyzed_applications > 0 && (
              <div className="text-right">
                <div className="text-lg font-medium tabular-nums text-amber-400">{applicationsStats.unanalyzed_applications}</div>
                <div className="text-[10px] uppercase tracking-wider text-zinc-600">не проанализировано</div>
              </div>
            )}
          </div>

          {/* Analysis Control */}
          {!isAnalyzing ? (
            applicationsStats.unanalyzed_applications > 0 && (
              <Button
                onClick={handleAnalyzeNew}
                className="w-full h-12 bg-zinc-100 text-zinc-900 hover:bg-white font-medium"
              >
                <Play className="h-4 w-4 mr-2" />
                Запустить анализ ({applicationsStats.unanalyzed_applications} резюме)
              </Button>
            )
          ) : (
            <div className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800/50">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-zinc-400">
                  Анализ: {analysisProgress.analyzed} / {analysisProgress.total}
                </span>
                <span className="text-xl font-semibold tabular-nums">{progressPercent}%</span>
              </div>
              <div className="h-2 bg-zinc-800 rounded-full overflow-hidden mb-3">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercent}%` }}
                  className="h-full bg-emerald-500 rounded-full"
                />
              </div>
              <div className="flex items-center justify-between text-xs text-zinc-600">
                <span>{getTimeRemaining()}</span>
                <Button
                  onClick={handleStopAnalysis}
                  variant="ghost"
                  size="sm"
                  className="text-zinc-500 hover:text-zinc-300 h-7"
                >
                  <Square className="h-3 w-3 mr-1 fill-current" />
                  Стоп
                </Button>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* No vacancy hint */}
      {selectedVacancy === 'all' && (
        <motion.div {...fadeIn} className="text-center py-16">
          <p className="text-zinc-600">Выберите вакансию для анализа</p>
        </motion.div>
      )}

      {/* Results */}
      {selectedVacancy !== 'all' && (
        <motion.div {...fadeIn} className="space-y-2">
          {isLoading ? (
            <div className="text-center py-12 text-zinc-600">Загрузка...</div>
          ) : results.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-zinc-500">Нет результатов</p>
              <p className="text-xs text-zinc-700 mt-1">Запустите анализ или измените фильтры</p>
            </div>
          ) : (
            results.map((r) => {
              const verdict = getVerdict(r);
              const priority = getPriority(r);
              const oneLiner = getOneLiner(r);
              const mustHaves = getMustHaves(r);
              const reasoning = getReasoningForHR(r);
              const questions = getInterviewQuestions(r);
              const salary = getSalaryFromResume(r);
              const hasCover = hasCoverLetter(r);
              const isExpanded = expandedResults.has(r.id);
              const phone = r.application?.candidate_phone;

              return (
                <div
                  key={r.id}
                  className="bg-zinc-900/50 border border-zinc-800/50 rounded-xl overflow-hidden hover:border-zinc-700/50 transition-colors"
                >
                  {/* Main Row */}
                  <div
                    className="p-4 cursor-pointer"
                    onClick={() => toggleExpanded(r.id)}
                  >
                    {/* Top line: Stars + Name + Badges + Salary */}
                    <div className="flex items-center gap-3 mb-2">
                      <PriorityStars priority={priority} verdict={verdict} />
                      <VerdictBadge verdict={verdict} />

                      <span className="font-medium text-zinc-100 truncate">
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
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      )}

                      <CoverLetterBadge hasCoverLetter={hasCover} />
                      <MustHavesCompact mustHaves={mustHaves} />

                      <div className="flex-1" />

                      <SalaryDisplay salary={salary} />

                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-zinc-600" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-zinc-600" />
                      )}
                    </div>

                    {/* One-liner */}
                    {oneLiner && (
                      <p className="text-sm text-zinc-400 leading-relaxed pl-0 md:pl-[52px]">
                        {oneLiner}
                      </p>
                    )}
                  </div>

                  {/* Expanded Content */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="px-4 pb-4 pt-2 space-y-4 border-t border-zinc-800/50">
                          {/* Reasoning for HR */}
                          {reasoning && (
                            <div className="p-4 bg-zinc-800/30 rounded-lg">
                              <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500 mb-2">
                                Заключение
                              </div>
                              <p className="text-sm text-zinc-300 leading-relaxed">{reasoning}</p>
                            </div>
                          )}

                          {/* Interview Questions */}
                          <InterviewQuestionsBlock questions={questions} />

                          {/* Actions */}
                          <div className="flex items-center gap-3 pt-2">
                            {phone ? (
                              <a
                                href={`tel:${phone}`}
                                className="flex items-center gap-2 px-4 py-2 bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-400 rounded-lg text-sm font-medium transition-colors"
                              >
                                <Phone className="h-4 w-4" />
                                {phone}
                              </a>
                            ) : (
                              <span className="text-xs text-zinc-600">Телефон не указан</span>
                            )}

                            {r.application?.resume_url && (
                              <a
                                href={r.application.resume_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-sm transition-colors"
                              >
                                <ExternalLink className="h-4 w-4" />
                                Резюме на HH
                              </a>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })
          )}
        </motion.div>
      )}

      <LimitExceededModal
        isOpen={limitModalOpen}
        onClose={() => setLimitModalOpen(false)}
        subscriptionInfo={limitExceededInfo}
      />
    </div>
  );
};

export default Analysis;
