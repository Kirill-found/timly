/**
 * Страница тарифных планов
 * Design: Dark Industrial - минималистичный, утилитарный
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Check, Loader2, Minus } from 'lucide-react';
import apiClient from '@/services/api';
import type { SubscriptionPlan, Subscription } from '@/types';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

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
      // Фильтруем: только активные, исключаем trial (объединён с free)
      const activePlans = plansData
        .filter((p: SubscriptionPlan) => p.is_active !== false && p.plan_type !== 'trial')
        .sort((a: SubscriptionPlan, b: SubscriptionPlan) => (a.display_order ?? 0) - (b.display_order ?? 0));
      setPlans(activePlans);
      setCurrentSubscription(subscriptionData);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = (planType: string) => {
    navigate(`/checkout?plan=${planType}&period=${billingPeriod}`);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const getPlanPrice = (plan: SubscriptionPlan) => {
    const yearlyPrice = plan.pricing?.yearly ?? plan.price_yearly ?? 0;
    const monthlyPrice = plan.pricing?.monthly ?? plan.price_monthly ?? 0;
    return billingPeriod === 'yearly' ? yearlyPrice : monthlyPrice;
  };

  const getMonthlyEquivalent = (plan: SubscriptionPlan) => {
    const yearlyPrice = plan.pricing?.yearly ?? plan.price_yearly ?? 0;
    return Math.round(yearlyPrice / 12);
  };

  const isCurrentPlan = (planType: string) => {
    return currentSubscription?.plan?.plan_type === planType;
  };

  // Функции для каждого тарифа
  const getPlanFeatures = (plan: SubscriptionPlan) => {
    const planType = plan.plan_type;
    const maxAnalyses = plan.limits?.analyses_per_month ?? plan.max_analyses_per_month ?? 0;
    const maxExports = plan.limits?.exports_per_month ?? plan.max_export_per_month ?? 0;

    const features: { text: string; included: boolean }[] = [];

    // Анализы
    features.push({
      text: maxAnalyses >= 999999 ? 'Безлимит анализов' : `${maxAnalyses} анализов/мес`,
      included: true
    });

    // Загрузки
    if (planType === 'free') {
      features.push({ text: '10 загрузок резюме', included: true });
    } else if (planType === 'starter') {
      features.push({ text: '50 загрузок резюме', included: true });
    } else {
      features.push({ text: 'Безлимит загрузок', included: true });
    }

    // Экспорты
    features.push({
      text: maxExports >= 999999 ? 'Безлимит экспортов' : `${maxExports} экспортов/мес`,
      included: true
    });

    // Поиск по базе
    const hasSearch = planType === 'professional' || planType === 'enterprise';
    features.push({
      text: 'Поиск по базе резюме',
      included: hasSearch
    });

    // AI анализ
    features.push({
      text: 'Продвинутый AI',
      included: planType !== 'free'
    });

    // Поддержка
    features.push({
      text: 'Приоритетная поддержка',
      included: planType !== 'free'
    });

    // API
    if (planType === 'professional' || planType === 'enterprise') {
      features.push({ text: 'API доступ', included: true });
    }

    // Enterprise extras
    if (planType === 'enterprise') {
      features.push({ text: 'Персональный менеджер', included: true });
      features.push({ text: 'Кастомные интеграции', included: true });
    }

    return features;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-zinc-600 mx-auto mb-4" />
          <p className="text-zinc-500 text-sm">Загрузка тарифов...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <motion.h1
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-2xl font-semibold text-zinc-100 tracking-tight"
        >
          Тарифы
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-zinc-500 mt-2"
        >
          Выберите подходящий план
        </motion.p>

        {/* Period Toggle */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex justify-center mt-6"
        >
          <div className="inline-flex items-center p-1 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`px-4 py-1.5 rounded text-sm transition-all ${
                billingPeriod === 'monthly'
                  ? 'bg-zinc-700 text-zinc-100'
                  : 'text-zinc-500 hover:text-zinc-400'
              }`}
            >
              Месяц
            </button>
            <button
              onClick={() => setBillingPeriod('yearly')}
              className={`px-4 py-1.5 rounded text-sm transition-all flex items-center gap-2 ${
                billingPeriod === 'yearly'
                  ? 'bg-zinc-700 text-zinc-100'
                  : 'text-zinc-500 hover:text-zinc-400'
              }`}
            >
              Год
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-600 text-zinc-300">
                -20%
              </span>
            </button>
          </div>
        </motion.div>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {plans.map((plan, idx) => {
          const price = getPlanPrice(plan);
          const features = getPlanFeatures(plan);
          const current = isCurrentPlan(plan.plan_type);
          const isPopular = plan.plan_type === 'professional';
          const isEnterprise = plan.plan_type === 'enterprise';
          const monthlyEquivalent = billingPeriod === 'yearly' ? getMonthlyEquivalent(plan) : null;

          return (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 + 0.2 }}
            >
              <Card className={`h-full border-zinc-800 bg-zinc-900/50 relative ${
                isPopular ? 'ring-1 ring-zinc-600' : ''
              }`}>
                {/* Popular badge */}
                {isPopular && (
                  <div className="absolute -top-2.5 left-4">
                    <span className="text-[10px] uppercase tracking-wider px-2 py-1 bg-zinc-100 text-zinc-900 font-medium rounded">
                      Популярный
                    </span>
                  </div>
                )}

                <CardContent className="p-5 flex flex-col h-full">
                  {/* Plan name */}
                  <div className="mb-4">
                    <h3 className="text-lg font-medium text-zinc-100">
                      {plan.name}
                    </h3>
                    <p className="text-xs text-zinc-600 mt-0.5">
                      {plan.description}
                    </p>
                  </div>

                  {/* Price */}
                  <div className="mb-5 pb-5 border-b border-zinc-800">
                    {price === 0 ? (
                      <div className="flex items-baseline">
                        <span className="text-3xl font-semibold text-zinc-100 tabular-nums">0</span>
                        <span className="text-zinc-500 ml-1">₽</span>
                      </div>
                    ) : isEnterprise ? (
                      <div>
                        <span className="text-xl font-medium text-zinc-100">По запросу</span>
                      </div>
                    ) : (
                      <div>
                        <div className="flex items-baseline">
                          <span className="text-3xl font-semibold text-zinc-100 tabular-nums">
                            {formatPrice(billingPeriod === 'yearly' ? monthlyEquivalent! : price)}
                          </span>
                          <span className="text-zinc-500 ml-1">₽/мес</span>
                        </div>
                        {billingPeriod === 'yearly' && (
                          <p className="text-xs text-zinc-600 mt-1">
                            {formatPrice(price)} ₽ за год
                          </p>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Features */}
                  <ul className="space-y-2 mb-5 flex-1">
                    {features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        {feature.included ? (
                          <Check className="h-3.5 w-3.5 text-zinc-500 flex-shrink-0" />
                        ) : (
                          <Minus className="h-3.5 w-3.5 text-zinc-700 flex-shrink-0" />
                        )}
                        <span className={feature.included ? 'text-zinc-400' : 'text-zinc-700'}>
                          {feature.text}
                        </span>
                      </li>
                    ))}
                  </ul>

                  {/* Button */}
                  {current ? (
                    <Button
                      disabled
                      variant="outline"
                      className="w-full border-zinc-700 text-zinc-600 cursor-not-allowed"
                    >
                      Текущий план
                    </Button>
                  ) : isEnterprise ? (
                    <Button
                      onClick={() => window.open('https://t.me/timly_support_bot', '_blank')}
                      variant="outline"
                      className="w-full border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100"
                    >
                      Написать в Telegram
                    </Button>
                  ) : (
                    <Button
                      onClick={() => handleSelectPlan(plan.plan_type)}
                      className={`w-full ${
                        isPopular
                          ? 'bg-zinc-100 text-zinc-900 hover:bg-white'
                          : 'bg-zinc-800 text-zinc-100 hover:bg-zinc-700'
                      }`}
                    >
                      {price === 0 ? 'Начать бесплатно' : 'Выбрать'}
                    </Button>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Current subscription info */}
      {currentSubscription && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="border-zinc-800 bg-zinc-900/50">
            <CardContent className="p-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-zinc-500">Текущий план</p>
                  <p className="text-zinc-100 font-medium">{currentSubscription.plan.name}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm text-zinc-500">Использовано</p>
                    <p className="text-zinc-100 tabular-nums">
                      {currentSubscription.usage?.analyses?.used ?? currentSubscription.analyses_used_this_month ?? 0}
                      <span className="text-zinc-600"> / </span>
                      {currentSubscription.usage?.analyses?.limit ?? currentSubscription.plan.max_analyses_per_month ?? 0}
                    </p>
                  </div>
                  <div className="w-32 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-zinc-500 rounded-full"
                      style={{
                        width: `${Math.min(
                          ((currentSubscription.analyses_used_this_month ?? 0) /
                          (currentSubscription.plan.max_analyses_per_month ?? 1)) * 100,
                          100
                        )}%`
                      }}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Footer */}
      <div className="text-center text-sm text-zinc-600">
        <p>
          Вопросы?{' '}
          <a
            href="https://t.me/timly_support_bot"
            target="_blank"
            rel="noopener noreferrer"
            className="text-zinc-400 hover:text-zinc-300 transition-colors"
          >
            Напишите нам
          </a>
        </p>
      </div>
    </div>
  );
};

export default Pricing;
