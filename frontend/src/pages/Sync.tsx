/**
 * Sync - Синхронизация с HH.ru
 * Design: Dark Industrial / Control Panel
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Briefcase,
  Users,
  Settings,
  ArrowRight
} from 'lucide-react';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/services/api';
import { useAuth } from '@/store/AuthContext';
import { SyncJob } from '@/types';

const Sync: React.FC = () => {
  const { user } = useAuth();
  const [currentJob, setCurrentJob] = useState<SyncJob | null>(() => {
    try {
      const saved = sessionStorage.getItem('currentSyncJob');
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (err) {
      console.error('[SYNC] Error restoring job:', err);
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [syncHistory, setSyncHistory] = useState<SyncJob[]>([]);

  // Сохраняем currentJob в sessionStorage
  useEffect(() => {
    if (currentJob) {
      sessionStorage.setItem('currentSyncJob', JSON.stringify(currentJob));
      if (currentJob.status === 'completed' || currentJob.status === 'failed') {
        setTimeout(() => {
          sessionStorage.removeItem('currentSyncJob');
        }, 60000);
      }
    } else {
      sessionStorage.removeItem('currentSyncJob');
    }
  }, [currentJob]);

  // Polling для отслеживания прогресса
  useEffect(() => {
    if (!currentJob || currentJob.status === 'completed' || currentJob.status === 'failed') {
      return;
    }

    const pollStatus = async () => {
      try {
        const updatedJob = await apiClient.getSyncStatus(currentJob.id);
        setCurrentJob(updatedJob);
        if (updatedJob.status === 'completed' || updatedJob.status === 'failed') {
          await loadSyncHistory();
        }
      } catch (err) {
        console.error('[SYNC] Polling error:', err);
      }
    };

    const interval = setInterval(pollStatus, 2000);

    const handleVisibilityChange = async () => {
      if (!document.hidden) {
        await pollStatus();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [currentJob]);

  // Загрузка истории
  useEffect(() => {
    loadSyncHistory();
    const interval = setInterval(loadSyncHistory, 10000);

    const handleVisibilityChange = async () => {
      if (!document.hidden) {
        await loadSyncHistory();
        if (currentJob && ['processing', 'pending', 'running'].includes(currentJob.status)) {
          try {
            const updatedJob = await apiClient.getSyncStatus(currentJob.id);
            setCurrentJob(updatedJob);
            if (updatedJob.status === 'completed' || updatedJob.status === 'failed') {
              await loadSyncHistory();
            }
          } catch (err) {
            console.error('[SYNC] Status check error:', err);
          }
        }
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [currentJob]);

  const loadSyncHistory = async () => {
    try {
      const jobs = await apiClient.getSyncHistory(10);
      setSyncHistory(Array.isArray(jobs) ? jobs : []);
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
      if (job) setCurrentJob(job);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Ошибка при запуске синхронизации');
    } finally {
      setIsLoading(false);
    }
  };

  const isJobRunning = currentJob?.status === 'processing' || currentJob?.status === 'running' || currentJob?.status === 'pending';

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTime = (dateString: string | null | undefined) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-500';
      case 'failed': return 'text-red-500';
      case 'processing':
      case 'running': return 'text-blue-500';
      default: return 'text-zinc-500';
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/10';
      case 'failed': return 'bg-red-500/10';
      case 'processing':
      case 'running': return 'bg-blue-500/10';
      default: return 'bg-zinc-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Завершено';
      case 'failed': return 'Ошибка';
      case 'processing':
      case 'running': return 'Выполняется';
      case 'pending': return 'В очереди';
      default: return status;
    }
  };

  // Fade in animation
  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  };

  // Нет токена HH.ru
  if (!user?.has_hh_token) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <motion.div {...fadeIn} className="max-w-md w-full">
          <Card className="border-dashed border-zinc-700">
            <CardContent className="pt-8 pb-8 text-center">
              <div className="w-14 h-14 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center mx-auto mb-6">
                <Settings className="h-6 w-6 text-zinc-400" />
              </div>
              <h2 className="text-xl font-semibold mb-2">HH.ru не подключён</h2>
              <p className="text-zinc-500 mb-6 text-sm">
                Для синхронизации вакансий подключите аккаунт HH.ru
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

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div {...fadeIn} className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">Синхронизация</h1>
          <p className="text-sm text-zinc-500 mt-1">Получение данных из HH.ru</p>
        </div>
        <Button
          onClick={startSync}
          disabled={isLoading || isJobRunning}
          className="h-9 px-4 bg-zinc-100 text-zinc-900 hover:bg-zinc-200 disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              Запуск...
            </>
          ) : isJobRunning ? (
            <>
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              Выполняется...
            </>
          ) : (
            <>
              <RefreshCw className="mr-2 h-4 w-4" />
              Синхронизировать
            </>
          )}
        </Button>
      </motion.div>

      {/* Error */}
      {error && (
        <motion.div {...fadeIn} className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
          <div className="flex items-center gap-3">
            <XCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        </motion.div>
      )}

      {/* Current Job */}
      {currentJob && (
        <motion.div {...fadeIn}>
          <Card>
            <CardContent className="p-0">
              {/* Status header */}
              <div className="p-5 border-b border-zinc-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {isJobRunning ? (
                      <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
                    ) : currentJob.status === 'completed' ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    <div>
                      <div className="text-sm font-medium text-zinc-200">
                        {isJobRunning ? 'Синхронизация выполняется' :
                         currentJob.status === 'completed' ? 'Синхронизация завершена' :
                         'Ошибка синхронизации'}
                      </div>
                      <div className="text-xs text-zinc-500 mt-0.5">
                        Начало: {formatTime(currentJob.started_at)}
                        {currentJob.completed_at && ` • Завершение: ${formatTime(currentJob.completed_at)}`}
                      </div>
                    </div>
                  </div>
                  <span className={`text-[11px] font-medium px-2 py-1 rounded ${getStatusBg(currentJob.status)} ${getStatusColor(currentJob.status)}`}>
                    {getStatusText(currentJob.status)}
                  </span>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 divide-x divide-zinc-800">
                <div className="p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                      <Briefcase className="h-5 w-5 text-blue-500" />
                    </div>
                    <div>
                      <div className="text-2xl font-semibold tabular-nums">
                        {currentJob.vacancies_synced}
                      </div>
                      <div className="text-xs text-zinc-500">вакансий</div>
                    </div>
                  </div>
                </div>
                <div className="p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                      <Users className="h-5 w-5 text-green-500" />
                    </div>
                    <div>
                      <div className="text-2xl font-semibold tabular-nums">
                        {currentJob.applications_synced}
                      </div>
                      <div className="text-xs text-zinc-500">откликов</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress bar for running job */}
              {isJobRunning && (
                <div className="px-5 pb-5">
                  <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: '60%' }} />
                  </div>
                </div>
              )}

              {/* Errors */}
              {currentJob.errors && currentJob.errors.length > 0 && (
                <div className="p-4 mx-5 mb-5 rounded-lg bg-red-500/10 border border-red-500/20">
                  <div className="text-xs font-medium text-red-400 mb-2">Ошибки:</div>
                  <ul className="space-y-1">
                    {currentJob.errors.map((err, idx) => (
                      <li key={idx} className="text-xs text-red-300">{err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Last sync info (when no current job) */}
      {!currentJob && syncHistory.length > 0 && syncHistory[0].status === 'completed' && (
        <motion.div {...fadeIn}>
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium text-green-400">Последняя синхронизация успешна</div>
                <div className="text-xs text-green-500/70 mt-0.5">
                  {formatDate(syncHistory[0].completed_at)} — {syncHistory[0].vacancies_synced} вакансий, {syncHistory[0].applications_synced} откликов
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* History */}
      {syncHistory.length > 0 && (
        <motion.div {...fadeIn}>
          <Card>
            <CardContent className="p-0">
              <div className="px-5 py-4 border-b border-zinc-800">
                <div className="text-[13px] font-medium uppercase tracking-wide text-zinc-400">
                  История синхронизаций
                </div>
              </div>
              <div className="divide-y divide-zinc-800/50">
                {syncHistory.map((job) => (
                  <div
                    key={job.id}
                    className="px-5 py-4 flex items-center justify-between hover:bg-zinc-900/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {job.status === 'completed' ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : job.status === 'failed' ? (
                        <XCircle className="h-4 w-4 text-red-500" />
                      ) : ['processing', 'running'].includes(job.status) ? (
                        <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-zinc-500" />
                      )}
                      <div>
                        <div className="text-[13px] font-medium text-zinc-300">
                          {formatDate(job.created_at)}
                        </div>
                        <div className="text-xs text-zinc-500">
                          {job.vacancies_synced} вакансий • {job.applications_synced} откликов
                        </div>
                      </div>
                    </div>
                    <span className={`text-[11px] font-medium px-2 py-1 rounded ${getStatusBg(job.status)} ${getStatusColor(job.status)}`}>
                      {getStatusText(job.status)}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Empty state */}
      {syncHistory.length === 0 && !currentJob && (
        <motion.div {...fadeIn} className="text-center py-12">
          <div className="w-14 h-14 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center mx-auto mb-4">
            <RefreshCw className="h-6 w-6 text-zinc-500" />
          </div>
          <p className="text-zinc-400 text-sm mb-1">Синхронизаций пока нет</p>
          <p className="text-zinc-600 text-xs">Нажмите кнопку выше чтобы начать</p>
        </motion.div>
      )}
    </div>
  );
};

export default Sync;
