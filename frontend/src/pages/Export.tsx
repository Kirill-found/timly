/**
 * Страница экспорта данных
 * Экспорт результатов анализа в Excel
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Download, FileSpreadsheet, Filter, CheckCircle, Clock, XCircle } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
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
    <div className="p-6 space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Экспорт данных</h1>
        <p className="text-muted-foreground">
          Экспорт результатов анализа резюме в Excel
        </p>
      </div>

      {/* Ошибки */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Успех */}
      {successMessage && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">{successMessage}</AlertDescription>
        </Alert>
      )}

      {/* Настройки экспорта */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Параметры экспорта
          </CardTitle>
          <CardDescription>
            Настройте фильтры для экспорта результатов анализа
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Выбор вакансии */}
          <div className="space-y-2">
            <Label htmlFor="vacancy">Вакансия</Label>
            <Select value={selectedVacancy} onValueChange={setSelectedVacancy}>
              <SelectTrigger id="vacancy">
                <SelectValue placeholder="Выберите вакансию" />
              </SelectTrigger>
              <SelectContent>
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
              <p className="text-sm text-muted-foreground">
                Откликов: {selectedVacancyData.applications_count} •
                Новых: {selectedVacancyData.new_applications_count}
              </p>
            )}
          </div>

          {/* Минимальный балл */}
          <div className="space-y-2">
            <Label htmlFor="min-score">Минимальный балл (опционально)</Label>
            <Select
              value={minScore?.toString() || 'all'}
              onValueChange={(value) => setMinScore(value === 'all' ? undefined : parseInt(value))}
            >
              <SelectTrigger id="min-score">
                <SelectValue placeholder="Любой балл" />
              </SelectTrigger>
              <SelectContent>
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
            <Label htmlFor="recommendation">Рекомендация (опционально)</Label>
            <Select value={recommendation} onValueChange={setRecommendation}>
              <SelectTrigger id="recommendation">
                <SelectValue placeholder="Все рекомендации" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все</SelectItem>
                <SelectItem value="hire">Только "Нанять"</SelectItem>
                <SelectItem value="interview">Только "Собеседование"</SelectItem>
                <SelectItem value="maybe">Только "Возможно"</SelectItem>
                <SelectItem value="reject">Только "Отклонить"</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Включить данные резюме */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="include-resume"
              checked={includeResumeData}
              onChange={(e) => setIncludeResumeData(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300"
            />
            <Label htmlFor="include-resume" className="text-sm font-normal cursor-pointer">
              Включить полные данные резюме (навыки, опыт, образование)
            </Label>
          </div>
        </CardContent>
      </Card>

      {/* Информация об экспорте */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5" />
            Формат экспорта
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Файл Excel будет содержать следующие данные:
            </p>
            <ul className="text-sm space-y-1 list-disc list-inside text-muted-foreground">
              <li>Имя кандидата и контактная информация</li>
              <li>Общий балл и рекомендация AI</li>
              <li>Соответствие навыков и опыта</li>
              <li>Сильные и слабые стороны</li>
              <li>Тревожные сигналы (при наличии)</li>
              <li>Обоснование рекомендации</li>
              {includeResumeData && <li>Полные данные резюме (навыки, опыт, образование)</li>}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Кнопка экспорта */}
      <Card>
        <CardContent className="pt-6">
          <Button
            onClick={handleExport}
            disabled={!selectedVacancy || isExporting || vacancies.length === 0}
            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            size="lg"
          >
            {isExporting ? (
              <>
                <Clock className="mr-2 h-5 w-5 animate-spin" />
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
            <p className="text-sm text-muted-foreground mt-3">
              Нет доступных вакансий для экспорта. Сначала синхронизируйте данные с HH.ru
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Export;
