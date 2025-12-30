/**
 * Страница поиска кандидатов по базе резюме HH.ru
 * Создание поисковых проектов, запуск поиска, AI анализ
 * Design: Dark Industrial
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Plus, Play, Brain, Star, StarOff, Trash2,
  Loader2, AlertCircle, Users, TrendingUp, MapPin,
  Briefcase, ExternalLink, Sparkles
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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
    const variants: Record<string, { className: string; label: string }> = {
      draft: { className: 'bg-zinc-800 text-zinc-400 border-zinc-700', label: 'Черновик' },
      running: { className: 'bg-blue-500/15 text-blue-400 border-blue-500/30', label: 'Поиск...' },
      completed: { className: 'bg-zinc-700 text-zinc-300 border-zinc-600', label: 'Загружено' },
      analyzing: { className: 'bg-purple-500/15 text-purple-400 border-purple-500/30', label: 'Анализ...' },
      done: { className: 'bg-green-500/15 text-green-400 border-green-500/30', label: 'Готово' },
      failed: { className: 'bg-red-500/15 text-red-400 border-red-500/30', label: 'Ошибка' }
    };
    const config = variants[status] || { className: 'bg-zinc-800 text-zinc-400', label: status };
    return <span className={`px-2 py-0.5 rounded text-xs border ${config.className}`}>{config.label}</span>;
  };

  const getRecommendationBadge = (rec?: string) => {
    if (!rec) return null;
    const config: Record<string, { className: string; label: string }> = {
      hire: { className: 'bg-green-500/15 text-green-400 border-green-500/30', label: 'Нанять' },
      consider: { className: 'bg-amber-500/15 text-amber-400 border-amber-500/30', label: 'Рассмотреть' },
      reject: { className: 'bg-red-500/15 text-red-400 border-red-500/30', label: 'Отклонить' }
    };
    const c = config[rec];
    if (!c) return null;
    return (
      <span className={`px-2 py-0.5 rounded text-xs border ${c.className}`}>
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
          <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight">Поиск кандидатов</h1>
          <p className="text-zinc-500 text-sm mt-1">
            Поиск по базе резюме HH.ru с AI анализом
          </p>
        </div>

        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button className="bg-zinc-100 text-zinc-900 hover:bg-white font-medium">
              <Plus className="w-4 h-4 mr-2" />
              Новый поиск
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg bg-zinc-900 border-zinc-800">
            <DialogHeader>
              <DialogTitle className="text-zinc-100">Создать поисковый проект</DialogTitle>
              <DialogDescription className="text-zinc-500">
                Настройте параметры поиска кандидатов
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label className="text-zinc-300">Название поиска *</Label>
                <Input
                  placeholder="Python разработчики в Москве"
                  className="h-10 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500"
                  value={newSearch.name}
                  onChange={e => setNewSearch(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label className="text-zinc-300">Поисковый запрос *</Label>
                <Input
                  placeholder="Python Django FastAPI"
                  className="h-10 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500"
                  value={newSearch.search_query}
                  onChange={e => setNewSearch(prev => ({ ...prev, search_query: e.target.value }))}
                />
                <p className="text-xs text-zinc-600">
                  Ключевые слова: должность, навыки, технологии
                </p>
              </div>

              <div className="space-y-2">
                <Label className="text-zinc-300">Привязка к вакансии</Label>
                <Select
                  value={newSearch.vacancy_id}
                  onValueChange={v => setNewSearch(prev => ({ ...prev, vacancy_id: v }))}
                >
                  <SelectTrigger className="bg-zinc-800/50 border-zinc-700 text-zinc-100">
                    <SelectValue placeholder="Без привязки" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-900 border-zinc-800">
                    <SelectItem value="">Без привязки</SelectItem>
                    {vacancies.map(v => (
                      <SelectItem key={v.id} value={v.id}>{v.title}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-zinc-300">Регион</Label>
                  <Select
                    value={newSearch.filters.area}
                    onValueChange={v => setNewSearch(prev => ({
                      ...prev,
                      filters: { ...prev.filters, area: v }
                    }))}
                  >
                    <SelectTrigger className="bg-zinc-800/50 border-zinc-700 text-zinc-100">
                      <SelectValue placeholder="Любой" />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-800">
                      <SelectItem value="">Любой</SelectItem>
                      {dictionaries?.areas.map(a => (
                        <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-zinc-300">Опыт работы</Label>
                  <Select
                    value={newSearch.filters.experience}
                    onValueChange={v => setNewSearch(prev => ({
                      ...prev,
                      filters: { ...prev.filters, experience: v }
                    }))}
                  >
                    <SelectTrigger className="bg-zinc-800/50 border-zinc-700 text-zinc-100">
                      <SelectValue placeholder="Любой" />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-800">
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
                  <Label className="text-zinc-300">Зарплата от</Label>
                  <Input
                    type="number"
                    placeholder="100000"
                    className="h-10 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500"
                    value={newSearch.filters.salary_from}
                    onChange={e => setNewSearch(prev => ({
                      ...prev,
                      filters: { ...prev.filters, salary_from: e.target.value }
                    }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-zinc-300">Зарплата до</Label>
                  <Input
                    type="number"
                    placeholder="300000"
                    className="h-10 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500"
                    value={newSearch.filters.salary_to}
                    onChange={e => setNewSearch(prev => ({
                      ...prev,
                      filters: { ...prev.filters, salary_to: e.target.value }
                    }))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label className="text-zinc-300">Описание</Label>
                <Textarea
                  placeholder="Заметки о поиске..."
                  className="bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500 resize-none"
                  value={newSearch.description}
                  onChange={e => setNewSearch(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>
            </div>

            <DialogFooter className="gap-2">
              <Button
                variant="outline"
                onClick={() => setShowCreateDialog(false)}
                className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
              >
                Отмена
              </Button>
              <Button
                onClick={handleCreateSearch}
                disabled={!newSearch.name || !newSearch.search_query || isLoading}
                className="bg-zinc-100 text-zinc-900 hover:bg-white"
              >
                {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                Создать
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Alert className="bg-red-500/10 border-red-500/20">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-400">{error}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      <div className="grid grid-cols-12 gap-6">
        {/* Список поисков */}
        <div className="col-span-4 space-y-4">
          <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader className="pb-3 border-b border-zinc-800">
              <CardTitle className="text-base text-zinc-100">Поисковые проекты</CardTitle>
            </CardHeader>
            <CardContent className="p-3 space-y-2">
              {isLoading && searches.length === 0 ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
                </div>
              ) : searches.length === 0 ? (
                <div className="text-center py-8">
                  <Search className="w-12 h-12 mx-auto mb-3 text-zinc-700" />
                  <p className="text-zinc-500">Нет поисковых проектов</p>
                  <p className="text-sm text-zinc-600">Создайте первый поиск</p>
                </div>
              ) : (
                <AnimatePresence>
                  {searches.map((search, idx) => (
                    <motion.div
                      key={search.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        selectedSearch?.id === search.id
                          ? 'bg-zinc-800 border-zinc-600'
                          : 'border-zinc-800 hover:bg-zinc-800/50 hover:border-zinc-700'
                      }`}
                      onClick={() => setSelectedSearch(search)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-zinc-200 truncate">{search.name}</div>
                          <div className="text-sm text-zinc-500 truncate mt-0.5">
                            {search.search_query}
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                            {getStatusBadge(search.status)}
                            <span className="text-xs text-zinc-600">
                              {search.processed_count} кандидатов
                            </span>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-zinc-500 hover:text-red-400 hover:bg-red-500/10"
                          onClick={e => {
                            e.stopPropagation();
                            handleDeleteSearch(search.id);
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Детали и кандидаты */}
        <div className="col-span-8 space-y-4">
          {selectedSearch ? (
            <>
              {/* Информация о поиске */}
              <Card className="border-zinc-800 bg-zinc-900/50">
                <CardHeader className="pb-3 border-b border-zinc-800">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-zinc-100">{selectedSearch.name}</CardTitle>
                      <p className="text-sm text-zinc-500 mt-1">
                        Запрос: {selectedSearch.search_query}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        onClick={handleRunSearch}
                        disabled={isSearching || selectedSearch.status === 'running'}
                        className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
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
                        className="bg-zinc-100 text-zinc-900 hover:bg-white"
                      >
                        {isAnalyzing ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <Sparkles className="w-4 h-4 mr-2" />
                        )}
                        AI Анализ
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                {/* Статистика */}
                {stats && (
                  <CardContent className="pt-4">
                    <div className="grid grid-cols-4 gap-px bg-zinc-800 rounded-lg overflow-hidden">
                      <div className="bg-zinc-900 p-4 text-center">
                        <div className="text-2xl font-bold text-zinc-100 tabular-nums">{stats.total_candidates}</div>
                        <div className="text-xs text-zinc-500 mt-1">Всего</div>
                      </div>
                      <div className="bg-zinc-900 p-4 text-center">
                        <div className="text-2xl font-bold text-green-400 tabular-nums">{stats.hire_count}</div>
                        <div className="text-xs text-zinc-500 mt-1">Нанять</div>
                      </div>
                      <div className="bg-zinc-900 p-4 text-center">
                        <div className="text-2xl font-bold text-amber-400 tabular-nums">{stats.consider_count}</div>
                        <div className="text-xs text-zinc-500 mt-1">Рассмотреть</div>
                      </div>
                      <div className="bg-zinc-900 p-4 text-center">
                        <div className="text-2xl font-bold text-red-400 tabular-nums">{stats.reject_count}</div>
                        <div className="text-xs text-zinc-500 mt-1">Отклонить</div>
                      </div>
                    </div>
                    {stats.avg_score && (
                      <div className="mt-4 text-center">
                        <span className="text-zinc-500">Средний балл: </span>
                        <span className="font-semibold text-zinc-100">{stats.avg_score}</span>
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>

              {/* Фильтры */}
              <div className="flex gap-3 items-center">
                <Select value={recommendationFilter} onValueChange={setRecommendationFilter}>
                  <SelectTrigger className="w-48 bg-zinc-900/50 border-zinc-800 text-zinc-300">
                    <SelectValue placeholder="Все рекомендации" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-900 border-zinc-800">
                    <SelectItem value="all">Все рекомендации</SelectItem>
                    <SelectItem value="hire">Нанять</SelectItem>
                    <SelectItem value="consider">Рассмотреть</SelectItem>
                    <SelectItem value="reject">Отклонить</SelectItem>
                  </SelectContent>
                </Select>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setFavoritesOnly(!favoritesOnly)}
                  className={favoritesOnly
                    ? 'bg-amber-500/15 border-amber-500/30 text-amber-400 hover:bg-amber-500/20'
                    : 'border-zinc-700 text-zinc-400 hover:bg-zinc-800'
                  }
                >
                  <Star className={`w-4 h-4 mr-1 ${favoritesOnly ? 'fill-amber-400' : ''}`} />
                  Избранные
                </Button>
              </div>

              {/* Список кандидатов */}
              <div className="space-y-3">
                {candidates.length === 0 ? (
                  <Card className="border-zinc-800 bg-zinc-900/50">
                    <CardContent className="py-12 text-center">
                      <Users className="w-12 h-12 mx-auto mb-3 text-zinc-700" />
                      <p className="text-zinc-500">Нет кандидатов</p>
                      <p className="text-sm text-zinc-600">Запустите поиск для загрузки резюме</p>
                    </CardContent>
                  </Card>
                ) : (
                  <AnimatePresence>
                    {candidates.map((candidate, idx) => (
                      <motion.div
                        key={candidate.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.03 }}
                      >
                        <Card className="border-zinc-800 bg-zinc-900/50 hover:border-zinc-700 transition-colors">
                          <CardContent className="py-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-3">
                                  <div className="font-semibold text-lg text-zinc-100">
                                    {candidate.full_name}
                                  </div>
                                  {candidate.ai_score !== undefined && (
                                    <span className="px-2.5 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-100 text-sm font-medium tabular-nums">
                                      {candidate.ai_score}
                                    </span>
                                  )}
                                  {getRecommendationBadge(candidate.ai_recommendation)}
                                </div>

                                <div className="text-zinc-400 mt-1">
                                  {candidate.title}
                                </div>

                                <div className="flex flex-wrap gap-4 mt-3 text-sm text-zinc-500">
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
                                  <div className="flex flex-wrap gap-1.5 mt-3">
                                    {candidate.skills.slice(0, 6).map((skill, idx) => (
                                      <span
                                        key={idx}
                                        className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-400 text-xs"
                                      >
                                        {skill}
                                      </span>
                                    ))}
                                    {candidate.skills.length > 6 && (
                                      <span className="px-2 py-0.5 rounded border border-zinc-700 text-zinc-500 text-xs">
                                        +{candidate.skills.length - 6}
                                      </span>
                                    )}
                                  </div>
                                )}

                                {candidate.ai_summary && (
                                  <p className="text-sm mt-3 text-zinc-500 line-clamp-2">
                                    {candidate.ai_summary}
                                  </p>
                                )}
                              </div>

                              <div className="flex flex-col gap-1 ml-4">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-9 w-9 hover:bg-zinc-800"
                                  onClick={() => handleToggleFavorite(candidate)}
                                >
                                  {candidate.is_favorite ? (
                                    <Star className="w-5 h-5 fill-amber-400 text-amber-400" />
                                  ) : (
                                    <StarOff className="w-5 h-5 text-zinc-500" />
                                  )}
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-9 w-9 hover:bg-zinc-800"
                                  asChild
                                >
                                  <a
                                    href={`https://hh.ru/resume/${candidate.hh_resume_id}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    <ExternalLink className="w-5 h-5 text-zinc-500" />
                                  </a>
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                )}
              </div>
            </>
          ) : (
            <Card className="border-zinc-800 bg-zinc-900/50">
              <CardContent className="py-16 text-center">
                <Search className="w-16 h-16 mx-auto mb-4 text-zinc-700" />
                <h3 className="text-lg font-medium text-zinc-300 mb-2">Выберите поисковый проект</h3>
                <p className="text-zinc-500">Или создайте новый для поиска кандидатов</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default CandidateSearch;
