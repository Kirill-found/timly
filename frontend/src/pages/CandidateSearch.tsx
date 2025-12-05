/**
 * Страница поиска кандидатов по базе резюме HH.ru
 * Создание поисковых проектов, запуск поиска, AI анализ
 */
import React, { useState, useEffect } from 'react';
import {
  Search, Plus, Play, Brain, Star, StarOff, Filter, Trash2,
  ChevronRight, Loader2, AlertCircle, CheckCircle, XCircle,
  Users, TrendingUp, MapPin, Briefcase, Clock, ExternalLink
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/services/api';
import type { ResumeSearch, SearchCandidate, Vacancy, SearchStats, SearchDictionaries } from '@/types';

const CandidateSearch: React.FC = () => {
  // Состояния
  const [searches, setSearches] = useState<ResumeSearch[]>([]);
  const [selectedSearch, setSelectedSearch] = useState<ResumeSearch | null>(null);
  const [candidates, setCandidates] = useState<SearchCandidate[]>([]);
  const [stats, setStats] = useState<SearchStats | null>(null);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [dictionaries, setDictionaries] = useState<SearchDictionaries | null>(null);

  // UI состояния
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  // Фильтры кандидатов
  const [recommendationFilter, setRecommendationFilter] = useState<string>('all');
  const [favoritesOnly, setFavoritesOnly] = useState(false);

  // Форма создания поиска
  const [newSearch, setNewSearch] = useState({
    name: '',
    description: '',
    search_query: '',
    vacancy_id: '',
    filters: {
      area: '',
      experience: '',
      salary_from: '',
      salary_to: '',
    }
  });

  // Загрузка данных при монтировании
  useEffect(() => {
    loadSearches();
    loadVacancies();
    loadDictionaries();
  }, []);

  // Загрузка кандидатов при выборе поиска
  useEffect(() => {
    if (selectedSearch) {
      loadCandidates();
      loadStats();
    }
  }, [selectedSearch, recommendationFilter, favoritesOnly]);

  const loadSearches = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getResumeSearches();
      setSearches(data.searches || []);
    } catch (err: any) {
      console.error('Error loading searches:', err);
      setError('Ошибка загрузки поисковых проектов');
    } finally {
      setIsLoading(false);
    }
  };

  const loadVacancies = async () => {
    try {
      const data = await apiClient.getVacancies({ active_only: true });
      setVacancies(data || []);
    } catch (err) {
      console.error('Error loading vacancies:', err);
    }
  };

  const loadDictionaries = async () => {
    try {
      const data = await apiClient.getSearchDictionaries();
      setDictionaries(data);
    } catch (err) {
      console.error('Error loading dictionaries:', err);
    }
  };

  const loadCandidates = async () => {
    if (!selectedSearch) return;

    try {
      const params: any = { per_page: 50 };
      if (recommendationFilter !== 'all') {
        params.recommendation = recommendationFilter;
      }
      if (favoritesOnly) {
        params.favorites_only = true;
      }

      const data = await apiClient.getSearchCandidates(selectedSearch.id, params);
      setCandidates(data.candidates || []);
    } catch (err: any) {
      console.error('Error loading candidates:', err);
    }
  };

  const loadStats = async () => {
    if (!selectedSearch) return;

    try {
      const data = await apiClient.getSearchStats(selectedSearch.id);
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const handleCreateSearch = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const filters: any = {};
      if (newSearch.filters.area) filters.area = newSearch.filters.area;
      if (newSearch.filters.experience) filters.experience = newSearch.filters.experience;
      if (newSearch.filters.salary_from) filters.salary_from = parseInt(newSearch.filters.salary_from);
      if (newSearch.filters.salary_to) filters.salary_to = parseInt(newSearch.filters.salary_to);

      const created = await apiClient.createResumeSearch({
        name: newSearch.name,
        description: newSearch.description || undefined,
        search_query: newSearch.search_query,
        vacancy_id: newSearch.vacancy_id || undefined,
        filters: Object.keys(filters).length > 0 ? filters : undefined
      });

      setSearches(prev => [created, ...prev]);
      setSelectedSearch(created);
      setShowCreateDialog(false);
      setNewSearch({
        name: '',
        description: '',
        search_query: '',
        vacancy_id: '',
        filters: { area: '', experience: '', salary_from: '', salary_to: '' }
      });
    } catch (err: any) {
      console.error('Error creating search:', err);
      setError(err.response?.data?.detail?.message || 'Ошибка создания поиска');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunSearch = async () => {
    if (!selectedSearch) return;

    try {
      setIsSearching(true);
      setError(null);

      await apiClient.runResumeSearch(selectedSearch.id, 100);

      // Обновляем данные
      const updated = await apiClient.getResumeSearch(selectedSearch.id);
      setSelectedSearch(updated);
      setSearches(prev => prev.map(s => s.id === updated.id ? updated : s));

      await loadCandidates();
      await loadStats();
    } catch (err: any) {
      console.error('Error running search:', err);
      setError(err.response?.data?.detail?.message || 'Ошибка выполнения поиска');
    } finally {
      setIsSearching(false);
    }
  };

  const handleAnalyzeCandidates = async () => {
    if (!selectedSearch) return;

    try {
      setIsAnalyzing(true);
      setError(null);

      await apiClient.analyzeSearchCandidates(selectedSearch.id);

      // Обновляем данные
      const updated = await apiClient.getResumeSearch(selectedSearch.id);
      setSelectedSearch(updated);
      setSearches(prev => prev.map(s => s.id === updated.id ? updated : s));

      await loadCandidates();
      await loadStats();
    } catch (err: any) {
      console.error('Error analyzing candidates:', err);
      setError(err.response?.data?.detail?.message || 'Ошибка AI анализа');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleToggleFavorite = async (candidate: SearchCandidate) => {
    if (!selectedSearch) return;

    try {
      await apiClient.updateSearchCandidate(selectedSearch.id, candidate.id, {
        is_favorite: !candidate.is_favorite
      });

      setCandidates(prev => prev.map(c =>
        c.id === candidate.id ? { ...c, is_favorite: !c.is_favorite } : c
      ));
    } catch (err) {
      console.error('Error toggling favorite:', err);
    }
  };

  const handleDeleteSearch = async (searchId: string) => {
    if (!confirm('Удалить поисковый проект?')) return;

    try {
      await apiClient.deleteResumeSearch(searchId);
      setSearches(prev => prev.filter(s => s.id !== searchId));
      if (selectedSearch?.id === searchId) {
        setSelectedSearch(null);
        setCandidates([]);
        setStats(null);
      }
    } catch (err) {
      console.error('Error deleting search:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; label: string }> = {
      draft: { variant: 'outline', label: 'Черновик' },
      running: { variant: 'default', label: 'Поиск...' },
      completed: { variant: 'secondary', label: 'Загружено' },
      analyzing: { variant: 'default', label: 'Анализ...' },
      done: { variant: 'default', label: 'Готово' },
      failed: { variant: 'destructive', label: 'Ошибка' }
    };
    const config = variants[status] || { variant: 'outline' as const, label: status };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getRecommendationBadge = (rec?: string) => {
    if (!rec) return null;
    const config: Record<string, { color: string; label: string }> = {
      hire: { color: 'bg-green-500', label: 'Нанять' },
      consider: { color: 'bg-yellow-500', label: 'Рассмотреть' },
      reject: { color: 'bg-red-500', label: 'Отклонить' }
    };
    const c = config[rec];
    if (!c) return null;
    return (
      <span className={`px-2 py-1 rounded text-white text-xs ${c.color}`}>
        {c.label}
      </span>
    );
  };

  const formatSalary = (salary?: number, currency: string = 'RUB') => {
    if (!salary) return 'Не указана';
    return `${salary.toLocaleString()} ${currency}`;
  };

  const formatExperience = (months?: number) => {
    if (!months) return 'Не указан';
    const years = Math.floor(months / 12);
    const m = months % 12;
    if (years === 0) return `${m} мес.`;
    if (m === 0) return `${years} лет`;
    return `${years} г. ${m} мес.`;
  };

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Поиск кандидатов</h1>
          <p className="text-muted-foreground">
            Поиск по базе резюме HH.ru с AI анализом
          </p>
        </div>

        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Новый поиск
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Создать поисковый проект</DialogTitle>
              <DialogDescription>
                Настройте параметры поиска кандидатов
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Название поиска *</Label>
                <Input
                  placeholder="Python разработчики в Москве"
                  value={newSearch.name}
                  onChange={e => setNewSearch(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label>Поисковый запрос *</Label>
                <Input
                  placeholder="Python Django FastAPI"
                  value={newSearch.search_query}
                  onChange={e => setNewSearch(prev => ({ ...prev, search_query: e.target.value }))}
                />
                <p className="text-xs text-muted-foreground">
                  Ключевые слова: должность, навыки, технологии
                </p>
              </div>

              <div className="space-y-2">
                <Label>Привязка к вакансии (для контекста AI анализа)</Label>
                <Select
                  value={newSearch.vacancy_id}
                  onValueChange={v => setNewSearch(prev => ({ ...prev, vacancy_id: v }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Без привязки" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Без привязки</SelectItem>
                    {vacancies.map(v => (
                      <SelectItem key={v.id} value={v.id}>{v.title}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Регион</Label>
                  <Select
                    value={newSearch.filters.area}
                    onValueChange={v => setNewSearch(prev => ({
                      ...prev,
                      filters: { ...prev.filters, area: v }
                    }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Любой" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Любой</SelectItem>
                      {dictionaries?.areas.map(a => (
                        <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Опыт работы</Label>
                  <Select
                    value={newSearch.filters.experience}
                    onValueChange={v => setNewSearch(prev => ({
                      ...prev,
                      filters: { ...prev.filters, experience: v }
                    }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Любой" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Любой</SelectItem>
                      {dictionaries?.experience.map(e => (
                        <SelectItem key={e.id} value={e.id}>{e.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Зарплата от</Label>
                  <Input
                    type="number"
                    placeholder="100000"
                    value={newSearch.filters.salary_from}
                    onChange={e => setNewSearch(prev => ({
                      ...prev,
                      filters: { ...prev.filters, salary_from: e.target.value }
                    }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Зарплата до</Label>
                  <Input
                    type="number"
                    placeholder="300000"
                    value={newSearch.filters.salary_to}
                    onChange={e => setNewSearch(prev => ({
                      ...prev,
                      filters: { ...prev.filters, salary_to: e.target.value }
                    }))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Описание (опционально)</Label>
                <Textarea
                  placeholder="Заметки о поиске..."
                  value={newSearch.description}
                  onChange={e => setNewSearch(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Отмена
              </Button>
              <Button
                onClick={handleCreateSearch}
                disabled={!newSearch.name || !newSearch.search_query || isLoading}
              >
                {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                Создать
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-12 gap-6">
        {/* Список поисков */}
        <div className="col-span-4 space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Поисковые проекты</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {isLoading && searches.length === 0 ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                </div>
              ) : searches.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Search className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Нет поисковых проектов</p>
                  <p className="text-sm">Создайте первый поиск</p>
                </div>
              ) : (
                searches.map(search => (
                  <div
                    key={search.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedSearch?.id === search.id
                        ? 'bg-primary/10 border-primary'
                        : 'hover:bg-muted'
                    }`}
                    onClick={() => setSelectedSearch(search)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate">{search.name}</div>
                        <div className="text-sm text-muted-foreground truncate">
                          {search.search_query}
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          {getStatusBadge(search.status)}
                          <span className="text-xs text-muted-foreground">
                            {search.processed_count} кандидатов
                          </span>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={e => {
                          e.stopPropagation();
                          handleDeleteSearch(search.id);
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Детали и кандидаты */}
        <div className="col-span-8 space-y-4">
          {selectedSearch ? (
            <>
              {/* Информация о поиске */}
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle>{selectedSearch.name}</CardTitle>
                      <CardDescription className="mt-1">
                        Запрос: {selectedSearch.search_query}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        onClick={handleRunSearch}
                        disabled={isSearching || selectedSearch.status === 'running'}
                      >
                        {isSearching ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <Play className="w-4 h-4 mr-2" />
                        )}
                        Запустить поиск
                      </Button>
                      <Button
                        onClick={handleAnalyzeCandidates}
                        disabled={isAnalyzing || selectedSearch.processed_count === 0}
                      >
                        {isAnalyzing ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <Brain className="w-4 h-4 mr-2" />
                        )}
                        AI Анализ
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                {/* Статистика */}
                {stats && (
                  <CardContent>
                    <div className="grid grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold">{stats.total_candidates}</div>
                        <div className="text-xs text-muted-foreground">Всего</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{stats.hire_count}</div>
                        <div className="text-xs text-muted-foreground">Нанять</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-600">{stats.consider_count}</div>
                        <div className="text-xs text-muted-foreground">Рассмотреть</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{stats.reject_count}</div>
                        <div className="text-xs text-muted-foreground">Отклонить</div>
                      </div>
                    </div>
                    {stats.avg_score && (
                      <div className="mt-4 text-center">
                        <span className="text-muted-foreground">Средний балл: </span>
                        <span className="font-semibold">{stats.avg_score}</span>
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>

              {/* Фильтры */}
              <div className="flex gap-4 items-center">
                <Select value={recommendationFilter} onValueChange={setRecommendationFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Все рекомендации" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Все рекомендации</SelectItem>
                    <SelectItem value="hire">Нанять</SelectItem>
                    <SelectItem value="consider">Рассмотреть</SelectItem>
                    <SelectItem value="reject">Отклонить</SelectItem>
                  </SelectContent>
                </Select>

                <Button
                  variant={favoritesOnly ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFavoritesOnly(!favoritesOnly)}
                >
                  <Star className="w-4 h-4 mr-1" />
                  Избранные
                </Button>
              </div>

              {/* Список кандидатов */}
              <div className="space-y-3">
                {candidates.length === 0 ? (
                  <Card>
                    <CardContent className="py-12 text-center text-muted-foreground">
                      <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>Нет кандидатов</p>
                      <p className="text-sm">Запустите поиск для загрузки резюме</p>
                    </CardContent>
                  </Card>
                ) : (
                  candidates.map(candidate => (
                    <Card key={candidate.id}>
                      <CardContent className="py-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <div className="font-semibold text-lg">
                                {candidate.full_name}
                              </div>
                              {candidate.ai_score !== undefined && (
                                <Badge variant="outline" className="text-lg px-3">
                                  {candidate.ai_score}
                                </Badge>
                              )}
                              {getRecommendationBadge(candidate.ai_recommendation)}
                            </div>

                            <div className="text-muted-foreground mt-1">
                              {candidate.title}
                            </div>

                            <div className="flex flex-wrap gap-4 mt-3 text-sm text-muted-foreground">
                              {candidate.area && (
                                <span className="flex items-center gap-1">
                                  <MapPin className="w-3 h-3" />
                                  {candidate.area}
                                </span>
                              )}
                              {candidate.experience_years && (
                                <span className="flex items-center gap-1">
                                  <Briefcase className="w-3 h-3" />
                                  {formatExperience(candidate.experience_years)}
                                </span>
                              )}
                              {candidate.salary && (
                                <span className="flex items-center gap-1">
                                  <TrendingUp className="w-3 h-3" />
                                  {formatSalary(candidate.salary, candidate.currency)}
                                </span>
                              )}
                              {candidate.age && (
                                <span>{candidate.age} лет</span>
                              )}
                            </div>

                            {candidate.skills.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-3">
                                {candidate.skills.slice(0, 6).map((skill, idx) => (
                                  <Badge key={idx} variant="secondary" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                                {candidate.skills.length > 6 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{candidate.skills.length - 6}
                                  </Badge>
                                )}
                              </div>
                            )}

                            {candidate.ai_summary && (
                              <p className="text-sm mt-3 text-muted-foreground line-clamp-2">
                                {candidate.ai_summary}
                              </p>
                            )}
                          </div>

                          <div className="flex flex-col gap-2 ml-4">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleToggleFavorite(candidate)}
                            >
                              {candidate.is_favorite ? (
                                <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                              ) : (
                                <StarOff className="w-5 h-5" />
                              )}
                            </Button>
                            <Button variant="ghost" size="icon" asChild>
                              <a
                                href={`https://hh.ru/resume/${candidate.hh_resume_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <ExternalLink className="w-5 h-5" />
                              </a>
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </>
          ) : (
            <Card>
              <CardContent className="py-16 text-center text-muted-foreground">
                <Search className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium mb-2">Выберите поисковый проект</h3>
                <p>Или создайте новый для поиска кандидатов</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default CandidateSearch;
