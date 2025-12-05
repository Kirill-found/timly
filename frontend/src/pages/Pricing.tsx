/**
 * Страница тарифных планов
 * Отображение доступных планов подписки и возможность апгрейда
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '@/services/api';
import type { SubscriptionPlan, Subscription } from '@/types';

const Pricing: React.FC = () => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [currentSubscription, setCurrentSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [plansData, subscriptionData] = await Promise.all([
        apiClient.getSubscriptionPlans(),
        apiClient.getCurrentSubscription()
      ]);
      setPlans(plansData);
      setCurrentSubscription(subscriptionData);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = (planType: string) => {
    // Перенаправляем на страницу оформления заказа
    navigate(`/checkout?plan=${planType}&period=${billingPeriod}`);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getPlanPrice = (plan: SubscriptionPlan) => {
    // Поддержка новой и старой структуры API
    const yearlyPrice = plan.pricing?.yearly ?? plan.price_yearly ?? 0;
    const monthlyPrice = plan.pricing?.monthly ?? plan.price_monthly ?? 0;
    return billingPeriod === 'yearly' ? yearlyPrice : monthlyPrice;
  };

  const isCurrentPlan = (planType: string) => {
    return currentSubscription?.plan?.plan_type === planType;
  };

  const getPlanFeatures = (plan: SubscriptionPlan): string[] => {
    // Поддержка новой и старой структуры API
    const maxVacancies = plan.limits?.active_vacancies ?? plan.max_active_vacancies ?? 0;
    const maxAnalyses = plan.limits?.analyses_per_month ?? plan.max_analyses_per_month ?? 0;
    const maxExports = plan.limits?.exports_per_month ?? plan.max_export_per_month ?? 0;

    const features: string[] = [
      `${maxVacancies === 999999 ? 'Неограниченно' : maxVacancies} активных вакансий`,
      `${maxAnalyses === 999999 ? 'Неограниченно' : maxAnalyses} анализов в месяц`,
      `${maxExports === 999999 ? 'Неограниченно' : maxExports} экспортов в месяц`
    ];

    if (plan.features.basic_analysis) features.push('Базовый AI анализ');
    if (plan.features.advanced_ai) features.push('Продвинутый AI анализ');
    if (plan.features.priority_support) features.push('Приоритетная поддержка');
    if (plan.features.api_access) features.push('Доступ к API');
    if (plan.features.custom_integrations) features.push('Кастомные интеграции');
    if (plan.features.dedicated_manager) features.push('Персональный менеджер');

    return features;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка тарифных планов...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Заголовок */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Выберите подходящий тариф
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Начните с бесплатного плана и масштабируйтесь по мере роста
          </p>

          {/* Переключатель периода оплаты */}
          <div className="flex justify-center items-center gap-4">
            <span className={`text-sm font-medium ${billingPeriod === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Ежемесячно
            </span>
            <button
              onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'yearly' : 'monthly')}
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-indigo-600 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  billingPeriod === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-sm font-medium ${billingPeriod === 'yearly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Ежегодно
              <span className="ml-2 text-green-600 text-xs">Экономия до 20%</span>
            </span>
          </div>
        </div>

        {/* Карточки тарифов */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {plans.map((plan) => {
            const price = getPlanPrice(plan);
            const features = getPlanFeatures(plan);
            const current = isCurrentPlan(plan.plan_type);

            return (
              <div
                key={plan.id}
                className={`relative bg-white rounded-2xl shadow-lg overflow-hidden ${
                  plan.is_popular ? 'ring-2 ring-indigo-600' : ''
                }`}
              >
                {plan.is_popular && (
                  <div className="absolute top-0 right-0 bg-indigo-600 text-white px-4 py-1 text-xs font-semibold rounded-bl-lg">
                    Популярный
                  </div>
                )}

                <div className="p-8">
                  {/* Заголовок плана */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {plan.name}
                  </h3>

                  {/* Цена */}
                  <div className="mb-6">
                    {price === 0 ? (
                      <div className="text-4xl font-bold text-gray-900">
                        Бесплатно
                      </div>
                    ) : (
                      <>
                        <div className="text-4xl font-bold text-gray-900">
                          {formatPrice(price)}
                        </div>
                        <div className="text-sm text-gray-500">
                          {billingPeriod === 'yearly' ? '/ год' : '/ месяц'}
                        </div>
                      </>
                    )}
                  </div>

                  {/* Возможности */}
                  <ul className="space-y-3 mb-8">
                    {features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <svg
                          className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0"
                          fill="none"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-sm text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* Кнопка действия */}
                  {current ? (
                    <button
                      disabled
                      className="w-full bg-gray-100 text-gray-600 py-3 px-6 rounded-lg font-semibold cursor-not-allowed"
                    >
                      Текущий план
                    </button>
                  ) : (
                    <button
                      onClick={() => handleSelectPlan(plan.plan_type)}
                      className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${
                        plan.is_popular
                          ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                          : 'bg-gray-900 text-white hover:bg-gray-800'
                      }`}
                    >
                      {price === 0 ? 'Начать бесплатно' : 'Выбрать план'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Текущая подписка */}
        {currentSubscription && (
          <div className="mt-12 bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Ваша текущая подписка
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-500 mb-1">План</p>
                <p className="text-lg font-semibold text-gray-900">
                  {currentSubscription.plan.name}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Использовано анализов</p>
                <p className="text-lg font-semibold text-gray-900">
                  {currentSubscription.usage?.analyses?.used ?? currentSubscription.analyses_used_this_month ?? 0} / {currentSubscription.usage?.analyses?.limit ?? currentSubscription.plan.limits?.analyses_per_month ?? currentSubscription.plan.max_analyses_per_month ?? 0}
                </p>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full"
                    style={{
                      width: `${currentSubscription.usage?.analyses?.percentage ?? Math.min(
                        ((currentSubscription.analyses_used_this_month ?? 0) / (currentSubscription.plan.max_analyses_per_month ?? 1)) * 100,
                        100
                      )}%`
                    }}
                  />
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Использовано экспортов</p>
                <p className="text-lg font-semibold text-gray-900">
                  {currentSubscription.usage?.exports?.used ?? currentSubscription.exports_used_this_month ?? 0} / {currentSubscription.usage?.exports?.limit ?? currentSubscription.plan.limits?.exports_per_month ?? currentSubscription.plan.max_export_per_month ?? 0}
                </p>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full"
                    style={{
                      width: `${currentSubscription.usage?.exports?.percentage ?? Math.min(
                        ((currentSubscription.exports_used_this_month ?? 0) / (currentSubscription.plan.max_export_per_month ?? 1)) * 100,
                        100
                      )}%`
                    }}
                  />
                </div>
              </div>
            </div>
            <div className="mt-6 flex gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Вернуться в Dashboard
              </button>
            </div>
          </div>
        )}

        {/* FAQ или дополнительная информация */}
        <div className="mt-12 text-center">
          <p className="text-gray-600">
            Нужна помощь с выбором плана?{' '}
            <a href="mailto:support@timly.ru" className="text-indigo-600 hover:text-indigo-700 font-semibold">
              Свяжитесь с нами
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
