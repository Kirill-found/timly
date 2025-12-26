/**
 * AnalysisProgress - Прогресс AI анализа
 * Design: Dark Industrial - минималистичный, информативный
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Square, Clock, Zap } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface AnalysisProgressProps {
  analyzed: number;
  total: number;
  startTime: number;
  onStop?: () => void;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  analyzed,
  total,
  startTime,
  onStop
}) => {
  const progress = total > 0 ? (analyzed / total) * 100 : 0;
  const elapsed = Date.now() - startTime;
  const avgTimePerResume = analyzed > 0 ? elapsed / analyzed : 0;
  const remainingCount = total - analyzed;
  const remainingMs = remainingCount * avgTimePerResume;
  const minutes = Math.floor(remainingMs / 60000);
  const seconds = Math.floor((remainingMs % 60000) / 1000);
  const speed = analyzed > 0 ? ((analyzed / (elapsed / 1000)) * 60).toFixed(1) : '0';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border-zinc-800">
        <CardContent className="p-0">
          {/* Header */}
          <div className="p-5 border-b border-zinc-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center">
                  <Brain className="h-5 w-5 text-zinc-400" />
                </div>
                <div>
                  <div className="text-sm font-medium text-zinc-200">
                    Анализ выполняется
                  </div>
                  <div className="text-xs text-zinc-500 mt-0.5">
                    {analyzed} из {total} резюме
                  </div>
                </div>
              </div>
              <div className="text-2xl font-semibold tabular-nums text-zinc-100">
                {progress.toFixed(0)}%
              </div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="px-5 py-4">
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="h-full bg-zinc-400 rounded-full relative"
              >
                {/* Subtle shine animation */}
                <motion.div
                  animate={{ x: ['-100%', '200%'] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 w-1/2 bg-gradient-to-r from-transparent via-zinc-300/20 to-transparent"
                />
              </motion.div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 divide-x divide-zinc-800 border-t border-zinc-800">
            <div className="p-4 text-center">
              <div className="text-xl font-semibold tabular-nums text-zinc-200">
                {analyzed}
              </div>
              <div className="text-[11px] text-zinc-500 mt-1">готово</div>
            </div>
            <div className="p-4 text-center">
              <div className="text-xl font-semibold tabular-nums text-zinc-200">
                {remainingCount}
              </div>
              <div className="text-[11px] text-zinc-500 mt-1">осталось</div>
            </div>
            <div className="p-4 text-center">
              <div className="text-xl font-semibold tabular-nums text-zinc-200">
                {speed}
              </div>
              <div className="text-[11px] text-zinc-500 mt-1">в минуту</div>
            </div>
          </div>

          {/* Time estimate & Stop button */}
          <div className="p-4 border-t border-zinc-800 flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs text-zinc-500">
              <div className="flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5" />
                <span>
                  {analyzed === 0 ? 'Расчёт...' :
                    minutes > 0 ? `≈ ${minutes} мин ${seconds} сек` : `≈ ${seconds} сек`}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5" />
                <span>{speed} рез/мин</span>
              </div>
            </div>

            {onStop && (
              <Button
                onClick={onStop}
                variant="ghost"
                size="sm"
                className="h-8 px-3 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 border border-zinc-700"
              >
                <Square className="h-3 w-3 mr-1.5 fill-current" />
                Остановить
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};
