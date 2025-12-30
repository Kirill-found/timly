/**
 * Export - Экспорт данных
 * Design: Dark Industrial Brutalism
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download, FileSpreadsheet, CheckCircle, Loader2, XCircle,
  Users, Briefcase, Star, ThumbsUp, Award, AlertTriangle,
  MessageSquare, FileText, User, Mail, Phone, Building
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

const EXPORT_FIELDS = [
  { icon: User, label: 'ФИО кандидата' },
  { icon: Mail, label: 'Email' },
  { icon: Phone, label: 'Телефон' },
  { icon: Star, label: 'Общий балл' },
  { icon: ThumbsUp, label: 'Рекомендация' },
  { icon: Award, label: 'Сильные стороны' },
  { icon: AlertTriangle, label: 'Слабые стороны' },
  { icon: MessageSquare, label: 'Обоснование' },
];

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

      let message = 'Файл успешно скачан!';
      if (recommendation !== 'all' || (minScore && minScore > 0)) {
        const filters = [];
        if (recommendation !== 'all') {
          const rec = RECOMMENDATIONS.find(r => r.id === recommendation);
          filters.push(rec?.label || recommendation);
        }
        if (minScore) filters.push(`${minScore}+ баллов`);
        message += ` Фильтры: ${filters.join(', ')}`;
      }
      setSuccessMessage(message);
    } catch (err: any) {
      console.error('Export error:', err);
      setError(err.response?.data?.error?.message || err.message || 'Ошибка при экспорте');
    } finally {
      setIsExporting(false);
    }
  };

  const selectedVacancyData = vacancies.find(v => v.id === selectedVacancy);
  const totalCandidates = selectedVacancyData?.applications_count || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
              <Download className="h-5 w-5 text-emerald-400" />
            </div>
            Экспорт данных
          </h1>
          <p className="text-zinc-500 text-sm mt-2">Выгрузка результатов анализа в Excel</p>
        </div>
      </motion.div>

      {/* Stats Row */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-3 gap-px bg-zinc-800 rounded-lg overflow-hidden"
      >
        <div className="bg-zinc-900 p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
            <Briefcase className="h-5 w-5 text-zinc-400" />
          </div>
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider">Вакансий</div>
            <div className="text-xl font-semibold text-zinc-100">{vacancies.length}</div>
          </div>
        </div>
        <div className="bg-zinc-900 p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
            <Users className="h-5 w-5 text-zinc-400" />
          </div>
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider">Кандидатов</div>
            <div className="text-xl font-semibold text-zinc-100">{totalCandidates}</div>
          </div>
        </div>
        <div className="bg-zinc-900 p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
            <FileSpreadsheet className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider">Формат</div>
            <div className="text-xl font-semibold text-zinc-100">.xlsx</div>
          </div>
        </div>
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

      {/* Vacancy Selection */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-3">
        <div className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Выберите вакансию</div>
        {vacancies.length === 0 ? (
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-8 text-center">
            <Briefcase className="h-10 w-10 text-zinc-700 mx-auto mb-3" />
            <p className="text-zinc-500 text-sm">Нет доступных вакансий</p>
            <p className="text-zinc-600 text-xs mt-1">Синхронизируйте данные с HH.ru</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {vacancies.map((vacancy, index) => (
              <motion.button
                key={vacancy.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 + index * 0.05 }}
                onClick={() => setSelectedVacancy(vacancy.id)}
                className={`relative p-4 rounded-lg border text-left transition-all duration-200 ${
                  selectedVacancy === vacancy.id
                    ? 'bg-zinc-800 border-emerald-500/50 ring-1 ring-emerald-500/20'
                    : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700 hover:bg-zinc-900'
                }`}
              >
                {selectedVacancy === vacancy.id && (
                  <div className="absolute top-3 right-3"><CheckCircle className="h-4 w-4 text-emerald-400" /></div>
                )}
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${selectedVacancy === vacancy.id ? 'bg-emerald-500/10' : 'bg-zinc-800'}`}>
                    <Building className={`h-4 w-4 ${selectedVacancy === vacancy.id ? 'text-emerald-400' : 'text-zinc-500'}`} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className={`font-medium truncate ${selectedVacancy === vacancy.id ? 'text-zinc-100' : 'text-zinc-300'}`}>{vacancy.title}</div>
                    <div className="flex items-center gap-3 mt-1 text-xs">
                      <span className="text-zinc-500"><Users className="h-3 w-3 inline mr-1" />{vacancy.applications_count} откликов</span>
                      {vacancy.new_applications_count > 0 && <span className="text-emerald-400">+{vacancy.new_applications_count} новых</span>}
                    </div>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        )}
      </motion.div>

      {/* Filters */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          <div className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Минимальный балл</div>
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
          <div className="text-xs text-zinc-500 uppercase tracking-wider font-medium">Рекомендация</div>
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

      {/* Export Preview & Button */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-zinc-900/50 border border-zinc-800 rounded-lg p-5">
          <div className="text-xs text-zinc-500 uppercase tracking-wider font-medium mb-4">Поля в экспорте</div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {EXPORT_FIELDS.map((field, index) => (
              <motion.div key={field.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 + index * 0.05 }} className="flex items-center gap-2 text-sm text-zinc-400">
                <field.icon className="h-4 w-4 text-zinc-600" />
                <span className="truncate">{field.label}</span>
              </motion.div>
            ))}
          </div>
        </div>
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5 flex flex-col justify-center">
          <Button
            onClick={handleExport}
            disabled={!selectedVacancy || isExporting || vacancies.length === 0}
            className="w-full h-12 bg-emerald-500 text-white hover:bg-emerald-400 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            size="lg"
          >
            {isExporting ? (
              <span className="flex items-center gap-2"><Loader2 className="h-5 w-5 animate-spin" />Экспорт...</span>
            ) : (
              <span className="flex items-center gap-2"><Download className="h-5 w-5" />Скачать Excel</span>
            )}
          </Button>
          {selectedVacancyData && (
            <div className="mt-3 text-center">
              <span className="text-xs text-zinc-500">{totalCandidates} {totalCandidates === 1 ? 'кандидат' : totalCandidates < 5 ? 'кандидата' : 'кандидатов'}</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* File Format Info */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="flex items-center justify-center gap-2 text-xs text-zinc-600">
        <FileText className="h-3 w-3" />
        <span>Microsoft Excel (.xlsx) | Совместим с Google Sheets</span>
      </motion.div>
    </div>
  );
};

export default Export;
