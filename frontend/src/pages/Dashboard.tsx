/**
 * Dashboard - Soft UI Light Theme (Adon-style)
 */
import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  RefreshCw,
  Settings,
  ArrowRight,
  Users,
  Briefcase,
  Star,
  ChevronRight,
  Play,
  Download,
  Zap,
  TrendingUp,
  Clock,
  DollarSign,
} from 'lucide-react';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { useAuth } from '@/store/AuthContext';
import { useApp } from '@/store/AppContext';
import { apiClient } from '@/services/api';

interface DashboardStats {
  total_analyses: number;
  analyses_this_month: number;
  avg_score: number;
  top_candidates_count: number;
  total_cost_cents: number;
  cost_this_month_cents: number;
  analyses_limit?: number;
  recent_analyses: Array<{
    vacancy_title: string;
    candidate_name: string;
    score: number;
    recommendation: string;
    analyzed_at: string;
    one_liner?: string;
  }>;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { activeSyncJobs, vacancies: contextVacancies } = useApp();
  const navigate = useNavigate();
  const vacancies = Array.isArray(contextVacancies) ? contextVacancies : [];

  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const loadDashboardStats = async () => {
      try {
        setStatsLoading(true);
        const response = await apiClient.getDashboardStats();
        setDashboardStats(response);
      } catch (error) {
        console.error('Dashboard stats error:', error);
      } finally {
        setStatsLoading(false);
      }
    };

    if (user?.has_hh_token) {
      loadDashboardStats();
    } else {
      setStatsLoading(false);
    }
  }, [user]);

  const getRecommendationStyle = (recommendation: string) => {
    switch (recommendation) {
      case 'hire': return 'text-green-600';
      case 'interview': return 'text-teal-600';
      case 'maybe': return 'text-amber-600';
      case 'reject': return 'text-red-500';
      default: return 'text-muted-foreground';
    }
  };

  const getRecommendationText = (recommendation: string) => {
    switch (recommendation) {
      case 'hire': return 'Рекомендую';
      case 'interview': return 'Рассмотреть';
      case 'maybe': return 'Сомнительно';
      case 'reject': return 'Не подходит';
      default: return recommendation;
    }
  };

  const getPriorityStars = (score: number) => {
    if (score >= 80) return 3;
    if (score >= 60) return 2;
    return 1;
  };

  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  };

  const topCandidates = dashboardStats?.recent_analyses
    ?.filter(a => a.recommendation === 'hire' || a.recommendation === 'interview')
    ?.slice(0, 5) || [];

  const getVacancyTopCount = (vacancyTitle: string) => {
    return dashboardStats?.recent_analyses?.filter(
      a => a.vacancy_title === vacancyTitle && (a.recommendation === 'hire' || a.recommendation === 'interview')
    ).length || 0;
  };

  if (!user?.has_hh_token) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center p-6">
        <motion.div {...fadeIn} className="max-w-md w-full">
          <Card className="border-dashed border-border">
            <CardContent className="pt-8 pb-8 text-center">
              <div className="w-14 h-14 rounded-lg bg-muted border border-border flex items-center justify-center mx-auto mb-6">
                <Settings className="h-6 w-6 text-muted-foreground" />
              </div>
              <h2 className="text-xl font-semibold mb-2">Настройте интеграцию</h2>
              <p className="text-muted-foreground mb-6 text-sm">
                Подключите HH.ru чтобы получать отклики и анализировать резюме
              </p>
              <Button asChild>
                <Link to="/settings">
                  Подключить HH.ru
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  if (statsLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-24 bg-muted rounded-lg" />
          ))}
        </div>
        <Skeleton className="h-48 bg-muted rounded-lg" />
        <Skeleton className="h-64 bg-muted rounded-lg" />
      </div>
    );
  }

  const totalApplications = vacancies.reduce((sum, v) => sum + (v.applications_count || 0), 0);
  const usagePercent = dashboardStats?.analyses_limit
    ? Math.round((dashboardStats.analyses_this_month / dashboardStats.analyses_limit) * 100)
    : 0;

  return (
    <div className="p-6 space-y-6">
      {activeSyncJobs.length > 0 && (
        <Alert className="border-blue-200 bg-blue-50">
          <RefreshCw className="h-4 w-4 animate-spin text-blue-600" />
          <AlertDescription className="ml-2 text-foreground">
            <span className="font-medium text-foreground">Синхронизация</span>
            <span className="text-muted-foreground"> — активных задач: {activeSyncJobs.length}</span>
            <Link to="/sync" className="ml-2 text-blue-600 hover:text-blue-600">
              Подробнее →
            </Link>
          </AlertDescription>
        </Alert>
      )}

      {/* Quick Stats - 3 карточки */}
      <motion.div {...fadeIn} className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-lg p-5 hover:border-muted-foreground/30 transition-colors">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
              <Briefcase className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Вакансии</div>
          </div>
          <div className="text-3xl font-semibold tracking-tight">{vacancies.length}</div>
          <div className="text-xs text-muted-foreground mt-1">активных позиций</div>
        </div>

        <div className="bg-card border border-border rounded-lg p-5 hover:border-muted-foreground/30 transition-colors">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
              <Users className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Отклики</div>
          </div>
          <div className="text-3xl font-semibold tracking-tight">{totalApplications}</div>
          <div className="text-xs text-muted-foreground mt-1">всего кандидатов</div>
        </div>

        <div className="bg-card border border-border rounded-lg p-5 hover:border-muted-foreground/30 transition-colors">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <Star className="h-5 w-5 text-green-600" />
            </div>
            <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Топ кандидаты</div>
          </div>
          <div className="text-3xl font-semibold tracking-tight text-green-600">
            {dashboardStats?.top_candidates_count || 0}
          </div>
          <div className="text-xs text-muted-foreground mt-1">рекомендованы к найму</div>
        </div>
      </motion.div>

      {/* Вакансии с топ-кандидатами */}
      {vacancies.length > 0 && (
        <motion.div {...fadeIn}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-[13px] font-medium uppercase tracking-wide text-muted-foreground">Ваши вакансии</h2>
            <Link to="/sync" className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1">
              Синхронизировать <ChevronRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {vacancies.slice(0, 6).map((vacancy) => {
              const topCount = getVacancyTopCount(vacancy.title);
              return (
                <button
                  key={vacancy.id}
                  onClick={() => navigate('/analysis?vacancy=' + vacancy.id)}
                  className="bg-card border border-border rounded-lg p-4 text-left hover:border-muted-foreground/30 hover:bg-muted transition-all group"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium text-foreground group-hover:text-foreground truncate pr-2">
                      {vacancy.title}
                    </div>
                    <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-muted-foreground flex-shrink-0" />
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="text-muted-foreground">
                      <Users className="h-3 w-3 inline mr-1" />
                      {vacancy.applications_count} откликов
                    </span>
                    {topCount > 0 && (
                      <span className="text-green-600">
                        <Star className="h-3 w-3 inline mr-1" />
                        {topCount} топ
                      </span>
                    )}
                    {vacancy.new_applications_count > 0 && (
                      <span className="text-blue-600">+{vacancy.new_applications_count} новых</span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Топ кандидаты с one-liner */}
      {topCandidates.length > 0 && (
        <motion.div {...fadeIn}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-[13px] font-medium uppercase tracking-wide text-muted-foreground">Лучшие кандидаты</h2>
            <Link to="/analysis" className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1">
              Все результаты <ChevronRight className="h-3 w-3" />
            </Link>
          </div>
          <Card>
            <CardContent className="p-0">
              <div className="divide-y divide-border">
                {topCandidates.map((candidate, index) => (
                  <div
                    key={index}
                    className="p-4 hover:bg-card transition-colors cursor-pointer"
                    onClick={() => navigate('/analysis')}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-orange-200 to-orange-300 flex items-center justify-center text-[11px] font-medium text-orange-800 flex-shrink-0">
                        {candidate.candidate_name?.split(' ').map(n => n[0]).join('').slice(0, 2) || '??'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-foreground">{candidate.candidate_name}</span>
                          <span className="text-amber-400 text-xs">
                            {'★'.repeat(getPriorityStars(candidate.score))}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground mb-2">{candidate.vacancy_title}</div>
                        <div className="text-sm text-muted-foreground italic">
                          "{candidate.one_liner || 'Релевантный опыт, оценка ' + candidate.score + '%'}"
                        </div>
                      </div>
                      <span className={'px-2 py-1 rounded text-[11px] font-medium border flex-shrink-0 ' + getRecommendationStyle(candidate.recommendation)}>
                        {getRecommendationText(candidate.recommendation)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Quick Actions + Usage */}
      <motion.div {...fadeIn} className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Button
            variant="outline"
            className="h-auto py-4 px-4 flex flex-col items-center gap-2 border-border hover:border-muted-foreground/30 hover:bg-muted"
            onClick={() => navigate('/analysis')}
          >
            <Play className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium">Запустить анализ</span>
          </Button>
          <Button
            variant="outline"
            className="h-auto py-4 px-4 flex flex-col items-center gap-2 border-border hover:border-muted-foreground/30 hover:bg-muted"
            onClick={() => navigate('/sync')}
          >
            <RefreshCw className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium">Синхронизация</span>
          </Button>
          <Button
            variant="outline"
            className="h-auto py-4 px-4 flex flex-col items-center gap-2 border-border hover:border-muted-foreground/30 hover:bg-muted"
            onClick={() => navigate('/export')}
          >
            <Download className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium">Экспорт Excel</span>
          </Button>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="h-4 w-4 text-muted-foreground" />
            <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Лимит</span>
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-2xl font-semibold">{dashboardStats?.analyses_this_month || 0}</span>
            <span className="text-muted-foreground">/ {dashboardStats?.analyses_limit || 500}</span>
          </div>
          <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-foreground rounded-full transition-all"
              style={{ width: Math.min(usagePercent, 100) + '%' }}
            />
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">{usagePercent}% использовано</span>
            <Link to="/pricing" className="text-muted-foreground hover:text-foreground">Тарифы →</Link>
          </div>
        </div>
      </motion.div>

      {/* Empty state если нет вакансий */}
      {vacancies.length === 0 && (
        <motion.div {...fadeIn}>
          <Card className="border-dashed border-border">
            <CardContent className="py-12 text-center">
              <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Нет вакансий</h3>
              <p className="text-muted-foreground text-sm mb-6">
                Синхронизируйте данные с HH.ru чтобы начать работу
              </p>
              <Button asChild>
                <Link to="/sync">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Синхронизировать
                </Link>
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard;
