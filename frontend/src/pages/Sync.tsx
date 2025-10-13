/**
 * Страница синхронизации с HH.ru
 * Запуск и отслеживание синхронизации вакансий и откликов
 */
import React, { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle, XCircle, AlertCircle, Briefcase, Users } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/services/api';
import { useAuth } from '@/store/AuthContext';
import { SyncJob } from '@/types';

const Sync: React.FC = () => {
  const { user } = useAuth();
  const [currentJob, setCurrentJob] = useState<SyncJob | null>(() => {
    // Восстанавливаем состояние из sessionStorage при монтировании
    try {
      const saved = sessionStorage.getItem('currentSyncJob');
      if (saved) {
        const job = JSON.parse(saved);
        console.log('[SYNC] Restored job from sessionStorage:', job.id, job.status);
        return job;
      }
    } catch (err) {
      console.error('[SYNC] Error restoring job from sessionStorage:', err);
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [syncHistory, setSyncHistory] = useState<SyncJob[]>([]);

  // Сохраняем currentJob в sessionStorage при каждом обновлении
  useEffect(() => {
    if (currentJob) {
      console.log('[SYNC] Saving job to sessionStorage:', currentJob.id, currentJob.status);
      sessionStorage.setItem('currentSyncJob', JSON.stringify(currentJob));

      // Если задача завершена или провалена, очищаем через 1 минуту
      if (currentJob.status === 'completed' || currentJob.status === 'failed') {
        setTimeout(() => {
          console.log('[SYNC] Clearing completed job from sessionStorage');
          sessionStorage.removeItem('currentSyncJob');
        }, 60000); // 1 минута
      }
    } else {
      console.log('[SYNC] Removing job from sessionStorage');
      sessionStorage.removeItem('currentSyncJob');
    }
  }, [currentJob]);

  // Polling для отслеживания прогресса
  useEffect(() => {
    console.log('[SYNC POLLING] useEffect triggered, currentJob:', currentJob?.status);

    if (!currentJob || currentJob.status === 'completed' || currentJob.status === 'failed') {
      console.log('[SYNC POLLING] Not starting polling - job is null or finished');
      return;
    }

    console.log('[SYNC POLLING] Starting polling for job:', currentJob.id);

    const pollStatus = async () => {
      console.log('[SYNC POLLING] Polling sync status...');
      try {
        const updatedJob = await apiClient.getSyncStatus(currentJob.id);
        console.log('[SYNC POLLING] Got updated job:', updatedJob.status, 'vacancies:', updatedJob.vacancies_synced, 'apps:', updatedJob.applications_synced);
        setCurrentJob(updatedJob);

        // Если завершилась, останавливаем polling и обновляем историю
        if (updatedJob.status === 'completed' || updatedJob.status === 'failed') {
          console.log('[SYNC POLLING] Job finished, loading history');
          await loadSyncHistory();
        }
      } catch (err) {
        console.error('[SYNC POLLING] Error polling sync status:', err);
      }
    };

    const interval = setInterval(pollStatus, 2000); // Проверяем каждые 2 секунды
    console.log('[SYNC POLLING] Interval started');

    // Добавляем обработчик для Page Visibility API
    // Когда пользователь возвращается на вкладку - сразу обновляем
    const handleVisibilityChange = async () => {
      console.log('[SYNC POLLING] Visibility changed, hidden:', document.hidden);
      if (!document.hidden) {
        console.log('[SYNC POLLING] Tab became visible, polling immediately...');
        await pollStatus(); // Немедленно обновляем при возврате на вкладку
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      console.log('[SYNC POLLING] Cleaning up interval and listener');
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [currentJob]);

  // Загрузка истории синхронизаций при монтировании и при возврате на страницу
  useEffect(() => {
    console.log('[SYNC HISTORY] useEffect triggered, currentJob:', currentJob?.status);
    loadSyncHistory();

    // Обновляем каждые 10 секунд, чтобы всегда показывать актуальную информацию
    const interval = setInterval(() => {
      console.log('[SYNC HISTORY] Interval tick - loading history');
      loadSyncHistory();
    }, 10000);

    // Добавляем обработчик для Page Visibility API
    // Когда пользователь возвращается на вкладку - сразу обновляем историю И проверяем активную синхронизацию
    const handleVisibilityChange = async () => {
      console.log('[SYNC HISTORY] Visibility changed, hidden:', document.hidden, 'currentJob:', currentJob?.status);
      if (!document.hidden) {
        console.log('[SYNC HISTORY] Tab became visible, updating sync history...');
        await loadSyncHistory(); // Немедленно обновляем при возврате на вкладку

        // Если есть текущая задача, проверяем её статус
        if (currentJob && (currentJob.status === 'processing' || currentJob.status === 'pending' || currentJob.status === 'running')) {
          console.log('[SYNC HISTORY] Checking current job status...', currentJob.id);
          try {
            const updatedJob = await apiClient.getSyncStatus(currentJob.id);
            console.log('[SYNC HISTORY] Updated job status:', updatedJob.status);
            setCurrentJob(updatedJob);

            // Если завершилась пока мы были на другой вкладке, обновляем историю
            if (updatedJob.status === 'completed' || updatedJob.status === 'failed') {
              console.log('[SYNC HISTORY] Job completed, reloading history');
              await loadSyncHistory();
            }
          } catch (err) {
            console.error('[SYNC HISTORY] Error checking job status on tab visible:', err);
          }
        } else {
          console.log('[SYNC HISTORY] No active job to check');
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      console.log('[SYNC HISTORY] Cleaning up interval and listener');
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [currentJob]);

  const loadSyncHistory = async () => {
    try {
      const jobs = await apiClient.getSyncHistory(10);
      if (jobs && Array.isArray(jobs)) {
        setSyncHistory(jobs);
      } else {
        setSyncHistory([]);
      }
    } catch (err) {
      console.error('Error loading sync history:', err);
      setSyncHistory([]);
    }
  };

  const startSync = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const job = await apiClient.startSync({
        sync_vacancies: true,
        sync_applications: true,
        force_full_sync: false
      });

      if (job) {
        setCurrentJob(job);
      }
    } catch (err: any) {
      console.error('Sync error:', err);
      setError(err.response?.data?.error?.message || 'Ошибка при запуске синхронизации');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'processing':
      case 'running':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Завершено';
      case 'failed':
        return 'Ошибка';
      case 'processing':
      case 'running':
        return 'Выполняется';
      case 'pending':
        return 'В очереди';
      default:
        return status;
    }
  };

  const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case 'completed':
        return 'default';
      case 'failed':
        return 'destructive';
      case 'processing':
      case 'running':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!user?.has_hh_token) {
    return (
      <div className="p-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="mt-2">
            <h3 className="font-semibold mb-2">HH.ru токен не настроен</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Для синхронизации вакансий необходимо подключить ваш аккаунт HH.ru.
            </p>
            <Button asChild>
              <a href="/settings">Настроить интеграцию</a>
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Синхронизация с HH.ru</h1>
        <p className="text-muted-foreground">
          Получение вакансий и откликов из вашего аккаунта работодателя
        </p>
      </div>

      {/* Ошибки */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Текущая синхронизация */}
      {currentJob && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  {getStatusIcon(currentJob.status)}
                  Текущая синхронизация
                </CardTitle>
                <CardDescription>
                  Статус: <Badge variant={getStatusVariant(currentJob.status)}>{getStatusText(currentJob.status)}</Badge>
                </CardDescription>
              </div>
              {(currentJob.status === 'processing' || currentJob.status === 'running') && (
                <div className="text-sm text-muted-foreground">
                  Обновление каждые 2 секунды...
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Прогресс */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                <Briefcase className="h-8 w-8 text-blue-500" />
                <div>
                  <div className="text-2xl font-bold">{currentJob.vacancies_synced}</div>
                  <div className="text-sm text-muted-foreground">Вакансий</div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                <Users className="h-8 w-8 text-green-500" />
                <div>
                  <div className="text-2xl font-bold">{currentJob.applications_synced}</div>
                  <div className="text-sm text-muted-foreground">Откликов</div>
                </div>
              </div>
            </div>

            {/* Временные метки */}
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">Создано</div>
                <div className="font-medium">{formatDate(currentJob.created_at)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Начало</div>
                <div className="font-medium">{formatDate(currentJob.started_at)}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Завершено</div>
                <div className="font-medium">{formatDate(currentJob.completed_at)}</div>
              </div>
            </div>

            {/* Ошибки */}
            {currentJob.errors && currentJob.errors.length > 0 && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  <div className="font-semibold mb-2">Обнаружены ошибки:</div>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    {currentJob.errors.map((err, idx) => (
                      <li key={idx}>{err}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {/* Успешное завершение */}
            {currentJob.status === 'completed' && (
              <Alert>
                <CheckCircle className="h-4 w-4 text-green-500" />
                <AlertDescription>
                  Синхронизация успешно завершена! Синхронизировано {currentJob.vacancies_synced} вакансий
                  и {currentJob.applications_synced} откликов.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Кнопка запуска */}
      <Card>
        <CardHeader>
          <CardTitle>Запустить синхронизацию</CardTitle>
          <CardDescription>
            Получить актуальные данные о вакансиях и откликах из HH.ru
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Информация о последней синхронизации */}
          {syncHistory.length > 0 && syncHistory[0].status === 'completed' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-green-700 font-medium mb-2">
                <CheckCircle className="h-4 w-4" />
                Последняя синхронизация успешно завершена
              </div>
              <div className="text-sm text-green-600">
                {formatDate(syncHistory[0].completed_at)} — синхронизировано{' '}
                {syncHistory[0].vacancies_synced} вакансий и {syncHistory[0].applications_synced} откликов
              </div>
            </div>
          )}

          <Button
            onClick={startSync}
            disabled={isLoading || (currentJob?.status === 'processing' || currentJob?.status === 'running' || currentJob?.status === 'pending')}
            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Запуск...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Синхронизировать с HH.ru
              </>
            )}
          </Button>

          {(currentJob?.status === 'processing' || currentJob?.status === 'running') && (
            <p className="text-sm text-muted-foreground mt-2">
              Синхронизация уже выполняется. Дождитесь её завершения.
            </p>
          )}
        </CardContent>
      </Card>

      {/* История синхронизаций */}
      {syncHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>История синхронизаций</CardTitle>
            <CardDescription>Последние 10 задач</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {syncHistory.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(job.status)}
                    <div>
                      <div className="font-medium">{formatDate(job.created_at)}</div>
                      <div className="text-sm text-muted-foreground">
                        {job.vacancies_synced} вакансий, {job.applications_synced} откликов
                      </div>
                    </div>
                  </div>
                  <Badge variant={getStatusVariant(job.status)}>
                    {getStatusText(job.status)}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Sync;
