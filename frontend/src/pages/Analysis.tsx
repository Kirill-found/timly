/**
 * Страница анализа резюме
 * Таблица с результатами AI анализа откликов
 */
import React, { useState, useEffect } from 'react';
import { Brain, Filter, Download, Search, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, XCircle, Clock, Loader2, StopCircle, ExternalLink, Phone } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/services/api';
import { Vacancy, AnalysisResult, AnalysisFilter } from '@/types';
import { useApp } from '@/store/AppContext';
import { AnalysisLimitsDisplay } from '@/components/AnalysisLimitsDisplay';

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

  // Новые состояния для инкрементального анализа
  const [applicationsStats, setApplicationsStats] = useState<any>(null);
  const [dashboardStats, setDashboardStats] = useState<any>(null); // Статистика для дашборда (не зависит от фильтров)
  const [isDownloading, setIsDownloading] = useState(false);

  // Используем глобальное состояние анализа
  const isAnalyzing = app.activeAnalysis !== null && app.activeAnalysis.vacancyId === selectedVacancy;
  const analysisProgress = app.activeAnalysis || { total: 0, analyzed: 0, startTime: 0, vacancyId: '' };

  // Состояние для слайдера квоты анализа
  const [analysisLimit, setAnalysisLimit] = useState<number>(100); // % от новых откликов

  // Загрузка вакансий при монтировании
  useEffect(() => {
    loadVacancies();
  }, []);

  // Загрузка результатов при изменении фильтров
  useEffect(() => {
    loadResults();
  }, [selectedVacancy, recommendationFilter]);


  // Загрузка статистики для выбранной вакансии (независимо от фильтров)
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
      if (data && Array.isArray(data)) {
        setVacancies(data);
      } else {
        setVacancies([]);
      }
    } catch (err: any) {
      console.error('Error loading vacancies:', err);
      setVacancies([]);
    }
  };

  const loadResults = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const filters: AnalysisFilter = {
        limit: 100,
      };

      if (selectedVacancy !== 'all') {
        filters.vacancy_id = selectedVacancy;
      }

      if (recommendationFilter !== 'all') {
        filters.recommendation = recommendationFilter as any;
      }

      const data = await apiClient.getAnalysisResults(filters);
      if (data && Array.isArray(data)) {
        setResults(data);
      } else {
        setResults([]);
      }
    } catch (err: any) {
      console.error('Error loading analysis results:', err);
      setError(err.response?.data?.error?.message || 'Ошибка при загрузке результатов анализа');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadApplicationsStats = async () => {
    try {
      if (selectedVacancy === 'all') {
        setApplicationsStats(null);
        return;
      }

      const stats = await apiClient.getApplicationsStats(selectedVacancy);
      setApplicationsStats(stats);
    } catch (err: any) {
      console.error('Error loading applications stats:', err);
      setApplicationsStats(null);
    }
  };

  const loadDashboardStats = async () => {
    try {
      if (selectedVacancy === 'all') {
        setDashboardStats(null);
        return;
      }

      const stats = await apiClient.getVacancyAnalysisStats(selectedVacancy);
      setDashboardStats(stats);
    } catch (err: any) {
      console.error('Error loading dashboard stats:', err);
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
      setError('Выберите конкретную вакансию для анализа');
      return;
    }

    setError(null);

    const initialUnanalyzed = applicationsStats?.unanalyzed_applications || 0;
    const initialAnalyzed = applicationsStats?.analyzed_applications || 0;
    const applicationsToAnalyze = Math.ceil((initialUnanalyzed * analysisLimit) / 100);

    app.startAnalysis({
      vacancyId: selectedVacancy,
      total: applicationsToAnalyze,
      analyzed: 0,
      startTime: Date.now()
    });

    try {
      await apiClient.startAnalysisNewApplications(selectedVacancy, undefined, applicationsToAnalyze);

      // Используем глобальный polling из AppContext
      const pollStats = async () => {
        try {
          await loadApplicationsStats();
          const stats = await apiClient.getApplicationsStats(selectedVacancy);
          const newlyAnalyzed = stats.analyzed_applications - initialAnalyzed;

          app.updateAnalysisProgress({
            analyzed: newlyAnalyzed
          });

          if (stats.unanalyzed_applications === 0 || newlyAnalyzed >= applicationsToAnalyze) {
            handleStopAnalysis();
          }
        } catch (err) {
          console.error('Error polling stats:', err);
        }
      };

      // Запускаем глобальный polling (интервал 3 сек, таймаут 5 мин)
      app.startGlobalPolling(pollStats, 3000, 300000);

    } catch (err: any) {
      console.error('Error starting analysis:', err);
      setError(err.response?.data?.error?.message || 'Ошибка при запуске анализа');
      app.stopAnalysis();
    }
  };

  const handleDownloadExcel = async () => {
    if (selectedVacancy === 'all') {
      setError('Выберите конкретную вакансию для экспорта');
      return;
    }

    setIsDownloading(true);
    setError(null);

    try {
      // Передаем текущий фильтр recommendation если он установлен
      const filterToApply = recommendationFilter !== 'all' ? recommendationFilter : undefined;
      const blob = await apiClient.downloadExcelReport(selectedVacancy, filterToApply);

      // Создаем ссылку для скачивания
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const filterSuffix = filterToApply ? `_${filterToApply}` : '';
      a.download = `analysis_report_${selectedVacancy}${filterSuffix}_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      console.error('Error downloading Excel:', err);
      setError(err.response?.data?.error?.message || 'Ошибка при скачивании отчета');
    } finally {
      setIsDownloading(false);
    }
  };

  const getRecommendationBadge = (recommendation?: string) => {
    switch (recommendation) {
      case 'hire':
        return <Badge className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" /> Нанять</Badge>;
      case 'interview':
        return <Badge className="bg-blue-500"><Clock className="h-3 w-3 mr-1" /> Собеседование</Badge>;
      case 'maybe':
        return <Badge variant="secondary"><AlertTriangle className="h-3 w-3 mr-1" /> Возможно</Badge>;
      case 'reject':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" /> Отклонить</Badge>;
      default:
        return <Badge variant="outline">Нет рекомендации</Badge>;
    }
  };

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-blue-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreIcon = (score?: number) => {
    if (!score) return null;
    if (score >= 60) return <TrendingUp className="h-4 w-4" />;
    return <TrendingDown className="h-4 w-4" />;
  };

  const filteredResults = results;

  // Статистика для дашборда (не зависит от фильтров)
  const statsData = dashboardStats ? {
    total: dashboardStats.total_analyzed,
    hire: dashboardStats.hire_count,
    interview: dashboardStats.interview_count,
    maybe: dashboardStats.maybe_count,
    reject: dashboardStats.reject_count,
    avgScore: dashboardStats.avg_score ? Math.round(dashboardStats.avg_score) : 0,
  } : {
    total: 0,
    hire: 0,
    interview: 0,
    maybe: 0,
    reject: 0,
    avgScore: 0,
  };

  return (
    <div className="p-6 space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Анализ резюме</h1>
        <p className="text-muted-foreground">
          Результаты AI анализа откликов кандидатов
        </p>
      </div>

      {/* Ошибки */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Отображение оставшихся анализов согласно тарифному плану */}
      <AnalysisLimitsDisplay />

      {/* Главная карточка анализа - для выбранной вакансии */}
      {selectedVacancy !== 'all' && applicationsStats && (
        <Card className="border-green-300 bg-gradient-to-br from-green-50 to-blue-50 shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-3">
              <Brain className="h-7 w-7 text-green-600" />
              AI Анализ Резюме
            </CardTitle>
            <CardDescription className="text-base">
              {applicationsStats.unanalyzed_applications > 0
                ? `У вас ${applicationsStats.unanalyzed_applications} новых резюме для анализа`
                : 'Все резюме проанализированы'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Статистика в одной строке */}
              <div className="flex items-center justify-around bg-white rounded-xl p-6 shadow-sm">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {applicationsStats.total_applications}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">Всего резюме</div>
                </div>
                <div className="h-12 w-px bg-gray-200"></div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {applicationsStats.analyzed_applications}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">Проанализировано</div>
                </div>
                <div className="h-12 w-px bg-gray-200"></div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">
                    {applicationsStats.unanalyzed_applications}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">Новых</div>
                </div>
              </div>

              {/* Слайдер выбора количества откликов для анализа */}
              {applicationsStats.unanalyzed_applications > 0 && !isAnalyzing && (
                <div className="bg-white rounded-xl p-6 shadow-sm space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold text-gray-900">Выберите количество откликов для анализа</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Будет проанализировано: {Math.ceil((applicationsStats.unanalyzed_applications * analysisLimit) / 100)} из {applicationsStats.unanalyzed_applications} новых откликов
                      </p>
                    </div>
                    <div className="text-3xl font-bold text-blue-600">
                      {analysisLimit}%
                    </div>
                  </div>

                  {/* HTML Range Input Slider */}
                  <div className="space-y-3">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="5"
                      value={analysisLimit}
                      onChange={(e) => setAnalysisLimit(Number(e.target.value))}
                      className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                      style={{
                        background: `linear-gradient(to right, rgb(37 99 235) 0%, rgb(37 99 235) ${analysisLimit}%, rgb(229 231 235) ${analysisLimit}%, rgb(229 231 235) 100%)`
                      }}
                    />

                    {/* Быстрые кнопки выбора процентов */}
                    <div className="flex gap-2 justify-center">
                      {[25, 50, 75, 100].map((percent) => (
                        <button
                          key={percent}
                          onClick={() => setAnalysisLimit(percent)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            analysisLimit === percent
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {percent}%
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Главная кнопка анализа */}
              <div className="space-y-3">
                <Button
                  onClick={handleAnalyzeNew}
                  disabled={isAnalyzing || applicationsStats.unanalyzed_applications === 0}
                  className="w-full h-16 text-lg bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 shadow-lg transition-all"
                  size="lg"
                >
                  {isAnalyzing ? (
                    <Loader2 className="h-6 w-6 mr-3 animate-spin" />
                  ) : (
                    <Brain className="h-6 w-6 mr-3" />
                  )}
                  {isAnalyzing
                    ? 'Анализирую резюме...'
                    : applicationsStats.unanalyzed_applications > 0
                      ? `Проанализировать ${Math.ceil((applicationsStats.unanalyzed_applications * analysisLimit) / 100)} ${analysisLimit < 100 ? `из ${applicationsStats.unanalyzed_applications}` : ''} новых резюме`
                      : 'Все резюме проанализированы'}
                </Button>

                {/* Прогресс-бар анализа */}
                {isAnalyzing && analysisProgress.total > 0 && (
                  <div className="bg-white rounded-lg p-4 space-y-3 border-2 border-blue-200 shadow-sm">
                    <div className="flex justify-between items-center text-sm">
                      <span className="font-medium text-gray-700">
                        Проанализировано: {analysisProgress.analyzed} из {analysisProgress.total}
                      </span>
                      <span className="text-blue-600 font-semibold">
                        {analysisProgress.total > 0
                          ? Math.round((analysisProgress.analyzed / analysisProgress.total) * 100)
                          : 0}%
                      </span>
                    </div>
                    <Progress
                      value={analysisProgress.total > 0
                        ? (analysisProgress.analyzed / analysisProgress.total) * 100
                        : 0
                      }
                      className="h-3"
                    />
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>
                        Осталось: {analysisProgress.total - analysisProgress.analyzed} резюме
                      </span>
                      <span>
                        {(() => {
                          if (analysisProgress.analyzed === 0) {
                            return 'Подсчет времени...';
                          }

                          const elapsed = Date.now() - analysisProgress.startTime;
                          const avgTimePerResume = elapsed / analysisProgress.analyzed;
                          const remainingCount = analysisProgress.total - analysisProgress.analyzed;
                          const remainingMs = remainingCount * avgTimePerResume;

                          const minutes = Math.floor(remainingMs / 60000);
                          const seconds = Math.floor((remainingMs % 60000) / 1000);

                          return minutes > 0
                            ? `≈ ${minutes} мин ${seconds} сек`
                            : `≈ ${seconds} сек`;
                        })()}
                      </span>
                    </div>

                    {/* Кнопка остановки анализа */}
                    <Button
                      onClick={handleStopAnalysis}
                      variant="destructive"
                      size="sm"
                      className="w-full mt-2"
                    >
                      <StopCircle className="h-4 w-4 mr-2" />
                      Остановить анализ
                    </Button>
                  </div>
                )}

                {applicationsStats.analyzed_applications > 0 && (
                  <Button
                    onClick={handleDownloadExcel}
                    disabled={isDownloading}
                    variant="outline"
                    className="w-full h-12"
                    size="lg"
                  >
                    <Download className="h-5 w-5 mr-2" />
                    {isDownloading
                      ? 'Готовлю отчет...'
                      : `Скачать Excel отчет (${applicationsStats.analyzed_applications} резюме)`}
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Подсказка если не выбрана вакансия */}
      {selectedVacancy === 'all' && (
        <Alert className="bg-blue-50 border-blue-200">
          <Brain className="h-4 w-4 text-blue-600" />
          <AlertDescription>
            <span className="font-medium">Выберите конкретную вакансию</span> в фильтре ниже, чтобы начать анализ резюме
          </AlertDescription>
        </Alert>
      )}

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Всего</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statsData.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Средний балл</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getScoreColor(statsData.avgScore)}`}>
              {statsData.avgScore}
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-200 bg-green-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-green-700">Нанять</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{statsData.hire}</div>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-blue-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-blue-700">Собеседование</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{statsData.interview}</div>
          </CardContent>
        </Card>

        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-yellow-700">Возможно</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{statsData.maybe}</div>
          </CardContent>
        </Card>

        <Card className="border-red-200 bg-red-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-red-700">Отклонить</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{statsData.reject}</div>
          </CardContent>
        </Card>
      </div>

      {/* Фильтры */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Фильтры
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Вакансия */}
            <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
              <SelectTrigger>
                <SelectValue placeholder="Выберите вакансию" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все вакансии</SelectItem>
                {vacancies.map(vacancy => (
                  <SelectItem key={vacancy.id} value={vacancy.id}>
                    {vacancy.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Рекомендация */}
            <Select value={recommendationFilter} onValueChange={setRecommendationFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Все рекомендации" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все рекомендации</SelectItem>
                <SelectItem value="hire">Нанять</SelectItem>
                <SelectItem value="interview">Собеседование</SelectItem>
                <SelectItem value="maybe">Возможно</SelectItem>
                <SelectItem value="reject">Отклонить</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Таблица результатов */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Результаты анализа</CardTitle>
            <CardDescription>
              Найдено: {filteredResults.length} {filteredResults.length === 1 ? 'результат' : 'результатов'}
            </CardDescription>
          </div>
          {filteredResults.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownloadExcel}
              disabled={isDownloading || selectedVacancy === 'all'}
            >
              <Download className="h-4 w-4 mr-2" />
              {isDownloading ? 'Готовлю отчет...' : 'Экспорт в Excel'}
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">
              Загрузка результатов...
            </div>
          ) : filteredResults.length === 0 ? (
            <div className="text-center py-12">
              <Brain className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">Результаты анализа отсутствуют</h3>
              <p className="text-muted-foreground mb-4">
                Запустите синхронизацию и анализ откликов
              </p>
              <Button asChild>
                <a href="/sync">Перейти к синхронизации</a>
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredResults.map((result) => (
                <div
                  key={result.id}
                  className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
                >
                  {/* Шапка карточки */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-lg">
                          {result.application?.candidate_name || 'Кандидат без имени'}
                        </h3>
                        {result.application?.resume_url && (
                          <a
                            href={result.application.resume_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 transition-colors"
                            title="Открыть резюме на HH.ru"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                      <div className="flex flex-col gap-1 text-sm text-muted-foreground">
                        {result.application?.candidate_email && (
                          <p>{result.application.candidate_email}</p>
                        )}
                        {result.application?.candidate_phone && (
                          <p className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            {result.application.candidate_phone}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className={`flex items-center gap-1 ${getScoreColor(result.score)}`}>
                        {getScoreIcon(result.score)}
                        <span className="text-2xl font-bold">{result.score || '—'}</span>
                      </div>
                      {getRecommendationBadge(result.recommendation)}
                    </div>
                  </div>

                  {/* Метрики */}
                  <div className="grid grid-cols-3 gap-4 mb-3">
                    <div>
                      <div className="text-xs text-muted-foreground">Навыки</div>
                      <div className="text-sm font-medium">{result.skills_match || 0}%</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Опыт</div>
                      <div className="text-sm font-medium">{result.experience_match || 0}%</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Зарплата</div>
                      <div className="text-sm font-medium">
                        {result.salary_match === 'match' && 'Совпадает'}
                        {result.salary_match === 'higher' && 'Выше'}
                        {result.salary_match === 'lower' && 'Ниже'}
                        {!result.salary_match && 'Не указана'}
                      </div>
                    </div>
                  </div>

                  {/* Сильные стороны */}
                  {result.strengths && result.strengths.length > 0 && (
                    <div className="mb-3">
                      <div className="text-xs font-medium text-green-600 mb-1">Сильные стороны:</div>
                      <div className="flex flex-wrap gap-1">
                        {result.strengths.map((strength, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs border-green-200 text-green-700">
                            {strength}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Слабые стороны */}
                  {result.weaknesses && result.weaknesses.length > 0 && (
                    <div className="mb-3">
                      <div className="text-xs font-medium text-yellow-600 mb-1">Слабые стороны:</div>
                      <div className="flex flex-wrap gap-1">
                        {result.weaknesses.map((weakness, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs border-yellow-200 text-yellow-700">
                            {weakness}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Тревожные сигналы */}
                  {result.red_flags && result.red_flags.length > 0 && (
                    <div className="mb-3">
                      <div className="text-xs font-medium text-red-600 mb-1 flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3" />
                        Тревожные сигналы:
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {result.red_flags.map((flag, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs border-red-200 text-red-700">
                            {flag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Обоснование */}
                  {result.reasoning && (
                    <div className="text-sm text-muted-foreground bg-muted p-3 rounded">
                      {result.reasoning}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Analysis;
