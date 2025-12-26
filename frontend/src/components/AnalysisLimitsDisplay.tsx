/**
 * AnalysisLimitsDisplay - Отображение лимитов анализа
 * Design: Dark Industrial - сегментированный прогресс, индустриальная эстетика
 */
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
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

  const usagePercent = Math.round((limits.analyses_used / limits.analyses_limit) * 100);
  const remainingPercent = 100 - usagePercent;
  const isLow = limits.analyses_remaining < limits.analyses_limit * 0.2;
  const isCritical = limits.analyses_remaining < 10;

  // Безлимитный тариф
  if (limits.is_unlimited) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-xl border border-emerald-500/20 bg-gradient-to-br from-emerald-950/30 via-zinc-900 to-zinc-900"
      >
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-emerald-500/5 via-transparent to-transparent" />

        <div className="relative p-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-medium uppercase tracking-wider text-emerald-400">
                  Безлимитный тариф
                </span>
              </div>
              <div className="text-3xl font-bold mt-2 tabular-nums text-zinc-100">
                {limits.analyses_used.toLocaleString('ru-RU')}
                <span className="text-sm font-normal text-zinc-500 ml-2">использовано</span>
              </div>
            </div>
            <div className="text-5xl font-black text-emerald-500/20">∞</div>
          </div>
        </div>
      </motion.div>
    );
  }

  // Цвет в зависимости от состояния
  const getStatusColor = () => {
    if (isCritical) return { primary: 'rgb(239, 68, 68)', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.3)' };
    if (isLow) return { primary: 'rgb(245, 158, 11)', bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.3)' };
    return { primary: 'rgb(34, 197, 94)', bg: 'rgba(34, 197, 94, 0.05)', border: 'rgba(63, 63, 70, 1)' };
  };

  const colors = getStatusColor();
  const segments = 20;
  const filledSegments = Math.round((usagePercent / 100) * segments);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-xl border bg-zinc-900/80"
      style={{ borderColor: colors.border }}
    >
      {/* Subtle gradient overlay */}
      <div
        className="absolute inset-0 opacity-30"
        style={{
          background: `radial-gradient(ellipse at top left, ${colors.bg}, transparent 50%)`
        }}
      />

      <div className="relative p-5">
        {/* Header row */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: colors.primary }}
              />
              <span className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
                Лимит анализов
              </span>
            </div>
            <div className="flex items-baseline gap-3">
              <span
                className="text-4xl font-bold tabular-nums tracking-tight"
                style={{ color: isCritical ? colors.primary : isLow ? colors.primary : '#fafafa' }}
              >
                {limits.analyses_remaining}
              </span>
              <span className="text-sm text-zinc-500">
                из {limits.analyses_limit} осталось
              </span>
            </div>
          </div>

          {/* Circular indicator */}
          <div className="relative w-16 h-16">
            <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
              {/* Background circle */}
              <circle
                cx="32"
                cy="32"
                r="28"
                fill="none"
                stroke="rgb(39, 39, 42)"
                strokeWidth="4"
              />
              {/* Progress circle */}
              <circle
                cx="32"
                cy="32"
                r="28"
                fill="none"
                stroke={colors.primary}
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray={`${remainingPercent * 1.76} 176`}
                className="transition-all duration-500"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span
                className="text-sm font-bold tabular-nums"
                style={{ color: colors.primary }}
              >
                {remainingPercent}%
              </span>
            </div>
          </div>
        </div>

        {/* Segmented progress bar */}
        <div className="flex gap-0.5 mb-3">
          {Array.from({ length: segments }).map((_, i) => {
            const isUsed = i < filledSegments;
            return (
              <motion.div
                key={i}
                initial={{ scaleY: 0 }}
                animate={{ scaleY: 1 }}
                transition={{ delay: i * 0.02, duration: 0.2 }}
                className="flex-1 h-2 rounded-sm origin-bottom"
                style={{
                  backgroundColor: isUsed
                    ? (isCritical ? 'rgb(239, 68, 68)' : isLow ? 'rgb(245, 158, 11)' : 'rgb(63, 63, 70)')
                    : 'rgb(39, 39, 42)'
                }}
              />
            );
          })}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-[11px] text-zinc-500">
          <span>
            Использовано: <span className="text-zinc-300 tabular-nums">{limits.analyses_used}</span>
          </span>
          {limits.reset_date && (
            <span>
              Обновление: {new Date(limits.reset_date).toLocaleDateString('ru-RU')}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
};
