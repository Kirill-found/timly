/**
 * Админ-панель
 * Управление пользователями и статистика
 * Design: Dark Industrial
 */
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/store/AuthContext';
import { apiClient } from '@/services/api';
import { Send, Users, DollarSign, Package, Search, CheckCircle, XCircle, Loader2, Shield } from 'lucide-react';

interface Statistics {
  users: {
    total: number;
    active: number;
    with_hh_token: number;
    new_this_week: number;
    without_subscription: number;
  };
  subscriptions: {
    free: number;
    starter: number;
    professional: number;
    enterprise: number;
  };
  payments_last_30_days: {
    count: number;
    revenue: number;
  };
}

interface User {
  id: string;
  email: string;
  company_name: string;
  role: string;
  is_active: boolean;
  has_hh_token: boolean;
  created_at: string;
  subscription: {
    plan_type: string;
    plan_name: string;
    status: string;
    expires_at: string;
    days_remaining: number;
  } | null;
}

export default function Admin() {
  useAuth();
  const [stats, setStats] = useState<Statistics | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState('');

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const getAuthToken = () => apiClient.getAuthToken();

  useEffect(() => {
    fetchStatistics();
    fetchUsers();
  }, []);

  const fetchStatistics = async () => {
    try {
      const token = getAuthToken();
      const response = await fetch(`${API_BASE_URL}/api/admin/statistics`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Ошибка загрузки статистики');

      const result = await response.json();
      setStats(result.data);
    } catch (err) {
      console.error('Error fetching statistics:', err);
    }
  };

  const fetchUsers = async (search = '') => {
    setLoading(true);
    try {
      const token = getAuthToken();
      const url = new URL(`${API_BASE_URL}/api/admin/users`);
      if (search) url.searchParams.append('search', search);

      const response = await fetch(url.toString(), {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Ошибка загрузки пользователей');

      const result = await response.json();
      setUsers(result.data.users);
    } catch (err) {
      setError('Не удалось загрузить список пользователей');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const sendStatisticsToTelegram = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = getAuthToken();
      const response = await fetch(
        `${API_BASE_URL}/api/admin/telegram/send-statistics`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) throw new Error('Ошибка отправки статистики');

      setSuccess('Статистика успешно отправлена в Telegram');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Не удалось отправить статистику в Telegram');
    } finally {
      setLoading(false);
    }
  };

  const updateUserSubscription = async (userId: string, planType: string) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = getAuthToken();
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${userId}/subscription?plan_type=${planType}&duration_months=1`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.detail || errorData.message || 'Ошибка обновления подписки';
        throw new Error(errorMessage);
      }

      setSuccess('Подписка успешно обновлена');
      setSelectedUser(null);
      setSelectedPlan('');
      fetchUsers(searchQuery);
      fetchStatistics();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      console.error('Subscription update error:', err);
      setError(err.message || 'Не удалось обновить подписку');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    fetchUsers(searchQuery);
  };

  const getPlanBadgeClass = (planType: string | undefined) => {
    if (!planType) return 'bg-zinc-700 text-zinc-300 border-zinc-600';
    switch (planType) {
      case 'trial':
        return 'bg-green-500/15 text-green-400 border-green-500/30';
      case 'free':
        return 'bg-zinc-700 text-zinc-300 border-zinc-600';
      case 'starter':
        return 'bg-blue-500/15 text-blue-400 border-blue-500/30';
      case 'professional':
        return 'bg-purple-500/15 text-purple-400 border-purple-500/30';
      case 'enterprise':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      default:
        return 'bg-zinc-700 text-zinc-300 border-zinc-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
              <Shield className="h-5 w-5 text-zinc-400" />
            </div>
            Админ-панель
          </h1>
          <p className="text-zinc-500 text-sm mt-2">Управление пользователями и статистика</p>
        </div>
        <Button
          onClick={sendStatisticsToTelegram}
          disabled={loading}
          variant="outline"
          className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
        >
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Send className="mr-2 h-4 w-4" />
          )}
          Отправить в Telegram
        </Button>
      </div>

      {/* Уведомления */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Alert className="bg-red-500/10 border-red-500/20">
            <XCircle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-400">{error}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      {success && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Alert className="bg-green-500/10 border-green-500/20">
            <CheckCircle className="h-4 w-4 text-green-400" />
            <AlertDescription className="text-green-400">{success}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Статистика */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-px bg-zinc-800 rounded-lg overflow-hidden">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-zinc-900 p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-zinc-500">Всего пользователей</span>
              <Users className="h-4 w-4 text-zinc-600" />
            </div>
            <div className="text-3xl font-bold text-zinc-100 tabular-nums">{stats.users.total}</div>
            <p className="text-xs text-zinc-600 mt-1">
              Новых за неделю: <span className="text-zinc-400">{stats.users.new_this_week}</span>
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-zinc-900 p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-zinc-500">С HH токеном</span>
              <Package className="h-4 w-4 text-zinc-600" />
            </div>
            <div className="text-3xl font-bold text-zinc-100 tabular-nums">{stats.users.with_hh_token}</div>
            <p className="text-xs text-zinc-600 mt-1">
              Активных: <span className="text-zinc-400">{stats.users.active}</span>
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-zinc-900 p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-zinc-500">Подписки</span>
              <Package className="h-4 w-4 text-zinc-600" />
            </div>
            <div className="text-3xl font-bold text-zinc-100 tabular-nums">
              {stats.subscriptions.free +
                stats.subscriptions.starter +
                stats.subscriptions.professional +
                stats.subscriptions.enterprise}
            </div>
            <p className="text-xs text-zinc-600 mt-1">
              Без подписки: <span className="text-zinc-400">{stats.users.without_subscription}</span>
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-zinc-900 p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-zinc-500">Выручка (30 дней)</span>
              <DollarSign className="h-4 w-4 text-zinc-600" />
            </div>
            <div className="text-3xl font-bold text-zinc-100 tabular-nums">
              {stats.payments_last_30_days.revenue.toLocaleString('ru-RU')} ₽
            </div>
            <p className="text-xs text-zinc-600 mt-1">
              Платежей: <span className="text-zinc-400">{stats.payments_last_30_days.count}</span>
            </p>
          </motion.div>
        </div>
      )}

      {/* Список пользователей */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader className="border-b border-zinc-800">
            <CardTitle className="text-zinc-100">Пользователи</CardTitle>
            <p className="text-sm text-zinc-500">Управление пользователями и подписками</p>
            <div className="flex gap-2 mt-4">
              <Input
                placeholder="Поиск по email или компании..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500"
              />
              <Button
                onClick={handleSearch}
                disabled={loading}
                variant="outline"
                className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pt-0 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800 hover:bg-transparent">
                  <TableHead className="text-zinc-400">Email</TableHead>
                  <TableHead className="text-zinc-400">Компания</TableHead>
                  <TableHead className="text-zinc-400">Подписка</TableHead>
                  <TableHead className="text-zinc-400">HH токен</TableHead>
                  <TableHead className="text-zinc-400">Дата регистрации</TableHead>
                  <TableHead className="text-zinc-400">Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} className="border-zinc-800 hover:bg-zinc-800/30">
                    <TableCell className="font-medium text-zinc-200">{user.email}</TableCell>
                    <TableCell className="text-zinc-400">{user.company_name || '—'}</TableCell>
                    <TableCell>
                      {user.subscription ? (
                        <span className={`px-2 py-0.5 rounded text-xs border ${getPlanBadgeClass(user.subscription.plan_type)}`}>
                          {user.subscription.plan_name}
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-xs border border-zinc-700 text-zinc-500">
                          Нет подписки
                        </span>
                      )}
                    </TableCell>
                    <TableCell>
                      <span className={`px-2 py-0.5 rounded text-xs border ${
                        user.has_hh_token
                          ? 'bg-green-500/15 text-green-400 border-green-500/30'
                          : 'bg-zinc-800 text-zinc-500 border-zinc-700'
                      }`}>
                        {user.has_hh_token ? 'Есть' : 'Нет'}
                      </span>
                    </TableCell>
                    <TableCell className="text-zinc-500 tabular-nums">
                      {new Date(user.created_at).toLocaleDateString('ru-RU')}
                    </TableCell>
                    <TableCell>
                      {selectedUser === user.id ? (
                        <div className="flex gap-2">
                          <Select value={selectedPlan} onValueChange={setSelectedPlan}>
                            <SelectTrigger className="w-[160px] bg-zinc-800/50 border-zinc-700 text-zinc-100">
                              <SelectValue placeholder="Выберите тариф" />
                            </SelectTrigger>
                            <SelectContent className="bg-zinc-900 border-zinc-800">
                              <SelectItem value="trial">Trial</SelectItem>
                              <SelectItem value="free">Free</SelectItem>
                              <SelectItem value="starter">Starter</SelectItem>
                              <SelectItem value="professional">Professional</SelectItem>
                              <SelectItem value="enterprise">Enterprise</SelectItem>
                            </SelectContent>
                          </Select>
                          <Button
                            size="sm"
                            onClick={() => updateUserSubscription(user.id, selectedPlan)}
                            disabled={!selectedPlan || loading}
                            className="bg-zinc-100 text-zinc-900 hover:bg-white"
                          >
                            Сохранить
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedUser(null);
                              setSelectedPlan('');
                            }}
                            className="border-zinc-700 text-zinc-400 hover:bg-zinc-800"
                          >
                            Отмена
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setSelectedUser(user.id)}
                          className="border-zinc-700 text-zinc-400 hover:bg-zinc-800"
                        >
                          Изменить тариф
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
