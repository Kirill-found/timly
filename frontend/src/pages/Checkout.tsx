/**
 * Страница оформления подписки и оплаты
 * Оплата через ЮKassa (карты, СБП, кошельки)
 * Design: Dark Industrial
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Check, Loader2, Lock, CreditCard, Smartphone, Wallet } from 'lucide-react';
import apiClient from '@/services/api';
import type { SubscriptionPlan, Subscription } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const Checkout: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const planType = searchParams.get('plan');
  const billingPeriod = searchParams.get('period') || 'monthly';

  const [plan, setPlan] = useState<SubscriptionPlan | null>(null);
  const [currentSubscription, setCurrentSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

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

      // Если план бесплатный (Trial или Free), просто обновляем подписку
      if (price === 0) {
        await apiClient.upgradeSubscription({
          plan_type: planType as any,
          duration_months: billingPeriod === 'yearly' ? 12 : 1
        });

        alert('Подписка успешно активирована!');
        navigate('/dashboard');
        return;
      }

      // Для платных планов создаем платеж в ЮKassa
      const returnUrl = `${window.location.origin}/pricing`;
      const payment = await apiClient.createPayment(
        planType!,
        billingPeriod === 'yearly' ? 12 : 1,
        returnUrl
      );

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
    // Trial and free plans should always be treated as free (price 0)
    if (plan.plan_type === 'trial' || plan.plan_type === 'free') return 0;
    const yearlyPrice = plan.pricing?.yearly ?? plan.price_yearly ?? 0;
    const monthlyPrice = plan.pricing?.monthly ?? plan.price_monthly ?? 0;
    const price = billingPeriod === 'yearly' ? yearlyPrice : monthlyPrice;
    // Negative prices are invalid, treat as free
    return price < 0 ? 0 : price;
  };

  const getMonthlyPrice = () => {
    if (!plan) return 0;
    const price = getPlanPrice();
    return billingPeriod === 'yearly' ? price / 12 : price;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="h-10 w-10 animate-spin text-zinc-500 mx-auto mb-4" />
          <p className="text-zinc-500">Загрузка...</p>
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
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <button
          onClick={() => navigate('/pricing')}
          className="text-zinc-400 hover:text-zinc-200 font-medium mb-4 flex items-center gap-1 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Назад к тарифам
        </button>
        <h1 className="text-2xl font-semibold text-zinc-100 tracking-tight">Оформление подписки</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Левая колонка - Детали заказа */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="border-zinc-800 bg-zinc-900/50">
              <CardHeader className="border-b border-zinc-800">
                <CardTitle className="text-zinc-100">Детали подписки</CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="border-b border-zinc-800 pb-4 mb-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-medium text-zinc-100">{plan.name}</h3>
                      <p className="text-sm text-zinc-500 mt-1">{plan.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-zinc-100 tabular-nums">
                        {isFree ? 'Бесплатно' : formatPrice(price)}
                      </div>
                      {!isFree && (
                        <div className="text-sm text-zinc-500">
                          {billingPeriod === 'yearly' ? 'за год' : 'за месяц'}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Что входит в план */}
                <div className="mb-6">
                  <h4 className="font-medium text-zinc-200 mb-3">Что входит в подписку:</h4>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-zinc-400">
                        {plan.max_active_vacancies === -1 ? 'Неограниченно' : plan.max_active_vacancies} активных вакансий
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-zinc-400">
                        {plan.max_analyses_per_month === -1 ? 'Неограниченно' : plan.max_analyses_per_month} анализов в месяц
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-zinc-400">
                        {plan.max_export_per_month === -1 ? 'Неограниченно' : plan.max_export_per_month} экспортов в месяц
                      </span>
                    </li>
                    {plan.features?.advanced_ai && (
                      <li className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-zinc-400">Продвинутый AI анализ</span>
                      </li>
                    )}
                    {plan.features?.priority_support && (
                      <li className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-zinc-400">Приоритетная поддержка</span>
                      </li>
                    )}
                  </ul>
                </div>

                {billingPeriod === 'yearly' && !isFree && (
                  <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                    <div className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-green-400 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-green-400">Выгодное предложение</p>
                        <p className="text-sm text-green-400/80 mt-1">
                          Годовая подписка = {formatPrice(getMonthlyPrice())}/мес. Экономия до 20%!
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Способы оплаты через ЮKassa */}
          {!isFree && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card className="border-zinc-800 bg-zinc-900/50">
                <CardHeader className="border-b border-zinc-800">
                  <CardTitle className="text-zinc-100">Способы оплаты</CardTitle>
                  <p className="text-sm text-zinc-500">Безопасная оплата через ЮKassa</p>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 border border-zinc-700 rounded-lg bg-zinc-800/30 text-center">
                      <CreditCard className="h-6 w-6 text-zinc-400 mx-auto mb-2" />
                      <p className="text-sm font-medium text-zinc-200">Банковская карта</p>
                      <p className="text-xs text-zinc-500 mt-1">Visa, Mastercard, Мир</p>
                    </div>
                    <div className="p-4 border border-zinc-700 rounded-lg bg-zinc-800/30 text-center">
                      <Smartphone className="h-6 w-6 text-zinc-400 mx-auto mb-2" />
                      <p className="text-sm font-medium text-zinc-200">СБП</p>
                      <p className="text-xs text-zinc-500 mt-1">Оплата по QR-коду</p>
                    </div>
                    <div className="p-4 border border-zinc-700 rounded-lg bg-zinc-800/30 text-center">
                      <Wallet className="h-6 w-6 text-zinc-400 mx-auto mb-2" />
                      <p className="text-sm font-medium text-zinc-200">Кошельки</p>
                      <p className="text-xs text-zinc-500 mt-1">ЮMoney и другие</p>
                    </div>
                  </div>
                  <p className="text-xs text-zinc-600 mt-4 text-center">
                    Выберите удобный способ оплаты на следующем шаге
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>

        {/* Правая колонка - Итого */}
        <div className="lg:col-span-1">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="border-zinc-800 bg-zinc-900/50 sticky top-6">
              <CardHeader className="border-b border-zinc-800">
                <CardTitle className="text-zinc-100">Итого</CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-500">План:</span>
                    <span className="font-medium text-zinc-200">{plan.name}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-zinc-500">Период:</span>
                    <span className="font-medium text-zinc-200">
                      {billingPeriod === 'yearly' ? '12 месяцев' : '1 месяц'}
                    </span>
                  </div>
                  {!isFree && billingPeriod === 'yearly' && (
                    <div className="flex justify-between text-sm">
                      <span className="text-zinc-500">Цена в месяц:</span>
                      <span className="font-medium text-zinc-200 tabular-nums">{formatPrice(getMonthlyPrice())}</span>
                    </div>
                  )}
                </div>

                <div className="border-t border-zinc-800 pt-4 mb-6">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-semibold text-zinc-200">К оплате:</span>
                    <span className="text-2xl font-bold text-zinc-100 tabular-nums">
                      {isFree ? 'Бесплатно' : formatPrice(price)}
                    </span>
                  </div>
                </div>

                <Button
                  onClick={handlePayment}
                  disabled={processing}
                  className="w-full bg-zinc-100 text-zinc-900 hover:bg-white font-medium"
                  size="lg"
                >
                  {processing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Переход к оплате...
                    </>
                  ) : isFree ? (
                    'Активировать план'
                  ) : (
                    'Оплатить через ЮKassa'
                  )}
                </Button>

                <p className="text-xs text-zinc-600 text-center mt-4">
                  Нажимая на кнопку, вы соглашаетесь с{' '}
                  <a href="#" className="text-zinc-400 hover:text-zinc-300">
                    условиями использования
                  </a>
                  {' '}и{' '}
                  <a href="#" className="text-zinc-400 hover:text-zinc-300">
                    политикой конфиденциальности
                  </a>
                </p>

                {!isFree && (
                  <div className="mt-6 pt-6 border-t border-zinc-800">
                    <div className="flex items-start text-sm text-zinc-500">
                      <Lock className="h-4 w-4 text-zinc-600 mr-2 mt-0.5 flex-shrink-0" />
                      <span>Безопасная оплата через ЮKassa. Данные карты защищены SSL-шифрованием.</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
