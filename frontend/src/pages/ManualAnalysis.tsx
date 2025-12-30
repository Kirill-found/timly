/**
 * ManualAnalysis - Ручной анализ резюме без HH.ru
 *
 * Функционал:
 * 1. Создание вакансии вручную (или выбор существующей)
 * 2. Загрузка резюме (PDF, DOCX, XLSX)
 * 3. AI-анализ с прогрессом
 * 4. Просмотр результатов с детализацией
 *
 * Design: Dark Industrial - единый стиль с остальными страницами Timly
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  FileSpreadsheet,
  File,
  Trash2,
  Play,
  Square,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  Plus,
  Sparkles,
  AlertCircle,
  CheckCircle,
  Clock,
  Users,
  Target,
  Briefcase,
  DollarSign,
  Phone,
  Mail,
  ExternalLink,
  Download,
  X,
  Loader2,
  ArrowLeft,
  ArrowRight
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/services/api';
import { useApp } from '@/store/AppContext';
import { LimitExceededModal } from '@/components/LimitExceededModal';

// ==================== ТИПЫ ====================

interface ManualVacancy {
  id?: string;
  title: string;
  description?: string;  // Опционально
  key_skills: string[];
  experience_required: string;
  salary_from?: number;
  salary_to?: number;
  currency: string;
}

interface UploadedFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: 'pdf' | 'docx' | 'xlsx' | 'unknown';
  status: 'pending' | 'uploading' | 'parsing' | 'ready' | 'analyzing' | 'done' | 'error';
  progress: number;
  error?: string;
  candidateData?: ParsedCandidate;
  analysisResult?: AnalysisResult;
}

interface ParsedCandidate {
  id: string;
  full_name: string;
  title?: string;
  email?: string;
  phone?: string;
  city?: string;
  experience_years?: number;
  skills: string[];
  salary_expectation?: number;
}

interface AnalysisResult {
  id: string;
  score: number;
  recommendation: 'hire' | 'interview' | 'maybe' | 'reject';
  skills_match: number;
  experience_match: number;
  salary_match: string;
  career_trajectory: string;
  skill_gaps: string[];
  strengths: string[];
  weaknesses: string[];
  red_flags: string[];
  green_flags: string[];
  reasoning: string;
  interview_questions: string[];
}

// ==================== КОНСТАНТЫ ====================

const EXPERIENCE_OPTIONS = [
  { value: 'no_experience', label: 'Без опыта' },
  { value: '1-3', label: '1-3 года' },
  { value: '3-6', label: '3-6 лет' },
  { value: '6+', label: '6+ лет' },
];

const SUGGESTED_SKILLS: Record<string, string[]> = {
  'developer': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git', 'Docker', 'REST API'],
  'designer': ['Figma', 'Photoshop', 'UI/UX', 'Prototyping', 'Design Systems', 'User Research'],
  'manager': ['Agile', 'Scrum', 'Jira', 'Leadership', 'Communication', 'Analytics', 'Presentation'],
  'marketing': ['SEO', 'SMM', 'Google Analytics', 'Content Marketing', 'CRM', 'Email Marketing'],
  'sales': ['CRM', 'B2B', 'Negotiation', 'Cold Calling', 'Pipeline Management', 'Presentations'],
  'hr': ['Recruiting', 'Interviewing', 'Onboarding', 'HR Systems', 'Employer Branding'],
  'analyst': ['SQL', 'Python', 'Excel', 'Power BI', 'Tableau', 'Data Visualization', 'Statistics'],
  'default': ['Communication', 'Teamwork', 'Problem Solving', 'Time Management'],
};

// ==================== ХЕЛПЕРЫ ====================

const getFileIcon = (type: string) => {
  switch (type) {
    case 'pdf': return <FileText className="w-5 h-5 text-red-400" />;
    case 'docx': return <FileText className="w-5 h-5 text-blue-400" />;
    case 'xlsx': return <FileSpreadsheet className="w-5 h-5 text-green-400" />;
    default: return <File className="w-5 h-5 text-zinc-400" />;
  }
};

const getFileType = (filename: string): 'pdf' | 'docx' | 'xlsx' | 'unknown' => {
  const ext = filename.toLowerCase().split('.').pop();
  if (ext === 'pdf') return 'pdf';
  if (ext === 'docx' || ext === 'doc') return 'docx';
  if (ext === 'xlsx' || ext === 'xls') return 'xlsx';
  return 'unknown';
};

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const getRecommendationStyle = (rec?: string) => {
  switch (rec) {
    case 'hire': return 'status-hire';
    case 'interview': return 'status-interview';
    case 'maybe': return 'status-maybe';
    case 'reject': return 'status-reject';
    default: return 'bg-zinc-800 text-zinc-400';
  }
};

const getRecommendationText = (rec?: string) => {
  switch (rec) {
    case 'hire': return 'Нанять';
    case 'interview': return 'Собеседование';
    case 'maybe': return 'Возможно';
    case 'reject': return 'Отклонить';
    default: return '—';
  }
};

// ==================== КОМПОНЕНТ ====================

const ManualAnalysis: React.FC = () => {
  // Состояние шагов
  const [currentStep, setCurrentStep] = useState<'vacancy' | 'upload' | 'analysis' | 'results'>('vacancy');

  // Вакансия
  const [vacancy, setVacancy] = useState<ManualVacancy>({
    title: '',
    key_skills: [],
    experience_required: '1-3',
    salary_from: undefined,
    salary_to: undefined,
    currency: 'RUB',
  });
  const [skillInput, setSkillInput] = useState('');
  const [suggestedSkills, setSuggestedSkills] = useState<string[]>([]);

  // Файлы
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Анализ
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState({ current: 0, total: 0 });

  // UI
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [limitModalOpen, setLimitModalOpen] = useState(false);
  const [limitExceededInfo, setLimitExceededInfo] = useState<any>(null);

  // Лимиты
  const [limits, setLimits] = useState<any>(null);

  const app = useApp();

  // ==================== ЭФФЕКТЫ ====================

  useEffect(() => {
    loadLimits();
  }, []);

  // Подсказки навыков на основе названия вакансии
  useEffect(() => {
    const title = vacancy.title.toLowerCase();
    let skills: string[] = SUGGESTED_SKILLS.default;

    if (title.includes('develop') || title.includes('разработ') || title.includes('программ')) {
      skills = SUGGESTED_SKILLS.developer;
    } else if (title.includes('design') || title.includes('дизайн')) {
      skills = SUGGESTED_SKILLS.designer;
    } else if (title.includes('manager') || title.includes('менеджер') || title.includes('руковод')) {
      skills = SUGGESTED_SKILLS.manager;
    } else if (title.includes('marketing') || title.includes('маркет')) {
      skills = SUGGESTED_SKILLS.marketing;
    } else if (title.includes('sales') || title.includes('продаж')) {
      skills = SUGGESTED_SKILLS.sales;
    } else if (title.includes('hr') || title.includes('рекрут')) {
      skills = SUGGESTED_SKILLS.hr;
    } else if (title.includes('analyst') || title.includes('аналит')) {
      skills = SUGGESTED_SKILLS.analyst;
    }

    // Фильтруем уже добавленные
    setSuggestedSkills(skills.filter(s => !vacancy.key_skills.includes(s)));
  }, [vacancy.title, vacancy.key_skills]);

  // ==================== API ====================

  const loadLimits = async () => {
    try {
      const data = await apiClient.checkLimits();
      setLimits(data);
    } catch (err) {
      console.error('Error loading limits:', err);
    }
  };

  const uploadAndParseFile = async (uploadedFile: UploadedFile): Promise<ParsedCandidate | null> => {
    try {
      // Обновляем статус на uploading
      setFiles(prev => prev.map(f =>
        f.id === uploadedFile.id ? { ...f, status: 'uploading', progress: 30 } : f
      ));

      const formData = new FormData();
      formData.append('file', uploadedFile.file);
      formData.append('vacancy_id', vacancy.id || 'temp');

      // Определяем эндпоинт по типу файла
      const endpoint = uploadedFile.type === 'pdf'
        ? '/api/manual-analysis/parse/pdf'
        : uploadedFile.type === 'xlsx'
          ? '/api/manual-analysis/parse/excel'
          : '/api/manual-analysis/parse/document';

      // Парсинг
      setFiles(prev => prev.map(f =>
        f.id === uploadedFile.id ? { ...f, status: 'parsing', progress: 60 } : f
      ));

      const response = await apiClient.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Готово к анализу
      setFiles(prev => prev.map(f =>
        f.id === uploadedFile.id
          ? { ...f, status: 'ready', progress: 100, candidateData: response.data }
          : f
      ));

      return response.data;
    } catch (err: any) {
      setFiles(prev => prev.map(f =>
        f.id === uploadedFile.id
          ? { ...f, status: 'error', error: err.response?.data?.detail || 'Ошибка парсинга' }
          : f
      ));
      return null;
    }
  };

  const analyzeCandidate = async (file: UploadedFile): Promise<AnalysisResult | null> => {
    if (!file.candidateData) return null;

    try {
      setFiles(prev => prev.map(f =>
        f.id === file.id ? { ...f, status: 'analyzing' } : f
      ));

      const response = await apiClient.post('/api/manual-analysis/analyze', {
        vacancy: vacancy,
        candidate: file.candidateData,
      });

      setFiles(prev => prev.map(f =>
        f.id === file.id
          ? { ...f, status: 'done', analysisResult: response.data }
          : f
      ));

      return response.data;
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail;

      if (errorDetail?.error === 'LIMIT_EXCEEDED') {
        setLimitExceededInfo(errorDetail.subscription);
        setLimitModalOpen(true);
      }

      setFiles(prev => prev.map(f =>
        f.id === file.id
          ? { ...f, status: 'error', error: errorDetail?.message || 'Ошибка анализа' }
          : f
      ));
      return null;
    }
  };

  const runFullAnalysis = async () => {
    const readyFiles = files.filter(f => f.status === 'ready' && f.candidateData);

    if (readyFiles.length === 0) {
      setError('Нет резюме готовых к анализу');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisProgress({ current: 0, total: readyFiles.length });
    setError(null);
    setCurrentStep('analysis');

    for (let i = 0; i < readyFiles.length; i++) {
      const result = await analyzeCandidate(readyFiles[i]);
      setAnalysisProgress({ current: i + 1, total: readyFiles.length });

      if (!result && limitModalOpen) {
        // Лимит превышен - останавливаем
        break;
      }
    }

    setIsAnalyzing(false);
    await loadLimits();
    setCurrentStep('results');
  };

  const downloadExcel = async () => {
    try {
      const analyzedFiles = files.filter(f => f.status === 'done' && f.analysisResult);

      const response = await apiClient.post('/api/manual-analysis/export/excel', {
        vacancy: vacancy,
        results: analyzedFiles.map(f => ({
          candidate: f.candidateData,
          analysis: f.analysisResult,
        })),
      }, { responseType: 'blob' });

      const url = window.URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `manual_analysis_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError('Ошибка экспорта');
    }
  };

  // ==================== ОБРАБОТЧИКИ ====================

  const handleAddSkill = (skill: string) => {
    if (skill.trim() && !vacancy.key_skills.includes(skill.trim())) {
      setVacancy(prev => ({
        ...prev,
        key_skills: [...prev.key_skills, skill.trim()],
      }));
    }
    setSkillInput('');
  };

  const handleRemoveSkill = (skill: string) => {
    setVacancy(prev => ({
      ...prev,
      key_skills: prev.key_skills.filter(s => s !== skill),
    }));
  };

  const handleSkillKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddSkill(skillInput);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(Array.from(e.target.files));
    }
  };

  const addFiles = async (newFiles: File[]) => {
    const validFiles = newFiles.filter(f => {
      const type = getFileType(f.name);
      return type !== 'unknown';
    });

    if (validFiles.length < newFiles.length) {
      setError(`Некоторые файлы не поддерживаются. Разрешены: PDF, DOCX, XLSX`);
    }

    const uploadedFiles: UploadedFile[] = validFiles.map(f => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file: f,
      name: f.name,
      size: f.size,
      type: getFileType(f.name),
      status: 'pending',
      progress: 0,
    }));

    setFiles(prev => [...prev, ...uploadedFiles]);

    // Автоматический парсинг
    for (const file of uploadedFiles) {
      await uploadAndParseFile(file);
    }
  };

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
    if (e.dataTransfer.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  }, []);

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const toggleExpanded = (id: string) => {
    setExpandedResults(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) newSet.delete(id);
      else newSet.add(id);
      return newSet;
    });
  };

  const canProceedToUpload = vacancy.title.trim() && vacancy.key_skills.length > 0;
  const canStartAnalysis = files.filter(f => f.status === 'ready').length > 0;
  const analyzedCount = files.filter(f => f.status === 'done').length;

  // ==================== АНИМАЦИИ ====================

  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  };

  const stagger = {
    animate: { transition: { staggerChildren: 0.05 } }
  };

  // ==================== РЕНДЕР ====================

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <motion.div {...fadeIn} className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">Ручной анализ</h1>
          <p className="text-sm text-zinc-500 mt-1">
            Загрузите резюме и получите AI-оценку без привязки к HH.ru
          </p>
        </div>

        {/* Лимиты */}
        {limits && !limits.is_unlimited && (
          <div className="text-right">
            <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
              Анализов осталось
            </div>
            <div className="text-2xl font-semibold tabular-nums">
              {limits.analyses_remaining}
              <span className="text-sm text-zinc-500 font-normal">/{limits.analyses_limit}</span>
            </div>
          </div>
        )}
      </motion.div>

      {/* Progress Steps */}
      <motion.div {...fadeIn} className="flex items-center gap-2">
        {[
          { key: 'vacancy', label: 'Вакансия', icon: Briefcase },
          { key: 'upload', label: 'Резюме', icon: Upload },
          { key: 'analysis', label: 'Анализ', icon: Sparkles },
          { key: 'results', label: 'Результаты', icon: Target },
        ].map((step, idx) => {
          const Icon = step.icon;
          const isActive = currentStep === step.key;
          const isPast = ['vacancy', 'upload', 'analysis', 'results'].indexOf(currentStep) > idx;

          return (
            <React.Fragment key={step.key}>
              <button
                onClick={() => {
                  if (isPast || isActive) setCurrentStep(step.key as any);
                }}
                disabled={!isPast && !isActive}
                className={`
                  flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all
                  ${isActive
                    ? 'bg-zinc-800 text-zinc-100'
                    : isPast
                      ? 'text-zinc-400 hover:text-zinc-200 cursor-pointer'
                      : 'text-zinc-600 cursor-not-allowed'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{step.label}</span>
              </button>
              {idx < 3 && (
                <ChevronRight className={`w-4 h-4 ${isPast ? 'text-zinc-500' : 'text-zinc-700'}`} />
              )}
            </React.Fragment>
          );
        })}
      </motion.div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
            <button onClick={() => setError(null)} className="ml-auto">
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ==================== ШАГ 1: ВАКАНСИЯ ==================== */}
      <AnimatePresence mode="wait">
        {currentStep === 'vacancy' && (
          <motion.div
            key="vacancy"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader>
                <CardTitle className="text-[13px] font-medium uppercase tracking-wide flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-zinc-500" />
                  Опишите вакансию
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-5">
                {/* Название */}
                <div className="space-y-2">
                  <Label className="text-zinc-400">Название должности *</Label>
                  <Input
                    value={vacancy.title}
                    onChange={(e) => setVacancy(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Например: Senior Python Developer"
                    className="h-11 bg-zinc-900 border-zinc-800 focus:border-zinc-700"
                  />
                </div>

                {/* Описание */}
                <div className="space-y-2">
                  <Label className="text-zinc-400">Описание вакансии</Label>
                  <Textarea
                    value={vacancy.description || ''}
                    onChange={(e) => setVacancy(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Опишите обязанности, требования и условия работы..."
                    rows={4}
                    className="bg-zinc-900 border-zinc-800 focus:border-zinc-700 resize-none"
                  />
                </div>

                {/* Навыки */}
                <div className="space-y-2">
                  <Label className="text-zinc-400">Ключевые навыки</Label>

                  {/* Добавленные навыки */}
                  {vacancy.key_skills.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {vacancy.key_skills.map(skill => (
                        <span
                          key={skill}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-zinc-800 text-zinc-300 text-sm"
                        >
                          {skill}
                          <button
                            onClick={() => handleRemoveSkill(skill)}
                            className="text-zinc-500 hover:text-zinc-300"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Поле ввода */}
                  <Input
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyDown={handleSkillKeyDown}
                    placeholder="Введите навык и нажмите Enter"
                    className="h-10 bg-zinc-900 border-zinc-800 focus:border-zinc-700"
                  />

                  {/* Подсказки */}
                  {suggestedSkills.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {suggestedSkills.slice(0, 8).map(skill => (
                        <button
                          key={skill}
                          onClick={() => handleAddSkill(skill)}
                          className="px-2 py-1 rounded text-xs bg-zinc-900 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 border border-zinc-800 transition-colors"
                        >
                          + {skill}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Опыт и Зарплата */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label className="text-zinc-400">Требуемый опыт</Label>
                    <Select
                      value={vacancy.experience_required}
                      onValueChange={(v) => setVacancy(prev => ({ ...prev, experience_required: v }))}
                    >
                      <SelectTrigger className="h-10 bg-zinc-900 border-zinc-800">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-zinc-900 border-zinc-800">
                        {EXPERIENCE_OPTIONS.map(opt => (
                          <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-zinc-400">Зарплата от</Label>
                    <Input
                      type="number"
                      value={vacancy.salary_from || ''}
                      onChange={(e) => setVacancy(prev => ({ ...prev, salary_from: e.target.value ? Number(e.target.value) : undefined }))}
                      placeholder="100 000"
                      className="h-10 bg-zinc-900 border-zinc-800"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="text-zinc-400">Зарплата до</Label>
                    <Input
                      type="number"
                      value={vacancy.salary_to || ''}
                      onChange={(e) => setVacancy(prev => ({ ...prev, salary_to: e.target.value ? Number(e.target.value) : undefined }))}
                      placeholder="200 000"
                      className="h-10 bg-zinc-900 border-zinc-800"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Кнопка далее */}
            <div className="flex justify-end">
              <Button
                onClick={() => setCurrentStep('upload')}
                disabled={!canProceedToUpload}
                className="h-11 px-6 bg-zinc-100 text-zinc-900 hover:bg-white font-medium"
              >
                Далее: Загрузить резюме
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </motion.div>
        )}

        {/* ==================== ШАГ 2: ЗАГРУЗКА РЕЗЮМЕ ==================== */}
        {currentStep === 'upload' && (
          <motion.div
            key="upload"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-6"
          >
            {/* Информация о вакансии */}
            <Card className="bg-zinc-900/50">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
                    <Briefcase className="w-5 h-5 text-zinc-400" />
                  </div>
                  <div>
                    <div className="font-medium text-zinc-200">{vacancy.title}</div>
                    <div className="text-xs text-zinc-500">
                      {vacancy.key_skills.slice(0, 4).join(', ')}
                      {vacancy.key_skills.length > 4 && ` +${vacancy.key_skills.length - 4}`}
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setCurrentStep('vacancy')}
                  className="text-zinc-400 hover:text-zinc-200"
                >
                  Изменить
                </Button>
              </CardContent>
            </Card>

            {/* Зона загрузки */}
            <Card>
              <CardHeader>
                <CardTitle className="text-[13px] font-medium uppercase tracking-wide flex items-center gap-2">
                  <Upload className="w-4 h-4 text-zinc-500" />
                  Загрузите резюме
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Drop zone */}
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`
                    relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
                    transition-all duration-200
                    ${isDragging
                      ? 'border-zinc-500 bg-zinc-800/50'
                      : 'border-zinc-800 hover:border-zinc-700 hover:bg-zinc-900/50'
                    }
                  `}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.xlsx,.xls"
                    onChange={handleFileSelect}
                    className="hidden"
                  />

                  <div className="flex flex-col items-center">
                    <div className={`
                      w-16 h-16 rounded-2xl flex items-center justify-center mb-4
                      ${isDragging ? 'bg-zinc-700' : 'bg-zinc-800'}
                    `}>
                      <Upload className={`w-8 h-8 ${isDragging ? 'text-zinc-300' : 'text-zinc-500'}`} />
                    </div>
                    <div className="text-zinc-300 font-medium mb-1">
                      {isDragging ? 'Отпустите файлы' : 'Перетащите файлы или нажмите'}
                    </div>
                    <div className="text-sm text-zinc-500">
                      PDF, DOCX, XLSX • до 50 файлов
                    </div>
                  </div>
                </div>

                {/* Список файлов */}
                {files.length > 0 && (
                  <div className="mt-6 space-y-2">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm text-zinc-400">
                        Загружено: {files.length} файл(ов)
                      </span>
                      <span className="text-sm text-zinc-500">
                        Готово к анализу: {files.filter(f => f.status === 'ready').length}
                      </span>
                    </div>

                    <motion.div variants={stagger} initial="initial" animate="animate" className="space-y-2">
                      {files.map((file) => (
                        <motion.div
                          key={file.id}
                          variants={fadeIn}
                          className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900 border border-zinc-800"
                        >
                          {getFileIcon(file.type)}

                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-zinc-200 truncate">
                                {file.name}
                              </span>
                              <span className="text-xs text-zinc-600">
                                {formatFileSize(file.size)}
                              </span>
                            </div>

                            {/* Статус */}
                            <div className="mt-1">
                              {file.status === 'pending' && (
                                <span className="text-xs text-zinc-500">Ожидание...</span>
                              )}
                              {file.status === 'uploading' && (
                                <div className="flex items-center gap-2">
                                  <Loader2 className="w-3 h-3 animate-spin text-zinc-400" />
                                  <span className="text-xs text-zinc-400">Загрузка...</span>
                                </div>
                              )}
                              {file.status === 'parsing' && (
                                <div className="flex items-center gap-2">
                                  <Loader2 className="w-3 h-3 animate-spin text-blue-400" />
                                  <span className="text-xs text-blue-400">Парсинг резюме...</span>
                                </div>
                              )}
                              {file.status === 'ready' && file.candidateData && (
                                <div className="flex items-center gap-2">
                                  <CheckCircle className="w-3 h-3 text-green-500" />
                                  <span className="text-xs text-green-500">
                                    {file.candidateData.full_name || 'Готово к анализу'}
                                  </span>
                                </div>
                              )}
                              {file.status === 'analyzing' && (
                                <div className="flex items-center gap-2">
                                  <Sparkles className="w-3 h-3 text-amber-400 animate-pulse" />
                                  <span className="text-xs text-amber-400">AI анализ...</span>
                                </div>
                              )}
                              {file.status === 'done' && file.analysisResult && (
                                <div className="flex items-center gap-2">
                                  <CheckCircle className="w-3 h-3 text-green-500" />
                                  <span className="text-xs text-zinc-400">
                                    {file.candidateData?.full_name} —
                                  </span>
                                  <span className={`text-xs px-1.5 py-0.5 rounded ${getRecommendationStyle(file.analysisResult.recommendation)}`}>
                                    {file.analysisResult.score} баллов
                                  </span>
                                </div>
                              )}
                              {file.status === 'error' && (
                                <div className="flex items-center gap-2">
                                  <AlertCircle className="w-3 h-3 text-red-500" />
                                  <span className="text-xs text-red-400">{file.error}</span>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Кнопка удаления */}
                          <button
                            onClick={() => removeFile(file.id)}
                            className="p-1.5 text-zinc-600 hover:text-zinc-400 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </motion.div>
                      ))}
                    </motion.div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Кнопки навигации */}
            <div className="flex justify-between">
              <Button
                variant="ghost"
                onClick={() => setCurrentStep('vacancy')}
                className="text-zinc-400 hover:text-zinc-200"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Назад
              </Button>

              <Button
                onClick={runFullAnalysis}
                disabled={!canStartAnalysis}
                className="h-11 px-6 bg-zinc-100 text-zinc-900 hover:bg-white font-medium"
              >
                <Play className="w-4 h-4 mr-2" />
                Запустить анализ ({files.filter(f => f.status === 'ready').length})
              </Button>
            </div>
          </motion.div>
        )}

        {/* ==================== ШАГ 3: АНАЛИЗ ==================== */}
        {currentStep === 'analysis' && (
          <motion.div
            key="analysis"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-6"
          >
            <Card>
              <CardContent className="p-8">
                <div className="text-center space-y-6">
                  {/* Анимированная иконка */}
                  <div className="w-20 h-20 rounded-2xl bg-zinc-800 flex items-center justify-center mx-auto">
                    <Sparkles className="w-10 h-10 text-amber-400 animate-pulse" />
                  </div>

                  <div>
                    <h2 className="text-xl font-semibold text-zinc-100 mb-2">
                      {isAnalyzing ? 'Анализ резюме' : 'Анализ завершён'}
                    </h2>
                    <p className="text-zinc-500">
                      {isAnalyzing
                        ? `Обработано ${analysisProgress.current} из ${analysisProgress.total}`
                        : `Проанализировано ${analyzedCount} резюме`
                      }
                    </p>
                  </div>

                  {/* Прогресс */}
                  {isAnalyzing && (
                    <div className="max-w-md mx-auto space-y-3">
                      <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{
                            width: `${analysisProgress.total > 0
                              ? (analysisProgress.current / analysisProgress.total) * 100
                              : 0}%`
                          }}
                          className="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full"
                        />
                      </div>
                      <div className="text-2xl font-semibold tabular-nums">
                        {analysisProgress.total > 0
                          ? Math.round((analysisProgress.current / analysisProgress.total) * 100)
                          : 0}%
                      </div>
                    </div>
                  )}

                  {/* Текущий файл */}
                  {isAnalyzing && (
                    <div className="text-sm text-zinc-500">
                      {files.find(f => f.status === 'analyzing')?.name || 'Подготовка...'}
                    </div>
                  )}

                  {/* Кнопки */}
                  {!isAnalyzing && (
                    <Button
                      onClick={() => setCurrentStep('results')}
                      className="h-11 px-6 bg-zinc-100 text-zinc-900 hover:bg-white font-medium"
                    >
                      Смотреть результаты
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* ==================== ШАГ 4: РЕЗУЛЬТАТЫ ==================== */}
        {currentStep === 'results' && (
          <motion.div
            key="results"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-6"
          >
            {/* Статистика */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-zinc-800 border border-zinc-800 rounded-lg overflow-hidden">
              {[
                { label: 'Всего', value: files.filter(f => f.status === 'done').length, color: '' },
                {
                  label: 'Нанять',
                  value: files.filter(f => f.analysisResult?.recommendation === 'hire').length,
                  color: 'text-green-500'
                },
                {
                  label: 'Собеседование',
                  value: files.filter(f => f.analysisResult?.recommendation === 'interview').length,
                  color: 'text-blue-500'
                },
                {
                  label: 'Возможно',
                  value: files.filter(f => f.analysisResult?.recommendation === 'maybe').length,
                  color: 'text-amber-500'
                },
              ].map(stat => (
                <div key={stat.label} className="bg-card p-4 text-center">
                  <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-1">
                    {stat.label}
                  </div>
                  <div className={`text-2xl font-semibold tabular-nums ${stat.color}`}>
                    {stat.value}
                  </div>
                </div>
              ))}
            </div>

            {/* Действия */}
            <div className="flex items-center justify-between">
              <Button
                variant="ghost"
                onClick={() => {
                  setFiles([]);
                  setCurrentStep('vacancy');
                }}
                className="text-zinc-400 hover:text-zinc-200"
              >
                <Plus className="w-4 h-4 mr-2" />
                Новый анализ
              </Button>

              <Button
                onClick={downloadExcel}
                disabled={analyzedCount === 0}
                variant="outline"
                className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
              >
                <Download className="w-4 h-4 mr-2" />
                Скачать Excel
              </Button>
            </div>

            {/* Список результатов */}
            <Card>
              <CardHeader className="pb-0">
                <CardTitle className="text-[13px] font-medium uppercase tracking-wide">
                  Результаты анализа
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4 px-0">
                {files.filter(f => f.status === 'done').length === 0 ? (
                  <div className="p-12 text-center text-zinc-500">
                    Нет результатов
                  </div>
                ) : (
                  <div>
                    {files
                      .filter(f => f.status === 'done' && f.analysisResult)
                      .sort((a, b) => (b.analysisResult?.score || 0) - (a.analysisResult?.score || 0))
                      .map((file) => {
                        const r = file.analysisResult!;
                        const c = file.candidateData!;

                        return (
                          <div key={file.id} className="border-b border-zinc-800/50 last:border-b-0">
                            {/* Row */}
                            <div
                              className="px-5 py-4 flex items-center gap-4 cursor-pointer hover:bg-zinc-900/50 transition-colors"
                              onClick={() => toggleExpanded(file.id)}
                            >
                              {/* Avatar */}
                              <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-[12px] font-medium text-zinc-400 flex-shrink-0">
                                {c.full_name?.split(' ').map(n => n[0]).join('').slice(0, 2) || '??'}
                              </div>

                              {/* Info */}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium text-zinc-200 truncate">
                                    {c.full_name || 'Без имени'}
                                  </span>
                                </div>
                                <div className="text-xs text-zinc-500 mt-0.5 truncate">
                                  {c.title || 'Должность не указана'}
                                </div>
                              </div>

                              {/* Score */}
                              <div className="text-right mr-2">
                                <div className="text-xl font-semibold tabular-nums">{r.score}</div>
                                <div className="text-[10px] text-zinc-500">баллов</div>
                              </div>

                              {/* Status */}
                              <span className={`px-2.5 py-1 rounded text-[11px] font-medium ${getRecommendationStyle(r.recommendation)}`}>
                                {getRecommendationText(r.recommendation)}
                              </span>

                              {/* Chevron */}
                              {expandedResults.has(file.id) ? (
                                <ChevronUp className="w-4 h-4 text-zinc-500" />
                              ) : (
                                <ChevronDown className="w-4 h-4 text-zinc-500" />
                              )}
                            </div>

                            {/* Expanded details */}
                            <AnimatePresence>
                              {expandedResults.has(file.id) && (
                                <motion.div
                                  initial={{ height: 0, opacity: 0 }}
                                  animate={{ height: 'auto', opacity: 1 }}
                                  exit={{ height: 0, opacity: 0 }}
                                  className="overflow-hidden"
                                >
                                  <div className="px-5 pb-5 pt-2 ml-[56px] space-y-4">
                                    {/* Контакты */}
                                    {(c.email || c.phone || c.city) && (
                                      <div className="flex flex-wrap gap-4 text-sm text-zinc-400">
                                        {c.email && (
                                          <div className="flex items-center gap-1.5">
                                            <Mail className="w-3.5 h-3.5" />
                                            {c.email}
                                          </div>
                                        )}
                                        {c.phone && (
                                          <div className="flex items-center gap-1.5">
                                            <Phone className="w-3.5 h-3.5" />
                                            {c.phone}
                                          </div>
                                        )}
                                      </div>
                                    )}

                                    {/* Метрики */}
                                    <div className="grid grid-cols-3 gap-3">
                                      <div className="p-3 rounded-lg bg-zinc-800/50">
                                        <div className="text-[11px] text-zinc-500 mb-1">Навыки</div>
                                        <div className="flex items-center gap-2">
                                          <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                                            <div
                                              className="h-full bg-green-500 rounded-full"
                                              style={{ width: `${r.skills_match}%` }}
                                            />
                                          </div>
                                          <span className="text-sm font-medium tabular-nums">{r.skills_match}%</span>
                                        </div>
                                      </div>
                                      <div className="p-3 rounded-lg bg-zinc-800/50">
                                        <div className="text-[11px] text-zinc-500 mb-1">Опыт</div>
                                        <div className="flex items-center gap-2">
                                          <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                                            <div
                                              className="h-full bg-blue-500 rounded-full"
                                              style={{ width: `${r.experience_match}%` }}
                                            />
                                          </div>
                                          <span className="text-sm font-medium tabular-nums">{r.experience_match}%</span>
                                        </div>
                                      </div>
                                      <div className="p-3 rounded-lg bg-zinc-800/50">
                                        <div className="text-[11px] text-zinc-500 mb-1">Карьера</div>
                                        <div className="text-sm font-medium">
                                          {r.career_trajectory === 'growth' ? 'Рост' :
                                           r.career_trajectory === 'stable' ? 'Стабильно' :
                                           r.career_trajectory === 'decline' ? 'Спад' : '—'}
                                        </div>
                                      </div>
                                    </div>

                                    {/* Skill Gaps */}
                                    {r.skill_gaps && r.skill_gaps.length > 0 && (
                                      <div>
                                        <div className="text-[11px] text-amber-500 mb-2">Недостающие навыки</div>
                                        <div className="flex flex-wrap gap-1.5">
                                          {r.skill_gaps.map((skill, i) => (
                                            <span key={i} className="px-2 py-0.5 text-xs bg-amber-500/10 text-amber-400 rounded">
                                              {skill}
                                            </span>
                                          ))}
                                        </div>
                                      </div>
                                    )}

                                    {/* Сильные/слабые стороны */}
                                    <div className="grid grid-cols-2 gap-4">
                                      {r.strengths && r.strengths.length > 0 && (
                                        <div>
                                          <div className="text-[11px] text-green-500 mb-2">Сильные стороны</div>
                                          <ul className="space-y-1">
                                            {r.strengths.map((s, i) => (
                                              <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
                                                <span className="text-green-500 mt-1">•</span>
                                                {s}
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                      {r.weaknesses && r.weaknesses.length > 0 && (
                                        <div>
                                          <div className="text-[11px] text-red-500 mb-2">Слабые стороны</div>
                                          <ul className="space-y-1">
                                            {r.weaknesses.map((w, i) => (
                                              <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
                                                <span className="text-red-500 mt-1">•</span>
                                                {w}
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                    </div>

                                    {/* Вопросы для интервью */}
                                    {r.interview_questions && r.interview_questions.length > 0 && (
                                      <div className="p-4 rounded-lg bg-zinc-800/30 border border-zinc-700/50">
                                        <div className="text-[11px] text-zinc-500 mb-3">Вопросы для интервью</div>
                                        <ol className="space-y-2">
                                          {r.interview_questions.map((q, i) => (
                                            <li key={i} className="text-sm text-zinc-300 flex gap-2">
                                              <span className="text-zinc-500 font-medium">{i + 1}.</span>
                                              {q}
                                            </li>
                                          ))}
                                        </ol>
                                      </div>
                                    )}

                                    {/* Обоснование */}
                                    {r.reasoning && (
                                      <div className="p-4 rounded-lg bg-zinc-800/30 border border-zinc-700/50">
                                        <div className="text-[11px] text-zinc-500 mb-2">Обоснование AI</div>
                                        <p className="text-sm text-zinc-300 leading-relaxed">
                                          {r.reasoning}
                                        </p>
                                      </div>
                                    )}
                                  </div>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        );
                      })}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modals */}
      <LimitExceededModal
        isOpen={limitModalOpen}
        onClose={() => setLimitModalOpen(false)}
        subscriptionInfo={limitExceededInfo}
      />
    </div>
  );
};

export default ManualAnalysis;
