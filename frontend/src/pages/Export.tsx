/**
 * Export - Экспорт данных
 * Design: Dark Industrial - консистентно с Dashboard
 */
import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download, CheckCircle, Loader2, XCircle,
  Users, Briefcase, Building
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/services/api';
import { Vacancy } from '@/types';
import { useApp } from '@/store/AppContext';

const RECOMMENDATIONS = [
  { id: 'all', label: 'Все', color: 'zinc' },
  { id: 'hire', label: 'Нанять', color: 'green' },
  { id: 'interview', label: 'Собеседование', color: 'blue' },
  { id: 'maybe', label: 'Возможно', color: 'amber' },
  { id: 'reject', label: 'Отклонить', color: 'red' },
] as const;

const SCORE_THRESHOLDS = [
  { id: 'all', label: 'Все баллы', min: undefined },
  { id: '80', label: '80+', min: 80 },
  { id: '60', label: '60+', min: 60 },
  { id: '40', label: '40+', min: 40 },
] as const;

const Export: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { vacancies: contextVacancies } = useApp();
  const vacancies = Array.isArray(contextVacancies) ? contextVacancies : [];

  const [selectedVacancy, setSelectedVacancy] = useState<string>('');
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [recommendation, setRecommendation] = useState<string>('all');
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    const recommendationParam = searchParams.get('recommendation');
    const minScoreParam = searchParams.get('minScore');
    if (recommendationParam) setRecommendation(recommendationParam);
    if (minScoreParam) setMinScore(parseInt(minScoreParam));
  }, [searchParams]);

  useEffect(() => {
    if (vacancies.length > 0 && !selectedVacancy) {
      setSelectedVacancy(vacancies[0].id);
    }
  }, [vacancies]);

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const selectedVacancyData = vacancies.find(v => v.id === selectedVacancy);
  const totalCandidates = selectedVacancyData?.applications_count || 0;

  // Распределение по рекомендациям (мок, потом подключить реальные данные)
  const distribution = useMemo(() => {
    const total = totalCandidates || 1;
    return {
      hire: Math.round(total * 0.25),
      interview: Math.round(total * 0.30),
      maybe: Math.round(total * 0.20),
      reject: Math.round(total * 0.25),
    };
  }, [totalCandidates]);

  // Подсчёт кандидатов в отчёте с учётом фильтров
  const candidatesInReport = useMemo(() => {
    if (recommendation === 'all') return totalCandidates;
    return distribution[recommendation as keyof typeof distribution] || 0;
  }, [recommendation, totalCandidates, distribution]);

  const handleExport = async () => {
    if (!selectedVacancy) {
      setError('Выберите вакансию для экспорта');
      return;
    }
    setIsExporting(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const blob = await apiClient.downloadExcelReport(selectedVacancy, recommendation, minScore);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      const vacancy = vacancies.find(v => v.id === selectedVacancy);
      const timestamp = new Date().toISOString().split('T')[0];
      let fileName = `timly_export_${vacancy?.title || 'vacancy'}`;
      if (recommendation !== 'all') fileName += `_${recommendation}`;
      if (minScore && minScore > 0) fileName += `_score${minScore}+`;
      fileName += `_${timestamp}.xlsx`;

      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSuccessMessage(`Экспортировано ${candidatesInReport} кандидатов`);
    } catch (err: any) {
      console.error('Export error:', err);
      setError(err.response?.data?.error?.message || err.message || 'Ошибка при экспорте');
    } finally {
      setIsExporting(false);
    }
  };

  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div {...fadeIn}>
        <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight">Экспорт данных</h1>
        <p className="text-zinc-500 text-sm mt-1">Выгрузка результатов анализа в Excel</p>
      </motion.div>

      {/* Alerts */}
      <AnimatePresence>
        {error && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <Alert className="bg-red-500/10 border-red-500/20">
              <XCircle className="h-4 w-4 text-red-400" />
              <AlertDescription className="text-red-400">{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}
        {successMessage && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
            <Alert className="bg-emerald-500/10 border-emerald-500/20">
              <CheckCircle className="h-4 w-4 text-emerald-400" />
              <AlertDescription className="text-emerald-400">{successMessage}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats Row - Распределение по рекомендациям */}
      <motion.div {...fadeIn} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-px bg-zinc-800 border border-zinc-800 rounded-lg overflow-hidden">
        <div className="bg-card p-5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">Нанять</div>
          <div className="text-3xl font-semibold tracking-tight text-emerald-400">{distribution.hire}</div>
          <div className="text-xs text-zinc-500">кандидатов</div>
        </div>
        <div className="bg-card p-5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">Собеседование</div>
          <div className="text-3xl font-semibold tracking-tight text-blue-400">{distribution.interview}</div>
          <div className="text-xs text-zinc-500">кандидатов</div>
        </div>
        <div className="bg-card p-5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">Возможно</div>
          <div className="text-3xl font-semibold tracking-tight text-amber-400">{distribution.maybe}</div>
          <div className="text-xs text-zinc-500">кандидатов</div>
        </div>
        <div className="bg-card p-5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">Отклонить</div>
          <div className="text-3xl font-semibold tracking-tight text-red-400">{distribution.reject}</div>
          <div className="text-xs text-zinc-500">кандидатов</div>
        </div>
      </motion.div>

      {/* Vacancy Selection */}
      <motion.div {...fadeIn} className="space-y-3">
        <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">Выберите вакансию</div>
        {vacancies.length === 0 ? (
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-8 text-center">
            <Briefcase className="h-10 w-10 text-zinc-700 mx-auto mb-3" />
            <p className="text-zinc-500 text-sm">Нет доступных вакансий</p>
            <p className="text-zinc-600 text-xs mt-1">Синхронизируйте данные с HH.ru</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {vacancies.map((vacancy) => (
              <button
                key={vacancy.id}
                onClick={() => setSelectedVacancy(vacancy.id)}
                className={`relative p-4 rounded-lg border text-left transition-all duration-200 ${
                  selectedVacancy === vacancy.id
                    ? 'bg-zinc-800 border-zinc-600'
                    : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700 hover:bg-zinc-900'
                }`}
              >
                {selectedVacancy === vacancy.id && (
                  <div className="absolute top-3 right-3"><CheckCircle className="h-4 w-4 text-zinc-400" /></div>
                )}
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${selectedVacancy === vacancy.id ? 'bg-zinc-700' : 'bg-zinc-800'}`}>
                    <Building className="h-4 w-4 text-zinc-500" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className={`font-medium truncate ${selectedVacancy === vacancy.id ? 'text-zinc-100' : 'text-zinc-300'}`}>{vacancy.title}</div>
                    <div className="flex items-center gap-3 mt-1 text-xs">
                      <span className="text-zinc-500"><Users className="h-3 w-3 inline mr-1" />{vacancy.applications_count} откликов</span>
                      {vacancy.new_applications_count > 0 && <span className="text-emerald-400">+{vacancy.new_applications_count} новых</span>}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </motion.div>

      {/* Filters */}
      <motion.div {...fadeIn} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">Минимальный балл</div>
          <div className="flex gap-2 flex-wrap">
            {SCORE_THRESHOLDS.map((threshold) => (
              <button
                key={threshold.id}
                onClick={() => setMinScore(threshold.min)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  (minScore === threshold.min || (threshold.min === undefined && minScore === undefined))
                    ? 'bg-zinc-100 text-zinc-900'
                    : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700'
                }`}
              >{threshold.label}</button>
            ))}
          </div>
        </div>
        <div className="space-y-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">Рекомендация</div>
          <div className="flex gap-2 flex-wrap">
            {RECOMMENDATIONS.map((rec) => {
              const isActive = recommendation === rec.id;
              const colorClasses: Record<string, string> = {
                zinc: isActive ? 'bg-zinc-100 text-zinc-900' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200',
                green: isActive ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-emerald-400 hover:border-emerald-500/30',
                blue: isActive ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-blue-400 hover:border-blue-500/30',
                amber: isActive ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-amber-400 hover:border-amber-500/30',
                red: isActive ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-red-400 hover:border-red-500/30',
              };
              return (
                <button key={rec.id} onClick={() => setRecommendation(rec.id)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 border ${colorClasses[rec.color]}`}>{rec.label}</button>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Export Button */}
      <motion.div {...fadeIn} className="flex items-center gap-4">
        <Button
          onClick={handleExport}
          disabled={!selectedVacancy || isExporting || vacancies.length === 0}
          className="h-12 px-8 bg-zinc-100 text-zinc-900 hover:bg-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          size="lg"
        >
          {isExporting ? (
            <span className="flex items-center gap-2"><Loader2 className="h-5 w-5 animate-spin" />Экспорт...</span>
          ) : (
            <span className="flex items-center gap-2"><Download className="h-5 w-5" />Скачать Excel</span>
          )}
        </Button>
        {selectedVacancyData && (
          <div className="text-sm text-zinc-500">
            В отчёте: <span className="text-zinc-100 font-medium">{candidatesInReport}</span> кандидатов
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Export;
