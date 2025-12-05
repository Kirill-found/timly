/**
 * Страница загрузки и анализа резюме
 * Загрузка PDF/Excel файлов с AI анализом
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Upload, FileText, FileSpreadsheet, Trash2, Star, StarOff,
  Loader2, AlertCircle, CheckCircle, Brain, Filter,
  Users, TrendingUp, Phone, Mail, MapPin, Briefcase
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
      if (selectedVacancy) params.vacancy_id = selectedVacancy;
      if (recommendationFilter !== 'all') params.recommendation = recommendationFilter;
      if (minScore) params.min_score = parseInt(minScore);

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
        if (selectedVacancy) {
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

  // Получение цвета рекомендации
  const getRecommendationColor = (rec: string | null) => {
    switch (rec) {
      case 'hire': return 'bg-green-500';
      case 'interview': return 'bg-blue-500';
      case 'maybe': return 'bg-yellow-500';
      case 'reject': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getRecommendationText = (rec: string | null) => {
    switch (rec) {
      case 'hire': return 'Нанять';
      case 'interview': return 'Собеседование';
      case 'maybe': return 'Возможно';
      case 'reject': return 'Отклонить';
      default: return 'Не проанализирован';
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Заголовок */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Загрузка резюме</h1>
          <p className="text-muted-foreground">
            Загрузите PDF или Excel с резюме для AI-анализа
          </p>
        </div>
      </div>

      {/* Уведомления */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {success && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Зона загрузки */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Загрузить файлы
          </CardTitle>
          <CardDescription>
            Поддерживаются PDF резюме и Excel файлы со списками кандидатов
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Выбор вакансии */}
          <div className="mb-4">
            <Label>Вакансия для сравнения (опционально)</Label>
            <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
              <SelectTrigger className="w-full mt-1">
                <SelectValue placeholder="Выберите вакансию для AI анализа" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Без вакансии</SelectItem>
                {vacancies.map(v => (
                  <SelectItem key={v.id} value={v.id}>{v.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Drag & Drop зона */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {isUploading ? (
              <div className="space-y-4">
                <Loader2 className="h-10 w-10 mx-auto animate-spin text-primary" />
                <p>Загрузка и анализ...</p>
                <Progress value={uploadProgress} className="w-full max-w-xs mx-auto" />
              </div>
            ) : (
              <>
                <div className="flex justify-center gap-4 mb-4">
                  <FileText className="h-10 w-10 text-red-500" />
                  <FileSpreadsheet className="h-10 w-10 text-green-500" />
                </div>
                <p className="text-lg mb-2">Перетащите файлы сюда</p>
                <p className="text-sm text-muted-foreground mb-4">
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
                <Button variant="outline" onClick={() => document.getElementById('file-upload')?.click()}>
                  Выбрать файлы
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Фильтры */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <Label>AI рекомендация</Label>
              <Select value={recommendationFilter} onValueChange={(v) => { setRecommendationFilter(v); loadCandidates(); }}>
                <SelectTrigger className="mt-1">
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
            <div className="flex-1 min-w-[200px]">
              <Label>Мин. AI Score</Label>
              <Select value={minScore} onValueChange={(v) => { setMinScore(v); loadCandidates(); }}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Любой" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Любой</SelectItem>
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
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Загруженные кандидаты ({candidates.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          ) : candidates.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Нет загруженных кандидатов</p>
              <p className="text-sm">Загрузите PDF или Excel файлы выше</p>
            </div>
          ) : (
            <div className="space-y-4">
              {candidates.map(candidate => (
                <div
                  key={candidate.id}
                  className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      {/* Имя и должность */}
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold">{candidate.full_name}</h3>
                        {candidate.is_analyzed && (
                          <Badge className={getRecommendationColor(candidate.ai_recommendation)}>
                            {getRecommendationText(candidate.ai_recommendation)}
                          </Badge>
                        )}
                        {candidate.ai_score && (
                          <Badge variant="outline">{candidate.ai_score}%</Badge>
                        )}
                      </div>

                      {/* Инфо */}
                      <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mb-2">
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
                      <div className="flex gap-4 text-sm mb-2">
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
                        <div className="flex flex-wrap gap-1 mb-2">
                          {candidate.skills.slice(0, 5).map((skill, i) => (
                            <Badge key={i} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                          {candidate.skills.length > 5 && (
                            <Badge variant="secondary" className="text-xs">
                              +{candidate.skills.length - 5}
                            </Badge>
                          )}
                        </div>
                      )}

                      {/* AI Summary */}
                      {candidate.ai_summary && (
                        <p className="text-sm text-muted-foreground mt-2 italic">
                          {candidate.ai_summary}
                        </p>
                      )}

                      {/* Strengths & Weaknesses */}
                      {candidate.is_analyzed && (
                        <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                          {candidate.ai_strengths.length > 0 && (
                            <div>
                              <p className="font-medium text-green-600 mb-1">Сильные стороны:</p>
                              <ul className="list-disc list-inside text-muted-foreground">
                                {candidate.ai_strengths.slice(0, 3).map((s, i) => (
                                  <li key={i}>{s}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {candidate.ai_weaknesses.length > 0 && (
                            <div>
                              <p className="font-medium text-orange-600 mb-1">Слабые стороны:</p>
                              <ul className="list-disc list-inside text-muted-foreground">
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
                    <div className="flex flex-col gap-2 ml-4">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => toggleFavorite(candidate)}
                      >
                        {candidate.is_favorite ? (
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        ) : (
                          <StarOff className="h-4 w-4" />
                        )}
                      </Button>
                      {!candidate.is_analyzed && selectedVacancy && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => analyzeCandidate(candidate.id, selectedVacancy)}
                          title="Анализировать"
                        >
                          <Brain className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteCandidate(candidate.id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>

                  {/* Источник файла */}
                  <div className="mt-2 pt-2 border-t text-xs text-muted-foreground flex items-center gap-2">
                    {candidate.source === 'pdf' ? (
                      <FileText className="h-3 w-3" />
                    ) : (
                      <FileSpreadsheet className="h-3 w-3" />
                    )}
                    {candidate.original_filename}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default UploadCandidates;
