/**
 * AnalysisLimitsDisplay - Отображение лимитов анализа
 * Design: Dark Industrial - минималистичный
 */
import React, { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
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
    const interval = setInterval(loadLimits, 10000);
    return () => clearInterval(interval);
  }, []);

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

  // Безлимитный тариф
  if (limits.is_unlimited) {
    return (
      <div className="flex items-center justify-between p-4 bg-card border border-zinc-800 rounded-lg">
        <div>
          <div className="text-sm font-medium text-zinc-200">Безлимитный тариф</div>
          <div className="text-xs text-zinc-500 mt-0.5">
            Использовано: {limits.analyses_used}
          </div>
        </div>
        <div className="text-xs text-green-500">∞</div>
      </div>
    );
  }

  const usagePercent = Math.round((limits.analyses_used / limits.analyses_limit) * 100);
  const isLow = limits.analyses_remaining < limits.analyses_limit * 0.2;
  const isCritical = limits.analyses_remaining < 10;

  return (
    <div className={`p-4 rounded-lg border ${
      isCritical
        ? 'bg-red-500/5 border-red-500/20'
        : isLow
        ? 'bg-amber-500/5 border-amber-500/20'
        : 'bg-card border-zinc-800'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className={`text-sm font-medium ${
            isCritical ? 'text-red-400' : isLow ? 'text-amber-400' : 'text-zinc-200'
          }`}>
            Осталось: {limits.analyses_remaining}
          </div>
          <div className="text-xs text-zinc-500 mt-0.5">
            {limits.analyses_used} / {limits.analyses_limit}
          </div>
        </div>
        <div className={`text-lg font-semibold tabular-nums ${
          isCritical ? 'text-red-400' : isLow ? 'text-amber-400' : 'text-zinc-400'
        }`}>
          {usagePercent}%
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${
            isCritical ? 'bg-red-500' : isLow ? 'bg-amber-500' : 'bg-zinc-500'
          }`}
          style={{ width: `${usagePercent}%` }}
        />
      </div>

      {/* Reset date */}
      {limits.reset_date && (
        <div className="text-[11px] text-zinc-600 mt-2">
          Обновление: {new Date(limits.reset_date).toLocaleDateString('ru-RU')}
        </div>
      )}
    </div>
  );
};
