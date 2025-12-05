/**
 * Компонент для отображения оставшихся анализов согласно тарифному плану
 */
import React, { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import { Card, CardContent } from '@/components/ui/card';
import { Brain, TrendingUp, AlertTriangle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { useApp } from '@/store/AppContext';

interface LimitsCheck {
  analyses_remaining: number;
  analyses_used: number;
  analyses_limit: number;
  is_unlimited: boolean;
  reset_date: string | null;
}

export const AnalysisLimitsDisplay: React.FC = () => {
  const app = useApp();
  const [limits, setLimits] = useState<LimitsCheck | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLimits();
    // Обновляем каждые 10 секунд (быстрее для отслеживания анализа)
    const interval = setInterval(loadLimits, 10000);
    return () => clearInterval(interval);
  }, []);

  // Обновляем лимиты при изменении прогресса анализа
  useEffect(() => {
    if (app.activeAnalysis) {
      loadLimits();
    }
  }, [app.activeAnalysis?.analyzed]);

  const loadLimits = async () => {
    try {
      const data = await apiClient.checkLimits();
      setLimits(data);
    } catch (err) {
      console.error('Error loading limits:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !limits) {
    return null;
  }

  if (limits.is_unlimited) {
    return (
      <Card className="border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Brain className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <div className="font-semibold text-purple-900">Безлимитный анализ</div>
                <div className="text-sm text-purple-700">
                  Использовано: {limits.analyses_used} анализов
                </div>
              </div>
            </div>
            <TrendingUp className="h-6 w-6 text-purple-600" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const usagePercent = (limits.analyses_used / limits.analyses_limit) * 100;
  const isLowRemaining = limits.analyses_remaining < limits.analyses_limit * 0.2;
  const isAlmostOut = limits.analyses_remaining < 10;

  return (
    <Card className={`${
      isAlmostOut
        ? 'border-red-200 bg-gradient-to-r from-red-50 to-orange-50'
        : isLowRemaining
        ? 'border-yellow-200 bg-gradient-to-r from-yellow-50 to-orange-50'
        : 'border-blue-200 bg-gradient-to-r from-blue-50 to-cyan-50'
    }`}>
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${
                isAlmostOut
                  ? 'bg-red-100'
                  : isLowRemaining
                  ? 'bg-yellow-100'
                  : 'bg-blue-100'
              }`}>
                {isAlmostOut || isLowRemaining ? (
                  <AlertTriangle className={`h-5 w-5 ${
                    isAlmostOut ? 'text-red-600' : 'text-yellow-600'
                  }`} />
                ) : (
                  <Brain className="h-5 w-5 text-blue-600" />
                )}
              </div>
              <div>
                <div className={`font-semibold ${
                  isAlmostOut
                    ? 'text-red-900'
                    : isLowRemaining
                    ? 'text-yellow-900'
                    : 'text-blue-900'
                }`}>
                  Анализов осталось: {limits.analyses_remaining}
                </div>
                <div className={`text-sm ${
                  isAlmostOut
                    ? 'text-red-700'
                    : isLowRemaining
                    ? 'text-yellow-700'
                    : 'text-blue-700'
                }`}>
                  Использовано: {limits.analyses_used} из {limits.analyses_limit}
                </div>
              </div>
            </div>
            <div className={`text-2xl font-bold ${
              isAlmostOut
                ? 'text-red-600'
                : isLowRemaining
                ? 'text-yellow-600'
                : 'text-blue-600'
            }`}>
              {Math.round(usagePercent)}%
            </div>
          </div>

          <Progress
            value={usagePercent}
            className={`h-2 ${
              isAlmostOut
                ? '[&>div]:bg-red-500'
                : isLowRemaining
                ? '[&>div]:bg-yellow-500'
                : '[&>div]:bg-blue-500'
            }`}
          />

          {limits.reset_date && (
            <div className="text-xs text-gray-600 text-center">
              Лимит обновится: {new Date(limits.reset_date).toLocaleDateString('ru-RU')}
            </div>
          )}

          {isAlmostOut && (
            <div className="text-xs text-red-600 font-medium text-center">
              ⚠️ Анализы заканчиваются! Рассмотрите обновление тарифного плана
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
