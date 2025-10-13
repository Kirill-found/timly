/**
 * Виджет подписки для отображения на Dashboard
 * Показывает текущий план, использование лимитов и ссылку на upgrade
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '@/services/api';
import type { Subscription, LimitsCheck } from '@/types';

const SubscriptionWidget: React.FC = () => {
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [limits, setLimits] = useState<LimitsCheck | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      setError(null);
      const [subscriptionData, limitsData] = await Promise.all([
        apiClient.getCurrentSubscription(),
        apiClient.checkLimits()
      ]);
      setSubscription(subscriptionData);
      setLimits(limitsData);
    } catch (error: any) {
      console.error('Failed to load subscription data:', error);
      setError(error?.response?.data?.detail?.message || 'Не удалось загрузить данные подписки');
    } finally {
      setLoading(false);
    }
  };

  const getUsagePercentage = (used: number, max: number) => {
    if (max >= 999999) return 0; // Unlimited
    if (max === 0) return 0;
    return Math.min((used / max) * 100, 100);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-2 bg-gray-200 rounded mb-2"></div>
          <div className="h-2 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600">
          <p className="font-semibold mb-2">Ошибка загрузки подписки</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={() => loadSubscriptionData()}
            className="mt-3 text-sm text-indigo-600 hover:text-indigo-800 underline"
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">Подписка не найдена</p>
        <button
          onClick={() => navigate('/pricing')}
          className="mt-3 text-sm text-indigo-600 hover:text-indigo-800 underline"
        >
          Выбрать план
        </button>
      </div>
    );
  }

  // Получаем данные с поддержкой новой и старой структуры API
  const analysesUsed = subscription.usage?.analyses?.used ?? subscription.analyses_used_this_month ?? 0;
  const analysesLimit = subscription.plan.limits?.analyses_per_month ?? subscription.plan.max_analyses_per_month ?? 0;

  const exportsUsed = subscription.usage?.exports?.used ?? subscription.exports_used_this_month ?? 0;
  const exportsLimit = subscription.plan.limits?.exports_per_month ?? subscription.plan.max_export_per_month ?? 0;

  const vacanciesLimit = subscription.plan.limits?.active_vacancies ?? subscription.plan.max_active_vacancies ?? 0;

  const analysisPercentage = getUsagePercentage(analysesUsed, analysesLimit);
  const exportPercentage = getUsagePercentage(exportsUsed, exportsLimit);

  const isFree = subscription.plan.plan_type === 'free';
  const hasWarnings = !limits?.can_analyze || !limits?.can_export;

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const periodEnd = subscription.period?.expires_at ?? subscription.current_period_end;

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Заголовок */}
      <div className={`p-6 ${isFree ? 'bg-gradient-to-r from-gray-500 to-gray-700' : 'bg-gradient-to-r from-indigo-500 to-purple-600'}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-white/80 mb-1">Текущий план</p>
            <h3 className="text-2xl font-bold text-white">
              {subscription.plan.name}
            </h3>
          </div>
          {isFree && (
            <button
              onClick={() => navigate('/pricing')}
              className="px-4 py-2 bg-white text-gray-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-sm"
            >
              Upgrade
            </button>
          )}
        </div>
      </div>

      {/* Основной контент */}
      <div className="p-6 space-y-6">
        {/* Предупреждения о лимитах */}
        {hasWarnings && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <svg
                className="h-5 w-5 text-yellow-600 mr-3 mt-0.5 flex-shrink-0"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-yellow-800 mb-1">
                  Лимиты исчерпаны
                </h4>
                <ul className="text-sm text-yellow-700 space-y-1">
                  {!limits?.can_analyze && limits?.messages?.analyses && <li>• {limits.messages.analyses}</li>}
                  {!limits?.can_export && limits?.messages?.exports && <li>• {limits.messages.exports}</li>}
                  {!limits?.can_add_vacancy && limits?.messages?.vacancies && <li>• {limits.messages.vacancies}</li>}
                </ul>
                <button
                  onClick={() => navigate('/pricing')}
                  className="mt-2 text-sm font-semibold text-yellow-800 hover:text-yellow-900 underline"
                >
                  Обновить план
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Использование анализов */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Анализы</span>
            <span className="text-sm text-gray-600">
              {analysesUsed} / {analysesLimit >= 999999 ? '∞' : analysesLimit}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${getUsageColor(analysisPercentage)}`}
              style={{ width: `${analysisPercentage}%` }}
            />
          </div>
        </div>

        {/* Использование экспортов */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Экспорты</span>
            <span className="text-sm text-gray-600">
              {exportsUsed} / {exportsLimit >= 999999 ? '∞' : exportsLimit}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${getUsageColor(exportPercentage)}`}
              style={{ width: `${exportPercentage}%` }}
            />
          </div>
        </div>

        {/* Активные вакансии */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700">Активные вакансии</span>
            <span className="text-sm text-gray-600">
              Лимит: {vacanciesLimit >= 999999 ? '∞' : vacanciesLimit}
            </span>
          </div>
        </div>

        {/* Период действия */}
        {periodEnd && (
          <div className="pt-4 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              Период обновления: {formatDate(periodEnd)}
            </div>
          </div>
        )}

        {/* Действия */}
        <div className="pt-4 border-t border-gray-200 flex gap-3">
          <button
            onClick={() => navigate('/pricing')}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-semibold"
          >
            {isFree ? 'Выбрать план' : 'Изменить план'}
          </button>
          <button
            onClick={() => window.open('mailto:support@timly.ru', '_blank')}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-semibold"
          >
            Помощь
          </button>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionWidget;
