/**
 * Страница результатов анализа
 * Просмотр и фильтрация проанализированных кандидатов
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Users, Trophy, Filter, ExternalLink, Download, ArrowUpDown } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { apiClient } from '@/services/api';
import { useApp } from '@/store/AppContext';
import { AnalysisResult } from '@/types';

const Results: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { vacancies: contextVacancies } = useApp();
  const vacancies = Array.isArray(contextVacancies) ? contextVacancies : [];

  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedVacancy, setSelectedVacancy] = useState<string>('');
  const [recommendationFilter, setRecommendationFilter] = useState<string>('all');
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [sortBy, setSortBy] = useState<'score' | 'date'>('score');

  // Инициализация фильтров из URL
  useEffect(() => {
    const recommendation = searchParams.get('recommendation');
    const minScoreParam = searchParams.get('minScore');
    const vacancyParam = searchParams.get('vacancy');

    if (recommendation) {
      setRecommendationFilter(recommendation);
    }

    if (minScoreParam) {
      setMinScore(parseInt(minScoreParam));
    }

    if (vacancyParam) {
      setSelectedVacancy(vacancyParam);
    }
  }, [searchParams]);

  // Автоматический выбор первой вакансии
  useEffect(() => {
    if (vacancies.length > 0 && !selectedVacancy) {
      setSelectedVacancy(vacancies[0].id);
    }
  }, [vacancies, selectedVacancy]);

  // Загрузка результатов
  useEffect(() => {
    loadResults();
  }, [selectedVacancy, recommendationFilter, minScore]);

  const loadResults = async () => {
    if (!selectedVacancy) {
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const filters: any = {
        vacancy_id: selectedVacancy,
      };

      if (recommendationFilter !== 'all') {
        filters.recommendation = recommendationFilter;
      }

      if (minScore && minScore > 0) {
        filters.min_score = minScore;
      }

      const data = await apiClient.getAnalysisResults(filters);
      setResults(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error loading results:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationVariant = (recommendation: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (recommendation) {
      case 'hire': return 'default';
      case 'interview': return 'secondary';
      case 'reject': return 'destructive';
      default: return 'outline';
    }
  };

  const getRecommendationText = (recommendation: string) => {
    switch (recommendation) {
      case 'hire': return 'Нанять';
      case 'interview': return 'Собеседование';
      case 'maybe': return 'Возможно';
      case 'reject': return 'Отклонить';
      default: return recommendation;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  const sortedResults = [...results].sort((a, b) => {
    if (sortBy === 'score') {
      return (b.score || 0) - (a.score || 0);
    } else {
      const aDate = a.analyzed_at ? new Date(a.analyzed_at).getTime() : 0;
      const bDate = b.analyzed_at ? new Date(b.analyzed_at).getTime() : 0;
      return bDate - aDate;
    }
  });

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-12 w-full" />
        <div className="grid gap-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Результаты анализа</h1>
        <p className="text-muted-foreground">
          Просмотр и фильтрация проанализированных кандидатов
        </p>
      </div>

      {/* Фильтры */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Фильтры
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Выбор вакансии */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Вакансия</label>
              <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите вакансию" />
                </SelectTrigger>
                <SelectContent>
                  {vacancies.map((vacancy) => (
                    <SelectItem key={vacancy.id} value={vacancy.id}>
                      {vacancy.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Рекомендация */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Рекомендация</label>
              <Select value={recommendationFilter} onValueChange={setRecommendationFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все</SelectItem>
                  <SelectItem value="hire">Нанять</SelectItem>
                  <SelectItem value="interview">Собеседование</SelectItem>
                  <SelectItem value="maybe">Возможно</SelectItem>
                  <SelectItem value="reject">Отклонить</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Минимальный балл */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Минимальный балл</label>
              <Select
                value={minScore?.toString() || '0'}
                onValueChange={(val) => setMinScore(parseInt(val) || undefined)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">Любой</SelectItem>
                  <SelectItem value="60">60+</SelectItem>
                  <SelectItem value="70">70+</SelectItem>
                  <SelectItem value="80">80+</SelectItem>
                  <SelectItem value="90">90+</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Сортировка */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Сортировка</label>
              <Select value={sortBy} onValueChange={(val) => setSortBy(val as 'score' | 'date')}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="score">По баллу</SelectItem>
                  <SelectItem value="date">По дате</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Статистика */}
          <div className="flex items-center gap-4 pt-2 border-t">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Найдено: <strong>{sortedResults.length}</strong></span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setRecommendationFilter('all');
                setMinScore(undefined);
              }}
            >
              Сбросить фильтры
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Результаты */}
      {sortedResults.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Users className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-4">Результаты не найдены</p>
            <p className="text-sm text-muted-foreground mb-4">
              Попробуйте изменить фильтры или запустить анализ
            </p>
            <Button asChild variant="outline">
              <Link to="/analysis">Запустить анализ</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {sortedResults.map((result) => (
            <Card key={result.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  {/* Информация о кандидате */}
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold">
                        {result.application?.candidate_name || result.candidate_name || 'Без имени'}
                      </h3>
                      <Badge variant={getRecommendationVariant(result.recommendation || '')}>
                        {getRecommendationText(result.recommendation || '')}
                      </Badge>
                    </div>

                    {/* Контакты */}
                    {(result.application?.candidate_email || result.application?.candidate_phone) && (
                      <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
                        {result.application?.candidate_email && (
                          <div className="flex items-center gap-1">
                            <span className="font-medium">Email:</span>
                            <a href={`mailto:${result.application.candidate_email}`} className="text-blue-600 hover:underline">
                              {result.application.candidate_email}
                            </a>
                          </div>
                        )}
                        {result.application?.candidate_phone && (
                          <div className="flex items-center gap-1">
                            <span className="font-medium">Телефон:</span>
                            <a href={`tel:${result.application.candidate_phone}`} className="text-blue-600 hover:underline">
                              {result.application.candidate_phone}
                            </a>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Прогресс бар */}
                    <div className="flex items-center gap-3">
                      <div className="flex-1 max-w-xs">
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              (result.score || 0) >= 80
                                ? 'bg-green-500'
                                : (result.score || 0) >= 60
                                ? 'bg-orange-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${result.score || 0}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-sm text-muted-foreground">{result.score}%</span>
                    </div>

                    {/* Детали оценки */}
                    {(result.skills_match !== undefined || result.experience_match !== undefined) && (
                      <div className="flex gap-4 text-sm">
                        {result.skills_match !== undefined && (
                          <div>
                            <span className="text-muted-foreground">Навыки:</span>{' '}
                            <span className="font-medium">{result.skills_match}%</span>
                          </div>
                        )}
                        {result.experience_match !== undefined && (
                          <div>
                            <span className="text-muted-foreground">Опыт:</span>{' '}
                            <span className="font-medium">{result.experience_match}%</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Обоснование */}
                    {result.reasoning && (
                      <p className="text-sm text-muted-foreground line-clamp-2">{result.reasoning}</p>
                    )}

                    {/* Сильные стороны */}
                    {result.strengths && result.strengths.length > 0 && (
                      <div className="text-sm">
                        <span className="font-medium text-green-600">Сильные стороны:</span>{' '}
                        <span className="text-muted-foreground">{result.strengths.slice(0, 3).join(', ')}</span>
                        {result.strengths.length > 3 && <span className="text-muted-foreground"> и ещё {result.strengths.length - 3}...</span>}
                      </div>
                    )}

                    {/* Красные флаги */}
                    {result.red_flags && result.red_flags.length > 0 && (
                      <div className="text-sm">
                        <span className="font-medium text-red-600">⚠ Красные флаги:</span>{' '}
                        <span className="text-muted-foreground">{result.red_flags.join(', ')}</span>
                      </div>
                    )}

                    {/* Ссылка на резюме */}
                    {(result.application?.resume_url || result.resume_url) && (
                      <a
                        href={result.application?.resume_url || result.resume_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                      >
                        Открыть резюме на HH.ru
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>

                  {/* Балл */}
                  <div className="text-right">
                    <div className={`text-4xl font-bold ${getScoreColor(result.score || 0)}`}>
                      {result.score || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">/100</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Экспорт */}
      {sortedResults.length > 0 && (
        <Card>
          <CardContent className="flex items-center justify-between p-4">
            <p className="text-sm text-muted-foreground">
              Экспортируйте результаты в Excel для дальнейшей работы
            </p>
            <Button asChild>
              <Link
                to={`/export?vacancy=${selectedVacancy}&recommendation=${recommendationFilter}&minScore=${
                  minScore || 0
                }`}
              >
                <Download className="mr-2 h-4 w-4" />
                Экспорт в Excel
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Results;
