/**
 * Страница загрузки и анализа резюме
 * Загрузка PDF/Excel файлов с AI анализом
 * Design: Dark Industrial
 */
import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload, FileText, FileSpreadsheet, Trash2, Star, StarOff,
  Loader2, AlertCircle, CheckCircle, Sparkles,
  Users, Phone, Mail, MapPin, Briefcase
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Label } from '@/components/ui/label';
import { apiClient } from '@/services/api';

interface UploadedCandidate {
  id: string;
  source: 'pdf' | 'excel';
  original_filename: string;
  full_name: string;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  phone: string | null;
  title: string | null;
  city: string | null;
  salary_expectation: number | null;
  experience_years: number | null;
  skills: string[];
  is_analyzed: boolean;
  ai_score: number | null;
  ai_recommendation: string | null;
  ai_summary: string | null;
  ai_strengths: string[];
  ai_weaknesses: string[];
  ai_red_flags: string[];
  is_favorite: boolean;
  is_contacted: boolean;
  notes: string | null;
  created_at: string;
}

interface Vacancy {
  id: string;
  title: string;
}

const UploadCandidates: React.FC = () => {
  // Состояния
  const [candidates, setCandidates] = useState<UploadedCandidate[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [selectedVacancy, setSelectedVacancy] = useState<string>('');
  const [selectedCandidate, setSelectedCandidate] = useState<UploadedCandidate | null>(null);

  // UI состояния
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Фильтры
  const [recommendationFilter, setRecommendationFilter] = useState<string>('all');
  const [minScore, setMinScore] = useState<string>('');

  // Drag and drop
  const [isDragging, setIsDragging] = useState(false);

  // Загрузка данных
  useEffect(() => {
    loadCandidates();
    loadVacancies();
  }, []);

  const loadCandidates = async () => {
    setIsLoading(true);
    try {
      const params: any = {};
      if (selectedVacancy && selectedVacancy !== '_none') params.vacancy_id = selectedVacancy;
      if (recommendationFilter !== 'all') params.recommendation = recommendationFilter;
      if (minScore && minScore !== '_any') params.min_score = parseInt(minScore);

      const response = await apiClient.get('/api/candidates/uploaded-candidates/', { params });
      setCandidates(response.data.candidates);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки кандидатов');
    } finally {
      setIsLoading(false);
    }
  };

  const loadVacancies = async () => {
    try {
      const response = await apiClient.get('/api/vacancies/');
      setVacancies(response.data.vacancies || []);
    } catch (err) {
      console.error('Ошибка загрузки вакансий:', err);
    }
  };

  // Обработка загрузки файлов
  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);
    setSuccess(null);

    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const isPdf = file.name.toLowerCase().endsWith('.pdf');
      const isExcel = file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls');

      if (!isPdf && !isExcel) {
        errorCount++;
        continue;
      }

      try {
        const formData = new FormData();
        formData.append('file', file);
        if (selectedVacancy && selectedVacancy !== '_none') {
          formData.append('vacancy_id', selectedVacancy);
        }
        formData.append('auto_analyze', 'true');

        const endpoint = isPdf
          ? '/api/candidates/uploaded-candidates/upload/pdf'
          : '/api/candidates/uploaded-candidates/upload/excel';

        await apiClient.post(endpoint, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        successCount++;
      } catch (err: any) {
        console.error(`Ошибка загрузки ${file.name}:`, err);
        errorCount++;
      }

      setUploadProgress(((i + 1) / files.length) * 100);
    }

    setIsUploading(false);

    if (successCount > 0) {
      setSuccess(`Успешно загружено: ${successCount} файл(ов)`);
      loadCandidates();
    }
    if (errorCount > 0) {
      setError(`Ошибки при загрузке: ${errorCount} файл(ов)`);
    }
  };

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileUpload(e.dataTransfer.files);
  }, [selectedVacancy]);

  // Анализ кандидата
  const analyzeCandidate = async (candidateId: string, vacancyId: string) => {
    try {
      await apiClient.post(`/api/candidates/uploaded-candidates/${candidateId}/analyze`, null, {
        params: { vacancy_id: vacancyId }
      });
      loadCandidates();
      setSuccess('Анализ завершен');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка анализа');
    }
  };

  // Удаление кандидата
  const deleteCandidate = async (candidateId: string) => {
    if (!confirm('Удалить кандидата?')) return;
    try {
      await apiClient.delete(`/api/candidates/uploaded-candidates/${candidateId}`);
      loadCandidates();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления');
    }
  };

  // Toggle favorite
  const toggleFavorite = async (candidate: UploadedCandidate) => {
    try {
      await apiClient.patch(`/api/candidates/uploaded-candidates/${candidate.id}`, {
        is_favorite: !candidate.is_favorite
      });
      loadCandidates();
    } catch (err) {
      console.error('Ошибка:', err);
    }
  };

  // Получение бейджа рекомендации
  const getRecommendationBadge = (rec: string | null) => {
    const config: Record<string, { className: string; label: string }> = {
      hire: { className: 'bg-green-500/15 text-green-400 border-green-500/30', label: 'Нанять' },
      interview: { className: 'bg-blue-500/15 text-blue-400 border-blue-500/30', label: 'Собеседование' },
      maybe: { className: 'bg-amber-500/15 text-amber-400 border-amber-500/30', label: 'Возможно' },
      reject: { className: 'bg-red-500/15 text-red-400 border-red-500/30', label: 'Отклонить' },
    };
    const c = rec ? config[rec] : null;
    if (!c) return null;
    return (
      <span className={`px-2 py-0.5 rounded text-xs border ${c.className}`}>
        {c.label}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight">Загрузка резюме</h1>
        <p className="text-zinc-500 text-sm mt-1">
          Загрузите PDF или Excel с резюме для AI-анализа
        </p>
      </div>

      {/* Уведомления */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Alert className="bg-red-500/10 border-red-500/20">
              <AlertCircle className="h-4 w-4 text-red-400" />
              <AlertDescription className="text-red-400">{error}</AlertDescription>
            </Alert>
          </motion.div>
        )}
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Alert className="bg-green-500/10 border-green-500/20">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <AlertDescription className="text-green-400">{success}</AlertDescription>
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Зона загрузки */}
      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardHeader className="border-b border-zinc-800">
          <CardTitle className="flex items-center gap-2 text-zinc-100">
            <Upload className="h-5 w-5 text-zinc-400" />
            Загрузить файлы
          </CardTitle>
          <p className="text-sm text-zinc-500">
            Поддерживаются PDF резюме и Excel файлы со списками кандидатов
          </p>
        </CardHeader>
        <CardContent className="pt-6">
          {/* Выбор вакансии */}
          <div className="mb-4">
            <Label className="text-zinc-300">Вакансия для сравнения</Label>
            <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
              <SelectTrigger className="mt-1.5 bg-zinc-800/50 border-zinc-700 text-zinc-100">
                <SelectValue placeholder="Выберите вакансию для AI анализа" />
              </SelectTrigger>
              <SelectContent className="bg-zinc-900 border-zinc-800">
                <SelectItem value="_none">Без вакансии</SelectItem>
                {vacancies.map(v => (
                  <SelectItem key={v.id} value={v.id}>{v.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Drag & Drop зона */}
          <div
            className={`border-2 border-dashed rounded-xl p-10 text-center transition-all ${
              isDragging
                ? 'border-zinc-500 bg-zinc-800/50'
                : 'border-zinc-700 hover:border-zinc-600'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {isUploading ? (
              <div className="space-y-4">
                <Loader2 className="h-10 w-10 mx-auto animate-spin text-zinc-400" />
                <p className="text-zinc-300">Загрузка и анализ...</p>
                <Progress value={uploadProgress} className="w-full max-w-xs mx-auto h-1.5 bg-zinc-800" />
              </div>
            ) : (
              <>
                <div className="flex justify-center gap-4 mb-4">
                  <div className="w-12 h-12 rounded-lg bg-red-500/10 flex items-center justify-center">
                    <FileText className="h-6 w-6 text-red-400" />
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <FileSpreadsheet className="h-6 w-6 text-green-400" />
                  </div>
                </div>
                <p className="text-lg text-zinc-200 mb-1">Перетащите файлы сюда</p>
                <p className="text-sm text-zinc-500 mb-4">
                  PDF, XLSX, XLS (макс. 10 MB)
                </p>
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".pdf,.xlsx,.xls"
                  multiple
                  onChange={(e) => handleFileUpload(e.target.files)}
                />
                <Button
                  variant="outline"
                  onClick={() => document.getElementById('file-upload')?.click()}
                  className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                >
                  Выбрать файлы
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Фильтры */}
      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardContent className="pt-6">
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <Label className="text-zinc-300">AI рекомендация</Label>
              <Select value={recommendationFilter} onValueChange={(v) => { setRecommendationFilter(v); loadCandidates(); }}>
                <SelectTrigger className="mt-1.5 bg-zinc-800/50 border-zinc-700 text-zinc-100">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-800">
                  <SelectItem value="all">Все</SelectItem>
                  <SelectItem value="hire">Нанять</SelectItem>
                  <SelectItem value="interview">Собеседование</SelectItem>
                  <SelectItem value="maybe">Возможно</SelectItem>
                  <SelectItem value="reject">Отклонить</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1 min-w-[200px]">
              <Label className="text-zinc-300">Мин. AI Score</Label>
              <Select value={minScore} onValueChange={(v) => { setMinScore(v); loadCandidates(); }}>
                <SelectTrigger className="mt-1.5 bg-zinc-800/50 border-zinc-700 text-zinc-100">
                  <SelectValue placeholder="Любой" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-800">
                  <SelectItem value="_any">Любой</SelectItem>
                  <SelectItem value="90">90+</SelectItem>
                  <SelectItem value="70">70+</SelectItem>
                  <SelectItem value="50">50+</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Список кандидатов */}
      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardHeader className="border-b border-zinc-800">
          <CardTitle className="flex items-center gap-2 text-zinc-100">
            <Users className="h-5 w-5 text-zinc-400" />
            Загруженные кандидаты
            <span className="ml-1 text-zinc-500 font-normal">({candidates.length})</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
            </div>
          ) : candidates.length === 0 ? (
            <div className="text-center py-12">
              <Users className="h-12 w-12 mx-auto mb-4 text-zinc-700" />
              <p className="text-zinc-500">Нет загруженных кандидатов</p>
              <p className="text-sm text-zinc-600">Загрузите PDF или Excel файлы выше</p>
            </div>
          ) : (
            <div className="space-y-3">
              <AnimatePresence>
                {candidates.map((candidate, idx) => (
                  <motion.div
                    key={candidate.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.03 }}
                    className="border border-zinc-800 rounded-lg p-4 hover:border-zinc-700 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        {/* Имя и должность */}
                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                          <h3 className="font-semibold text-zinc-100">{candidate.full_name}</h3>
                          {candidate.is_analyzed && getRecommendationBadge(candidate.ai_recommendation)}
                          {candidate.ai_score && (
                            <span className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200 text-xs font-medium tabular-nums">
                              {candidate.ai_score}%
                            </span>
                          )}
                        </div>

                        {/* Инфо */}
                        <div className="flex flex-wrap gap-4 text-sm text-zinc-500 mb-2">
                          {candidate.title && (
                            <span className="flex items-center gap-1">
                              <Briefcase className="h-3 w-3" />
                              {candidate.title}
                            </span>
                          )}
                          {candidate.city && (
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {candidate.city}
                            </span>
                          )}
                          {candidate.experience_years && (
                            <span>Опыт: {candidate.experience_years} лет</span>
                          )}
                          {candidate.salary_expectation && (
                            <span>ЗП: {candidate.salary_expectation.toLocaleString()} ₽</span>
                          )}
                        </div>

                        {/* Контакты */}
                        <div className="flex gap-4 text-sm text-zinc-400 mb-2">
                          {candidate.email && (
                            <span className="flex items-center gap-1">
                              <Mail className="h-3 w-3" />
                              {candidate.email}
                            </span>
                          )}
                          {candidate.phone && (
                            <span className="flex items-center gap-1">
                              <Phone className="h-3 w-3" />
                              {candidate.phone}
                            </span>
                          )}
                        </div>

                        {/* Навыки */}
                        {candidate.skills && candidate.skills.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mb-2">
                            {candidate.skills.slice(0, 5).map((skill, i) => (
                              <span
                                key={i}
                                className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-400 text-xs"
                              >
                                {skill}
                              </span>
                            ))}
                            {candidate.skills.length > 5 && (
                              <span className="px-2 py-0.5 rounded border border-zinc-700 text-zinc-500 text-xs">
                                +{candidate.skills.length - 5}
                              </span>
                            )}
                          </div>
                        )}

                        {/* AI Summary */}
                        {candidate.ai_summary && (
                          <p className="text-sm text-zinc-500 mt-2 italic">
                            {candidate.ai_summary}
                          </p>
                        )}

                        {/* Strengths & Weaknesses */}
                        {candidate.is_analyzed && (candidate.ai_strengths.length > 0 || candidate.ai_weaknesses.length > 0) && (
                          <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                            {candidate.ai_strengths.length > 0 && (
                              <div>
                                <p className="font-medium text-green-400 mb-1">Сильные стороны:</p>
                                <ul className="list-disc list-inside text-zinc-500 space-y-0.5">
                                  {candidate.ai_strengths.slice(0, 3).map((s, i) => (
                                    <li key={i}>{s}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {candidate.ai_weaknesses.length > 0 && (
                              <div>
                                <p className="font-medium text-amber-400 mb-1">Слабые стороны:</p>
                                <ul className="list-disc list-inside text-zinc-500 space-y-0.5">
                                  {candidate.ai_weaknesses.slice(0, 3).map((w, i) => (
                                    <li key={i}>{w}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Действия */}
                      <div className="flex flex-col gap-1 ml-4">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-9 w-9 hover:bg-zinc-800"
                          onClick={() => toggleFavorite(candidate)}
                        >
                          {candidate.is_favorite ? (
                            <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                          ) : (
                            <StarOff className="h-4 w-4 text-zinc-500" />
                          )}
                        </Button>
                        {!candidate.is_analyzed && selectedVacancy && selectedVacancy !== '_none' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-9 w-9 hover:bg-zinc-800"
                            onClick={() => analyzeCandidate(candidate.id, selectedVacancy)}
                            title="Анализировать"
                          >
                            <Sparkles className="h-4 w-4 text-zinc-500" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-9 w-9 hover:bg-red-500/10"
                          onClick={() => deleteCandidate(candidate.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-400" />
                        </Button>
                      </div>
                    </div>

                    {/* Источник файла */}
                    <div className="mt-3 pt-3 border-t border-zinc-800 text-xs text-zinc-600 flex items-center gap-2">
                      {candidate.source === 'pdf' ? (
                        <FileText className="h-3 w-3" />
                      ) : (
                        <FileSpreadsheet className="h-3 w-3" />
                      )}
                      {candidate.original_filename}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default UploadCandidates;
