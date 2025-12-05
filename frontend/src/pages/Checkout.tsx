/**
 * Страница оформления подписки и оплаты
 * Показывает детали выбранного плана и предлагает способы оплаты
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiClient from '@/services/api';
import type { SubscriptionPlan, Subscription } from '@/types';

const Checkout: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const planType = searchParams.get('plan');
  const billingPeriod = searchParams.get('period') || 'monthly';

  const [plan, setPlan] = useState<SubscriptionPlan | null>(null);
  const [currentSubscription, setCurrentSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'yookassa' | 'crypto'>('card');

  useEffect(() => {
    if (!planType) {
      navigate('/pricing');
      return;
    }
    loadData();
  }, [planType]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [plansData, subscriptionData] = await Promise.all([
        apiClient.getSubscriptionPlans(),
        apiClient.getCurrentSubscription()
      ]);

      const selectedPlan = plansData.find(p => p.plan_type === planType);
      if (!selectedPlan) {
        navigate('/pricing');
        return;
      }

      setPlan(selectedPlan);
      setCurrentSubscription(subscriptionData);
    } catch (error) {
      console.error('Failed to load checkout data:', error);
      alert('Ошибка загрузки данных');
      navigate('/pricing');
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    if (!plan) return;

    try {
      setProcessing(true);

      const price = getPlanPrice();
      console.log('[CHECKOUT] handlePayment called', {
        planType: plan.plan_type,
        billingPeriod,
        price,
        plan: plan,
        pricing: plan.pricing
      });

      // Если план бесплатный (Trial или Free), просто обновляем подписку
      if (price === 0) {
        console.log('[CHECKOUT] FREE PLAN - Activating without payment');
        await apiClient.upgradeSubscription({
          plan_type: planType as any,
          duration_months: billingPeriod === 'yearly' ? 12 : 1
        });

        alert('Подписка успешно активирована!');
        navigate('/dashboard');
        return;
      }

      // Для платных планов создаем платеж в ЮKassa
      console.log('[CHECKOUT] PAID PLAN - Creating payment');
      const returnUrl = `${window.location.origin}/pricing`;
      const payment = await apiClient.createPayment(
        planType!,
        billingPeriod === 'yearly' ? 12 : 1,
        returnUrl
      );

      console.log('[CHECKOUT] Payment created, redirecting to:', payment.confirmation_url);
      // Перенаправляем на страницу оплаты ЮKassa
      window.location.href = payment.confirmation_url;

    } catch (error: any) {
      console.error('Payment failed:', error);
      const errorMessage = error.response?.data?.detail?.message || error.response?.data?.message || 'Ошибка при создании платежа';
      alert(errorMessage);
      setProcessing(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getPlanPrice = () => {
    if (!plan) return 0;
    const yearlyPrice = plan.pricing?.yearly ?? plan.price_yearly ?? 0;
    const monthlyPrice = plan.pricing?.monthly ?? plan.price_monthly ?? 0;
    return billingPeriod === 'yearly' ? yearlyPrice : monthlyPrice;
  };

  const getDurationMonths = () => {
    return billingPeriod === 'yearly' ? 12 : 1;
  };

  const getMonthlyPrice = () => {
    if (!plan) return 0;
    const price = getPlanPrice();
    return billingPeriod === 'yearly' ? price / 12 : price;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка...</p>
        </div>
      </div>
    );
  }

  if (!plan) {
    return null;
  }

  const price = getPlanPrice();
  const isFree = price === 0;

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Заголовок */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/pricing')}
            className="text-indigo-600 hover:text-indigo-700 font-medium mb-4 flex items-center"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Назад к тарифам
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Оформление подписки</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Левая колонка - Детали заказа */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Детали подписки</h2>

              <div className="border-b border-gray-200 pb-4 mb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{plan.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">{plan.description}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">
                      {isFree ? 'Бесплатно' : formatPrice(price)}
                    </div>
                    {!isFree && (
                      <div className="text-sm text-gray-500">
                        {billingPeriod === 'yearly' ? 'за год' : 'за месяц'}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Что входит в план */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">Что входит в подписку:</h4>
                <ul className="space-y-2">
                  <li className="flex items-start">
                    <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm text-gray-700">
                      {plan.max_active_vacancies === -1 ? 'Неограниченно' : plan.max_active_vacancies} активных вакансий
                    </span>
                  </li>
                  <li className="flex items-start">
                    <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm text-gray-700">
                      {plan.max_analyses_per_month === -1 ? 'Неограниченно' : plan.max_analyses_per_month} анализов в месяц
                    </span>
                  </li>
                  <li className="flex items-start">
                    <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm text-gray-700">
                      {plan.max_export_per_month === -1 ? 'Неограниченно' : plan.max_export_per_month} экспортов в месяц
                    </span>
                  </li>
                  {plan.features?.advanced_ai && (
                    <li className="flex items-start">
                      <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-sm text-gray-700">Продвинутый AI анализ</span>
                    </li>
                  )}
                  {plan.features?.priority_support && (
                    <li className="flex items-start">
                      <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-sm text-gray-700">Приоритетная поддержка</span>
                    </li>
                  )}
                </ul>
              </div>

              {billingPeriod === 'yearly' && !isFree && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-start">
                    <svg className="h-5 w-5 text-green-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <p className="text-sm font-medium text-green-800">Выгодное предложение</p>
                      <p className="text-sm text-green-700 mt-1">
                        Годовая подписка = {formatPrice(getMonthlyPrice())}/мес. Экономия до 20%!
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Способы оплаты (только для платных планов) */}
            {!isFree && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Способ оплаты</h2>

                <div className="space-y-3">
                  {/* Банковская карта */}
                  <label className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                    paymentMethod === 'card' ? 'border-indigo-600 bg-indigo-50' : 'border-gray-200 hover:border-gray-300'
                  }`}>
                    <input
                      type="radio"
                      name="payment"
                      value="card"
                      checked={paymentMethod === 'card'}
                      onChange={(e) => setPaymentMethod(e.target.value as any)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                    />
                    <div className="ml-3 flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">Банковская карта</span>
                        <div className="flex space-x-2">
                          <img src="https://upload.wikimedia.org/wikipedia/commons/0/04/Visa.svg" alt="Visa" className="h-6" />
                          <img src="https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg" alt="Mastercard" className="h-6" />
                          <img src="https://upload.wikimedia.org/wikipedia/commons/a/a3/Mir_payment_system_logo.svg" alt="Mir" className="h-6" />
                        </div>
                      </div>
                      <p className="text-sm text-gray-500 mt-1">Visa, Mastercard, Мир</p>
                    </div>
                  </label>

                  {/* ЮKassa */}
                  <label className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                    paymentMethod === 'yookassa' ? 'border-indigo-600 bg-indigo-50' : 'border-gray-200 hover:border-gray-300'
                  }`}>
                    <input
                      type="radio"
                      name="payment"
                      value="yookassa"
                      checked={paymentMethod === 'yookassa'}
                      onChange={(e) => setPaymentMethod(e.target.value as any)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                    />
                    <div className="ml-3">
                      <span className="font-medium text-gray-900">ЮKassa</span>
                      <p className="text-sm text-gray-500 mt-1">Электронные кошельки, СБП</p>
                    </div>
                  </label>

                  {/* Криптовалюта */}
                  <label className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                    paymentMethod === 'crypto' ? 'border-indigo-600 bg-indigo-50' : 'border-gray-200 hover:border-gray-300'
                  }`}>
                    <input
                      type="radio"
                      name="payment"
                      value="crypto"
                      checked={paymentMethod === 'crypto'}
                      onChange={(e) => setPaymentMethod(e.target.value as any)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                    />
                    <div className="ml-3">
                      <span className="font-medium text-gray-900">Криптовалюта</span>
                      <p className="text-sm text-gray-500 mt-1">BTC, ETH, USDT</p>
                    </div>
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Правая колонка - Итого */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Итого</h2>

              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">План:</span>
                  <span className="font-medium text-gray-900">{plan.name}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Период:</span>
                  <span className="font-medium text-gray-900">
                    {billingPeriod === 'yearly' ? '12 месяцев' : '1 месяц'}
                  </span>
                </div>
                {!isFree && billingPeriod === 'yearly' && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Цена в месяц:</span>
                    <span className="font-medium text-gray-900">{formatPrice(getMonthlyPrice())}</span>
                  </div>
                )}
              </div>

              <div className="border-t border-gray-200 pt-4 mb-6">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold text-gray-900">К оплате:</span>
                  <span className="text-2xl font-bold text-indigo-600">
                    {isFree ? 'Бесплатно' : formatPrice(price)}
                  </span>
                </div>
              </div>

              <button
                onClick={handlePayment}
                disabled={processing}
                className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? 'Обработка...' : isFree ? 'Активировать план' : 'Перейти к оплате'}
              </button>

              <p className="text-xs text-gray-500 text-center mt-4">
                Нажимая на кнопку, вы соглашаетесь с{' '}
                <a href="#" className="text-indigo-600 hover:text-indigo-700">
                  условиями использования
                </a>
                {' '}и{' '}
                <a href="#" className="text-indigo-600 hover:text-indigo-700">
                  политикой конфиденциальности
                </a>
              </p>

              {!isFree && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="flex items-start text-sm text-gray-600">
                    <svg className="h-5 w-5 text-gray-400 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    <span>Безопасная оплата. Данные защищены SSL-шифрованием.</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
