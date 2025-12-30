/**
 * Settings - Настройки
 * Design: Dark Industrial - идентично Dashboard
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle,
  XCircle,
  ExternalLink,
  Loader2,
  RefreshCw,
  Unlink,
  AlertTriangle,
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/services/api';
import { useAuth } from '@/store/AuthContext';

const Settings: React.FC = () => {
  const { user, refreshProfile } = useAuth();
  const [isConnectingHH, setIsConnectingHH] = useState(false);
  const [isDisconnectingHH, setIsDisconnectingHH] = useState(false);
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleOAuthConnect = () => {
    setIsConnectingHH(true);
    const clientId = 'H1F4CKSVJ1360RB6KTOAG6NRQD8AQVLFDRLIPSLJ4N3I5164VRLC9JJU45AUVLTH';
    const redirectUri = 'https://timly-hr.ru/auth/hh-callback';
    const authUrl = `https://hh.ru/oauth/authorize?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}`;
    window.location.href = authUrl;
  };

  const handleDisconnectHH = async () => {
    try {
      setIsDisconnectingHH(true);
      setError(null);
      await apiClient.disconnectHH();
      setSuccessMessage('HH.ru отключён');
      setShowDisconnectConfirm(false);
      await refreshProfile();
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || 'Ошибка отключения HH.ru');
    } finally {
      setIsDisconnectingHH(false);
    }
  };

  useEffect(() => {
    const code = sessionStorage.getItem('hh_oauth_code');
    if (code) {
      sessionStorage.removeItem('hh_oauth_code');
      setIsConnectingHH(true);
      setError(null);
      apiClient.exchangeHHCode(code)
        .then(async (response) => {
          if (response.data?.token_saved && response.data?.token_valid) {
            setSuccessMessage('HH.ru подключён');
            await refreshProfile();
          } else {
            setError('Не удалось подключить HH.ru');
          }
        })
        .catch((err: any) => {
          setError(err.response?.data?.detail?.message || 'Ошибка подключения');
        })
        .finally(() => setIsConnectingHH(false));
    }
  }, [refreshProfile]);

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const subscription = {
    plan: user?.subscription_plan || 'free',
    planName: user?.subscription_plan === 'pro' ? 'Pro' : user?.subscription_plan === 'business' ? 'Business' : 'Free',
    analysisUsed: user?.analysis_count || 0,
    analysisLimit: user?.subscription_plan === 'pro' ? 500 : user?.subscription_plan === 'business' ? 2000 : 50,
    vacanciesUsed: user?.vacancies_count || 0,
    vacanciesLimit: user?.subscription_plan === 'pro' ? 50 : user?.subscription_plan === 'business' ? 200 : 5,
  };

  const fadeIn = {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div {...fadeIn}>
        <h1 className="text-xl font-semibold text-zinc-100">Настройки</h1>
        <p className="text-sm text-zinc-500 mt-1">Профиль и интеграции</p>
      </motion.div>

      {/* Notifications */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3"
          >
            <XCircle className="w-4 h-4 flex-shrink-0" />
            {error}
            <button onClick={() => setError(null)} className="ml-auto text-red-400/60 hover:text-red-400">
              <XCircle className="w-4 h-4" />
            </button>
          </motion.div>
        )}
        {successMessage && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm flex items-center gap-3"
          >
            <CheckCircle className="w-4 h-4 flex-shrink-0" />
            {successMessage}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Disconnect Confirmation Modal */}
      <AnimatePresence>
        {showDisconnectConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
            onClick={() => setShowDisconnectConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-2xl"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-500" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-zinc-100">Отключить HH.ru?</h3>
                  <p className="text-sm text-zinc-500">Это действие можно отменить</p>
                </div>
              </div>
              <p className="text-sm text-zinc-400 mb-6">После отключения вы не сможете загружать отклики с HH.ru. Вы сможете переподключить аккаунт в любой момент.</p>
              <div className="flex gap-3">
                <Button variant="outline" className="flex-1 h-11 border-zinc-700 text-zinc-300 hover:bg-zinc-800" onClick={() => setShowDisconnectConfirm(false)}>Отмена</Button>
                <Button className="flex-1 h-11 bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20" onClick={handleDisconnectHH} disabled={isDisconnectingHH}>
                  {isDisconnectingHH ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Unlink className="w-4 h-4 mr-2" />Отключить</>}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Profile Stats - как в Dashboard */}
      <motion.div {...fadeIn} className="grid grid-cols-1 md:grid-cols-4 gap-px bg-zinc-800 border border-zinc-800 rounded-lg overflow-hidden">
        <div className="bg-card p-5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
            Email
          </div>
          <div className="text-xl font-semibold tracking-tight truncate">
            {user?.email || '—'}
          </div>
        </div>

        <div className="bg-card p-5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
            Компания
          </div>
          <div className="text-xl font-semibold tracking-tight truncate">
            {user?.company_name || '—'}
          </div>
        </div>

        <div className="bg-card p-5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
            Роль
          </div>
          <div className="text-xl font-semibold tracking-tight">
            {user?.role === 'admin' ? 'Админ' : 'Пользователь'}
          </div>
        </div>

        <div className="bg-card p-5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500 mb-2">
            Тариф
          </div>
          <div className="text-xl font-semibold tracking-tight">
            {subscription.planName}
          </div>
        </div>
      </motion.div>

      {/* Integrations */}
      <motion.div {...fadeIn}>
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-[13px] font-medium uppercase tracking-wide">
              Интеграции
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* HH.ru - Enhanced */}
              <div className={`p-5 rounded-xl border transition-all duration-300 ${user?.has_hh_token ? 'border-green-500/30 bg-gradient-to-br from-green-500/5 to-transparent' : 'border-zinc-800 bg-zinc-900/50 hover:border-zinc-700'}`}>
                <div className="flex items-center gap-4 mb-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-sm font-bold transition-all ${user?.has_hh_token ? 'bg-green-500/20 text-green-400 shadow-lg shadow-green-500/10' : 'bg-red-500/10 text-red-500'}`}>hh</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[15px] font-semibold text-zinc-100">HeadHunter</span>
                      {user?.has_hh_token && <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-500/10 text-green-400 border border-green-500/20"><span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />Активен</span>}
                    </div>
                    <div className="text-xs text-zinc-500 mt-0.5">{user?.has_hh_token ? 'Вакансии и отклики синхронизируются' : 'Подключите для загрузки откликов'}</div>
                  </div>
                </div>
                {user?.has_hh_token ? (
                  <div className="flex gap-2">
                    <Button onClick={handleOAuthConnect} disabled={isConnectingHH} size="sm" className="flex-1 h-9 bg-zinc-800 text-zinc-300 hover:bg-zinc-700 border border-zinc-700 font-medium">{isConnectingHH ? <Loader2 className="h-4 w-4 animate-spin" /> : <><RefreshCw className="h-3.5 w-3.5 mr-2" />Переподключить</>}</Button>
                    <Button onClick={() => setShowDisconnectConfirm(true)} size="sm" variant="ghost" className="h-9 px-3 text-zinc-500 hover:text-red-400 hover:bg-red-500/10"><Unlink className="h-4 w-4" /></Button>
                  </div>
                ) : (
                  <Button onClick={handleOAuthConnect} disabled={isConnectingHH} className="w-full h-10 bg-zinc-100 text-zinc-900 hover:bg-white font-medium">{isConnectingHH ? <Loader2 className="h-4 w-4 animate-spin" /> : <><ExternalLink className="h-4 w-4 mr-2" />Подключить HH.ru</>}</Button>
                )}
              </div>

              {/* Telegram */}
              <div className="p-5 rounded-lg border border-zinc-800 bg-zinc-900/50 opacity-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-sm font-bold text-blue-400">
                      TG
                    </div>
                    <div>
                      <div className="text-[13px] font-medium text-zinc-100">Telegram</div>
                      <div className="text-xs text-zinc-500 mt-0.5">Уведомления</div>
                    </div>
                  </div>
                  <span className="text-[11px] text-zinc-600 bg-zinc-800 px-2.5 py-1 rounded font-medium">
                    Скоро
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Limits - как в Analysis */}
      <motion.div {...fadeIn}>
        <Card>
          <CardHeader className="pb-0 flex flex-row items-center justify-between">
            <CardTitle className="text-[13px] font-medium uppercase tracking-wide">
              Лимиты
            </CardTitle>
            {subscription.plan === 'free' && (
              <Button
                variant="outline"
                size="sm"
                className="h-8 px-4 border-zinc-700 text-zinc-300 hover:bg-zinc-800 text-xs font-medium"
                onClick={() => window.open('https://timly-hr.ru/pricing', '_blank')}
              >
                Улучшить тариф
              </Button>
            )}
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Analysis */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
                    Анализы резюме
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-semibold tabular-nums">
                      {subscription.analysisLimit - subscription.analysisUsed}
                    </span>
                    <span className="text-sm text-zinc-500">из {subscription.analysisLimit}</span>
                  </div>
                </div>
                <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      subscription.analysisUsed / subscription.analysisLimit >= 0.9 ? 'bg-red-500' :
                      subscription.analysisUsed / subscription.analysisLimit >= 0.7 ? 'bg-amber-500' :
                      'bg-zinc-600'
                    }`}
                    style={{ width: `${(subscription.analysisUsed / subscription.analysisLimit) * 100}%` }}
                  />
                </div>
              </div>

              {/* Vacancies */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
                    Активные вакансии
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-semibold tabular-nums">
                      {subscription.vacanciesLimit - subscription.vacanciesUsed}
                    </span>
                    <span className="text-sm text-zinc-500">из {subscription.vacanciesLimit}</span>
                  </div>
                </div>
                <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      subscription.vacanciesUsed / subscription.vacanciesLimit >= 0.9 ? 'bg-red-500' :
                      subscription.vacanciesUsed / subscription.vacanciesLimit >= 0.7 ? 'bg-amber-500' :
                      'bg-zinc-600'
                    }`}
                    style={{ width: `${(subscription.vacanciesUsed / subscription.vacanciesLimit) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Warning */}
            {(subscription.analysisUsed / subscription.analysisLimit) >= 0.8 && (
              <div className="mt-6 p-4 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm">
                Использовано более 80% лимита анализов
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default Settings;
