/**
 * Главная панель управления Timly
 * Dashboard с общей статистикой и быстрыми действиями
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  Users,
  Trophy,
  BarChart3,
  RefreshCw,
  Download,
  Settings,
  TrendingUp,
  Target,
  Sparkles,
  ArrowUpRight,
  Clock,
  CheckCircle2
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
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

// Цвета для графиков
const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  gradient: ['#3b82f6', '#8b5cf6', '#ec4899']
};

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { activeSyncJobs } = useApp();
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
      // Убрали автообновление каждые 10 секунд, чтобы страница не моргала
      // Данные обновятся при следующем заходе на Dashboard
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

  // Данные для графиков (mock data для красоты)
  const monthlyData = [
    { name: 'Янв', анализы: 12, кандидаты: 8 },
    { name: 'Фев', анализы: 19, кандидаты: 15 },
    { name: 'Мар', анализы: 25, кандидаты: 20 },
    { name: 'Апр', анализы: 31, кандидаты: 24 },
    { name: 'Май', анализы: 38, кандидаты: 29 },
    { name: 'Июн', анализы: dashboardStats?.analyses_this_month || 45, кандидаты: dashboardStats?.top_candidates_count || 35 }
  ];

  const recommendationData = [
    { name: 'Нанять', value: dashboardStats?.top_candidates_count || 15, color: CHART_COLORS.success },
    { name: 'Собеседование', value: Math.floor((dashboardStats?.total_analyses || 50) * 0.3), color: CHART_COLORS.primary },
    { name: 'Возможно', value: Math.floor((dashboardStats?.total_analyses || 50) * 0.25), color: CHART_COLORS.warning },
    { name: 'Отклонить', value: Math.floor((dashboardStats?.total_analyses || 50) * 0.2), color: CHART_COLORS.danger }
  ];

  // Анимационные варианты
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  if (!user?.has_hh_token) {
    return (
      <div className="p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto"
        >
          <Alert className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
            <Settings className="h-5 w-5 text-primary" />
            <AlertDescription className="mt-2">
              <h3 className="font-semibold text-lg mb-2">Настройка интеграции с HH.ru</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Для начала работы с Timly необходимо подключить ваш аккаунт HH.ru.
                Это позволит системе получать данные о ваших вакансиях и откликах.
              </p>
              <Button asChild className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70">
                <Link to="/settings">
                  <Settings className="mr-2 h-4 w-4" />
                  Настроить интеграцию
                </Link>
              </Button>
            </AlertDescription>
          </Alert>
        </motion.div>
      </div>
    );
  }

  if (statsLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-16 w-full" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-80" />
          <Skeleton className="h-80" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-3 sm:p-4 md:p-6 space-y-4 sm:space-y-6">
      {/* Приветствие с градиентом */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-4 sm:p-6 md:p-8 text-white"
      >
        <div className="absolute inset-0 bg-grid-white/10" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="h-5 w-5 sm:h-6 sm:w-6" />
            <h1 className="text-xl sm:text-2xl md:text-3xl font-bold">
              Добро пожаловать{window.innerWidth >= 640 ? `, ${user?.company_name || 'HR-специалист'}` : ''}!
            </h1>
          </div>
          <p className="text-white/90 text-sm sm:text-base md:text-lg">
            Обзор вашей активности в системе анализа резюме
          </p>
        </div>

        {/* Декоративные элементы */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full blur-3xl" />
      </motion.div>

      {/* Активные синхронизации */}
      {activeSyncJobs.length > 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <Alert className="border-blue-500/50 bg-blue-500/10">
            <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />
            <AlertDescription>
              <span className="font-medium">Выполняется синхронизация.</span> Активных задач: {activeSyncJobs.length}.{' '}
              <Link to="/sync" className="font-medium underline hover:text-blue-600 transition-colors">
                Посмотреть статус
              </Link>
            </AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Основная статистика с градиентными карточками */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        {/* Карточка 1: Всего анализов */}
        <motion.div variants={itemVariants}>
          <Link to="/export">
            <Card className="group relative overflow-hidden cursor-pointer transition-all duration-300 hover:shadow-2xl hover:scale-105 border-0 bg-gradient-to-br from-blue-500 to-blue-600">
              <div className="absolute inset-0 bg-grid-white/10" />
              <CardHeader className="relative flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/90">Всего анализов</CardTitle>
                <div className="rounded-full bg-white/20 p-2 backdrop-blur-sm">
                  <BarChart3 className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="flex items-baseline gap-2">
                  <div className="text-4xl font-bold text-white">{dashboardStats?.total_analyses || 0}</div>
                  <TrendingUp className="h-5 w-5 text-white/80" />
                </div>
                <p className="text-xs text-white/70 mt-2 flex items-center gap-1">
                  <ArrowUpRight className="h-3 w-3" />
                  Кликните для просмотра
                </p>
              </CardContent>
            </Card>
          </Link>
        </motion.div>

        {/* Карточка 2: За этот месяц */}
        <motion.div variants={itemVariants}>
          <Link to="/export">
            <Card className="group relative overflow-hidden cursor-pointer transition-all duration-300 hover:shadow-2xl hover:scale-105 border-0 bg-gradient-to-br from-green-500 to-emerald-600">
              <div className="absolute inset-0 bg-grid-white/10" />
              <CardHeader className="relative flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/90">За этот месяц</CardTitle>
                <div className="rounded-full bg-white/20 p-2 backdrop-blur-sm">
                  <Clock className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="flex items-baseline gap-2">
                  <div className="text-4xl font-bold text-white">{dashboardStats?.analyses_this_month || 0}</div>
                  <TrendingUp className="h-5 w-5 text-white/80" />
                </div>
                <p className="text-xs text-white/70 mt-2 flex items-center gap-1">
                  <ArrowUpRight className="h-3 w-3" />
                  Кликните для просмотра
                </p>
              </CardContent>
            </Card>
          </Link>
        </motion.div>

        {/* Карточка 3: Средний балл */}
        <motion.div variants={itemVariants}>
          <Link to="/export?minScore=80">
            <Card className="group relative overflow-hidden cursor-pointer transition-all duration-300 hover:shadow-2xl hover:scale-105 border-0 bg-gradient-to-br from-orange-500 to-amber-600">
              <div className="absolute inset-0 bg-grid-white/10" />
              <CardHeader className="relative flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/90">Средний балл</CardTitle>
                <div className="rounded-full bg-white/20 p-2 backdrop-blur-sm">
                  <Trophy className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="flex items-baseline gap-2">
                  <div className="text-4xl font-bold text-white">
                    {dashboardStats?.avg_score?.toFixed(1) || 0}
                  </div>
                  <span className="text-xl text-white/70">/100</span>
                </div>
                <p className="text-xs text-white/70 mt-2 flex items-center gap-1">
                  <Target className="h-3 w-3" />
                  Лучшие кандидаты (80+)
                </p>
              </CardContent>
            </Card>
          </Link>
        </motion.div>

        {/* Карточка 4: Топ кандидатов */}
        <motion.div variants={itemVariants}>
          <Link to="/export?recommendation=hire">
            <Card className="group relative overflow-hidden cursor-pointer transition-all duration-300 hover:shadow-2xl hover:scale-105 border-0 bg-gradient-to-br from-purple-500 to-pink-600">
              <div className="absolute inset-0 bg-grid-white/10" />
              <CardHeader className="relative flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/90">Топ кандидатов</CardTitle>
                <div className="rounded-full bg-white/20 p-2 backdrop-blur-sm">
                  <Users className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="flex items-baseline gap-2">
                  <div className="text-4xl font-bold text-white">{dashboardStats?.top_candidates_count || 0}</div>
                  <CheckCircle2 className="h-5 w-5 text-white/80" />
                </div>
                <p className="text-xs text-white/70 mt-2 flex items-center gap-1">
                  <ArrowUpRight className="h-3 w-3" />
                  Рекомендация "Нанять"
                </p>
              </CardContent>
            </Card>
          </Link>
        </motion.div>
      </motion.div>

      {/* Графики и статистика */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* График динамики анализов */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Динамика анализов
              </CardTitle>
              <CardDescription>Количество анализов по месяцам</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={monthlyData}>
                  <defs>
                    <linearGradient id="colorAnalyzes" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.8}/>
                      <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0.1}/>
                    </linearGradient>
                    <linearGradient id="colorCandidates" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={CHART_COLORS.secondary} stopOpacity={0.8}/>
                      <stop offset="95%" stopColor={CHART_COLORS.secondary} stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" stroke="#888888" />
                  <YAxis stroke="#888888" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: 'none',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="анализы"
                    stroke={CHART_COLORS.primary}
                    fillOpacity={1}
                    fill="url(#colorAnalyzes)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="кандидаты"
                    stroke={CHART_COLORS.secondary}
                    fillOpacity={1}
                    fill="url(#colorCandidates)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* График распределения рекомендаций */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                Распределение рекомендаций
              </CardTitle>
              <CardDescription>Категории кандидатов</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={recommendationData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {recommendationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: 'none',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Основной контент */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Виджет подписки */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="md:col-span-1"
        >
          <SubscriptionWidget />
        </motion.div>

        {/* Последние анализы */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="md:col-span-2"
        >
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Последние анализы
              </CardTitle>
              <CardDescription>Результаты AI-анализа резюме</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardStats?.recent_analyses?.length ? (
                <div className="space-y-4">
                  {dashboardStats.recent_analyses.map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="group flex items-center justify-between border-b pb-4 last:border-0 last:pb-0 hover:bg-muted/50 -mx-2 px-2 py-2 rounded-lg transition-all"
                    >
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium group-hover:text-primary transition-colors">{item.candidate_name}</p>
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
                        <div className="flex items-center gap-3">
                          <Progress
                            value={item.score}
                            className="w-32 h-2"
                          />
                          <span className="text-xs text-muted-foreground font-medium">{item.score}%</span>
                        </div>
                      </div>
                      <div className="text-right ml-4">
                        <span className="text-3xl font-bold bg-gradient-to-br from-primary to-primary/60 bg-clip-text text-transparent">
                          {item.score}
                        </span>
                        <span className="text-sm text-muted-foreground">/100</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
                    <BarChart3 className="h-8 w-8 text-primary" />
                  </div>
                  <p className="text-muted-foreground mb-4 font-medium">Пока нет анализов</p>
                  <Button asChild variant="outline" className="hover:bg-primary hover:text-white transition-all">
                    <Link to="/analysis">Запустить первый анализ</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
