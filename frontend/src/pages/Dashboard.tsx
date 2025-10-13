/**
 * Главная панель управления Timly
 * Dashboard с общей статистикой и быстрыми действиями
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Trophy,
  BarChart3,
  RefreshCw,
  Download,
  Settings
} from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { useAuth } from '@/store/AuthContext';
import { useApp } from '@/store/AppContext';
import { apiClient } from '@/services/api';
import SubscriptionWidget from '@/components/Subscription/SubscriptionWidget';

interface DashboardStats {
  total_analyses: number;
  analyses_this_month: number;
  avg_score: number;
  top_candidates_count: number;
  total_cost_cents: number;
  cost_this_month_cents: number;
  recent_analyses: Array<{
    vacancy_title: string;
    candidate_name: string;
    score: number;
    recommendation: string;
    analyzed_at: string;
  }>;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { activeSyncJobs } = useApp();
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const loadDashboardStats = async () => {
      try {
        setStatsLoading(true);

        // Загрузка реальной статистики из API
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

      // Автоматическое обновление статистики каждые 10 секунд
      const intervalId = setInterval(() => {
        loadDashboardStats();
      }, 10000); // 10 секунд

      return () => clearInterval(intervalId); // Очистка при размонтировании
    } else {
      setStatsLoading(false);
    }
  }, [user]);

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
      case 'hire': return 'Нанимать';
      case 'interview': return 'Собеседование';
      case 'maybe': return 'Возможно';
      case 'reject': return 'Отклонить';
      default: return recommendation;
    }
  };

  if (!user?.has_hh_token) {
    return (
      <div className="p-6">
        <div className="max-w-2xl mx-auto">
          <Alert>
            <Settings className="h-4 w-4" />
            <AlertDescription className="mt-2">
              <h3 className="font-semibold mb-2">Настройка интеграции с HH.ru</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Для начала работы с Timly необходимо подключить ваш аккаунт HH.ru.
                Это позволит системе получать данные о ваших вакансиях и откликах.
              </p>
              <Button asChild>
                <Link to="/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  Настроить интеграцию
                </Link>
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  if (statsLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-12 w-full" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Приветствие */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Добро пожаловать, {user?.company_name || 'HR-специалист'}!
        </h1>
        <p className="text-muted-foreground">
          Обзор вашей активности в системе анализа резюме
        </p>
      </div>

      {/* Активные синхронизации */}
      {activeSyncJobs.length > 0 && (
        <Alert>
          <RefreshCw className="h-4 w-4 animate-spin" />
          <AlertDescription>
            Выполняется синхронизация. Активных задач: {activeSyncJobs.length}.{' '}
            <Link to="/sync" className="font-medium underline">
              Посмотреть статус
            </Link>
          </AlertDescription>
        </Alert>
      )}

      {/* Основная статистика */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Link to="/export">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Всего анализов</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{dashboardStats?.total_analyses || 0}</div>
              <p className="text-xs text-muted-foreground mt-1">Кликните для просмотра</p>
            </CardContent>
          </Card>
        </Link>

        <Link to="/export">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">За этот месяц</CardTitle>
              <LayoutDashboard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{dashboardStats?.analyses_this_month || 0}</div>
              <p className="text-xs text-muted-foreground mt-1">Кликните для просмотра</p>
            </CardContent>
          </Card>
        </Link>

        <Link to="/export?minScore=80">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Средний балл</CardTitle>
              <Trophy className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {dashboardStats?.avg_score?.toFixed(1) || 0}/100
              </div>
              <p className="text-xs text-muted-foreground mt-1">Лучшие кандидаты (80+)</p>
            </CardContent>
          </Card>
        </Link>

        <Link to="/export?recommendation=hire">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Топ кандидатов</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{dashboardStats?.top_candidates_count || 0}</div>
              <p className="text-xs text-muted-foreground mt-1">Рекомендация "Нанять"</p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Основной контент */}
      <div className="grid gap-4 md:grid-cols-3">
        {/* Виджет подписки */}
        <div className="md:col-span-1">
          <SubscriptionWidget />
        </div>

        {/* Быстрые действия */}
        <Card className="md:col-span-1" style={{ display: 'none' }}>
          <CardHeader>
            <CardTitle>Быстрые действия</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button asChild className="w-full">
              <Link to="/sync">
                <RefreshCw className="mr-2 h-4 w-4" />
                Синхронизировать с HH.ru
              </Link>
            </Button>

            <Button asChild variant="outline" className="w-full">
              <Link to="/analysis">
                <BarChart3 className="mr-2 h-4 w-4" />
                Запустить анализ
              </Link>
            </Button>

            <Button asChild variant="outline" className="w-full">
              <Link to="/export">
                <Download className="mr-2 h-4 w-4" />
                Экспорт результатов
              </Link>
            </Button>

            <Button asChild variant="outline" className="w-full">
              <Link to="/settings">
                <Settings className="mr-2 h-4 w-4" />
                Настройки
              </Link>
            </Button>

            <div className="mt-6 p-4 bg-muted rounded-lg">
              <p className="text-sm font-medium mb-2">Стоимость анализов:</p>
              <p className="text-xs text-muted-foreground">
                За этот месяц: {((dashboardStats?.cost_this_month_cents || 0) / 100).toFixed(2)} ₽
              </p>
              <p className="text-xs text-muted-foreground">
                Всего: {((dashboardStats?.total_cost_cents || 0) / 100).toFixed(2)} ₽
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Последние анализы */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Последние анализы</CardTitle>
            <CardDescription>Результаты AI-анализа резюме</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardStats?.recent_analyses?.length ? (
              <div className="space-y-4">
                {dashboardStats.recent_analyses.map((item, index) => (
                  <div key={index} className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{item.candidate_name}</p>
                        <Link to={`/results?recommendation=${item.recommendation}`}>
                          <Badge
                            variant={getRecommendationVariant(item.recommendation)}
                            className="cursor-pointer hover:opacity-80 transition-opacity"
                          >
                            {getRecommendationText(item.recommendation)}
                          </Badge>
                        </Link>
                      </div>
                      <p className="text-sm text-muted-foreground">{item.vacancy_title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full ${
                              item.score >= 80 ? 'bg-green-500' :
                              item.score >= 60 ? 'bg-orange-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${item.score}%` }}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground">{item.score}%</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-bold text-primary">{item.score}</span>
                      <span className="text-sm text-muted-foreground">/100</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground mb-4">Пока нет анализов</p>
                <Button asChild variant="link">
                  <Link to="/analysis">Запустить первый анализ</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;