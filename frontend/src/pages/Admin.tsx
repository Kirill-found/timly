import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
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
import { Send, Users, DollarSign, Package, Search } from 'lucide-react';

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
  const { token } = useAuth();
  const [stats, setStats] = useState<Statistics | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState('');

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchStatistics();
    fetchUsers();
  }, []);

  const fetchStatistics = async () => {
    try {
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
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${userId}/subscription?plan_type=${planType}&duration_months=1`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) throw new Error('Ошибка обновления подписки');

      setSuccess('Подписка успешно обновлена');
      setSelectedUser(null);
      setSelectedPlan('');
      fetchUsers(searchQuery);
      fetchStatistics();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Не удалось обновить подписку');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    fetchUsers(searchQuery);
  };

  const getPlanBadgeColor = (planType: string | undefined) => {
    if (!planType) return 'bg-gray-500';
    switch (planType) {
      case 'free':
        return 'bg-gray-500';
      case 'starter':
        return 'bg-blue-500';
      case 'professional':
        return 'bg-purple-500';
      case 'enterprise':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Админ-панель</h1>
        <Button onClick={sendStatisticsToTelegram} disabled={loading}>
          <Send className="mr-2 h-4 w-4" />
          Отправить статистику в Telegram
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Статистика */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Всего пользователей</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.users.total}</div>
              <p className="text-xs text-muted-foreground">
                Новых за неделю: {stats.users.new_this_week}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">С HH токеном</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.users.with_hh_token}</div>
              <p className="text-xs text-muted-foreground">
                Активных: {stats.users.active}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Подписки</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.subscriptions.free +
                  stats.subscriptions.starter +
                  stats.subscriptions.professional +
                  stats.subscriptions.enterprise}
              </div>
              <p className="text-xs text-muted-foreground">
                Без подписки: {stats.users.without_subscription}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Выручка (30 дней)</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.payments_last_30_days.revenue.toLocaleString('ru-RU')} ₽
              </div>
              <p className="text-xs text-muted-foreground">
                Платежей: {stats.payments_last_30_days.count}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Список пользователей */}
      <Card>
        <CardHeader>
          <CardTitle>Пользователи</CardTitle>
          <CardDescription>Управление пользователями и подписками</CardDescription>
          <div className="flex gap-2 mt-4">
            <Input
              placeholder="Поиск по email или компании..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} disabled={loading}>
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email</TableHead>
                <TableHead>Компания</TableHead>
                <TableHead>Подписка</TableHead>
                <TableHead>HH токен</TableHead>
                <TableHead>Дата регистрации</TableHead>
                <TableHead>Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.email}</TableCell>
                  <TableCell>{user.company_name || '—'}</TableCell>
                  <TableCell>
                    {user.subscription ? (
                      <Badge className={getPlanBadgeColor(user.subscription.plan_type)}>
                        {user.subscription.plan_name}
                      </Badge>
                    ) : (
                      <Badge variant="outline">Нет подписки</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.has_hh_token ? 'default' : 'secondary'}>
                      {user.has_hh_token ? 'Есть' : 'Нет'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString('ru-RU')}
                  </TableCell>
                  <TableCell>
                    {selectedUser === user.id ? (
                      <div className="flex gap-2">
                        <Select value={selectedPlan} onValueChange={setSelectedPlan}>
                          <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Выберите тариф" />
                          </SelectTrigger>
                          <SelectContent>
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
                        >
                          Отмена
                        </Button>
                      </div>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedUser(user.id)}
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
    </div>
  );
}
