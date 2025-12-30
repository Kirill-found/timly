/**
 * Страница экспорта данных
 * Экспорт результатов анализа в Excel
 * Design: Dark Industrial
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Download, FileSpreadsheet, Filter, CheckCircle, Loader2, XCircle } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiClient } from '@/services/api';
import { Vacancy, ExportRequest } from '@/types';
import { useApp } from '@/store/AppContext';

const Export: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { vacancies: contextVacancies } = useApp();
  const vacancies = Array.isArray(contextVacancies) ? contextVacancies : [];
  const [selectedVacancy, setSelectedVacancy] = useState<string>('');
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [recommendation, setRecommendation] = useState<string>('all');
  const [includeResumeData, setIncludeResumeData] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Инициализация из URL параметров
  useEffect(() => {
    const recommendationParam = searchParams.get('recommendation');
    const minScoreParam = searchParams.get('minScore');

    if (recommendationParam) {
      setRecommendation(recommendationParam);
    }

    if (minScoreParam) {
      setMinScore(parseInt(minScoreParam));
    }
  }, [searchParams]);

  useEffect(() => {
    // Автоматически выбираем первую вакансию если она есть
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
      // Передаём фильтры в backend для применения при экспорте
      const blob = await apiClient.downloadExcelReport(
        selectedVacancy,
        recommendation,
        minScore
      );

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      const vacancy = vacancies.find(v => v.id === selectedVacancy);
      const timestamp = new Date().toISOString().split('T')[0];

      // Добавляем информацию о фильтрах в имя файла
      let fileName = `timly_export_${vacancy?.title || 'vacancy'}`;
      if (recommendation !== 'all') {
        fileName += `_${recommendation}`;
      }
      if (minScore && minScore > 0) {
        fileName += `_score${minScore}+`;
      }
      fileName += `_${timestamp}.xlsx`;

      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      // Формируем сообщение с информацией о применённых фильтрах
      let message = 'Экспорт успешно завершен!';
      if (recommendation !== 'all' || (minScore && minScore > 0)) {
        message += ' Применены фильтры: ';
        const filters = [];
        if (recommendation !== 'all') {
          const recText = {
            hire: 'Нанять',
            interview: 'Собеседование',
            maybe: 'Возможно',
            reject: 'Отклонить'
          }[recommendation] || recommendation;
          filters.push(`Рекомендация "${recText}"`);
        }
        if (minScore && minScore > 0) {
          filters.push(`Минимальный балл ${minScore}`);
        }
        message += filters.join(', ') + '.';
      }
      setSuccessMessage(message);
    } catch (err: any) {
      console.error('Export error:', err);
      setError(err.response?.data?.error?.message || err.message || 'Ошибка при экспорте данных');
    } finally {
      setIsExporting(false);
    }
  };

  const selectedVacancyData = vacancies.find(v => v.id === selectedVacancy);

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
            <Download className="h-5 w-5 text-green-400" />
          </div>
          Экспорт данных
        </h1>
        <p className="text-zinc-500 text-sm mt-2">
          Экспорт результатов анализа резюме в Excel
        </p>
      </div>

      {/* Ошибки */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Alert className="bg-red-500/10 border-red-500/20">
            <XCircle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-400">{error}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Успех */}
      {successMessage && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Alert className="bg-green-500/10 border-green-500/20">
            <CheckCircle className="h-4 w-4 text-green-400" />
            <AlertDescription className="text-green-400">{successMessage}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Настройки экспорта */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader className="border-b border-zinc-800">
            <CardTitle className="flex items-center gap-2 text-zinc-100">
              <Filter className="h-5 w-5 text-zinc-400" />
              Параметры экспорта
            </CardTitle>
            <p className="text-sm text-zinc-500">
              Настройте фильтры для экспорта результатов анализа
            </p>
          </CardHeader>
          <CardContent className="pt-6 space-y-5">
            {/* Выбор вакансии */}
            <div className="space-y-2">
              <Label className="text-zinc-300">Вакансия</Label>
              <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
                <SelectTrigger className="bg-zinc-800/50 border-zinc-700 text-zinc-100">
                  <SelectValue placeholder="Выберите вакансию" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-800">
                  {vacancies.length === 0 ? (
                    <SelectItem value="none" disabled>Вакансии не найдены</SelectItem>
                  ) : (
                    vacancies.map(vacancy => (
                      <SelectItem key={vacancy.id} value={vacancy.id}>
                        {vacancy.title} ({vacancy.applications_count} откликов)
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              {selectedVacancyData && (
                <p className="text-sm text-zinc-600">
                  Откликов: {selectedVacancyData.applications_count} •
                  Новых: {selectedVacancyData.new_applications_count}
                </p>
              )}
            </div>

            {/* Минимальный балл */}
            <div className="space-y-2">
              <Label className="text-zinc-300">Минимальный балл</Label>
              <Select
                value={minScore?.toString() || 'all'}
                onValueChange={(value) => setMinScore(value === 'all' ? undefined : parseInt(value))}
              >
                <SelectTrigger className="bg-zinc-800/50 border-zinc-700 text-zinc-100">
                  <SelectValue placeholder="Любой балл" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-800">
                  <SelectItem value="all">Любой балл</SelectItem>
                  <SelectItem value="80">80+ (отличные кандидаты)</SelectItem>
                  <SelectItem value="60">60+ (хорошие кандидаты)</SelectItem>
                  <SelectItem value="40">40+ (приемлемые кандидаты)</SelectItem>
                  <SelectItem value="20">20+ (все кандидаты)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Рекомендация */}
            <div className="space-y-2">
              <Label className="text-zinc-300">Рекомендация</Label>
              <Select value={recommendation} onValueChange={setRecommendation}>
                <SelectTrigger className="bg-zinc-800/50 border-zinc-700 text-zinc-100">
                  <SelectValue placeholder="Все рекомендации" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-800">
                  <SelectItem value="all">Все</SelectItem>
                  <SelectItem value="hire">Только "Нанять"</SelectItem>
                  <SelectItem value="interview">Только "Собеседование"</SelectItem>
                  <SelectItem value="maybe">Только "Возможно"</SelectItem>
                  <SelectItem value="reject">Только "Отклонить"</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Включить данные резюме */}
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="include-resume"
                checked={includeResumeData}
                onChange={(e) => setIncludeResumeData(e.target.checked)}
                className="h-4 w-4 rounded border-zinc-600 bg-zinc-800 text-zinc-100 focus:ring-zinc-500 focus:ring-offset-zinc-900"
              />
              <Label htmlFor="include-resume" className="text-sm font-normal text-zinc-400 cursor-pointer">
                Включить полные данные резюме (навыки, опыт, образование)
              </Label>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Информация об экспорте */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader className="border-b border-zinc-800">
            <CardTitle className="flex items-center gap-2 text-zinc-100">
              <FileSpreadsheet className="h-5 w-5 text-zinc-400" />
              Формат экспорта
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-3">
              <p className="text-sm text-zinc-400">
                Файл Excel будет содержать следующие данные:
              </p>
              <ul className="text-sm space-y-2 text-zinc-500">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                  Имя кандидата и контактная информация
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                  Общий балл и рекомендация AI
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                  Соответствие навыков и опыта
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                  Сильные и слабые стороны
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                  Тревожные сигналы (при наличии)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                  Обоснование рекомендации
                </li>
                {includeResumeData && (
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                    Полные данные резюме (навыки, опыт, образование)
                  </li>
                )}
              </ul>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Кнопка экспорта */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardContent className="pt-6">
            <Button
              onClick={handleExport}
              disabled={!selectedVacancy || isExporting || vacancies.length === 0}
              className="w-full sm:w-auto bg-zinc-100 text-zinc-900 hover:bg-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              size="lg"
            >
              {isExporting ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Экспорт в процессе...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-5 w-5" />
                  Скачать Excel файл
                </>
              )}
            </Button>

            {vacancies.length === 0 && (
              <p className="text-sm text-zinc-600 mt-3">
                Нет доступных вакансий для экспорта. Сначала синхронизируйте данные с HH.ru
              </p>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Export;
