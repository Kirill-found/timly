/**
 * Компонент визуализации прогресса AI анализа
 * Показывает анимированный прогресс с particle effects
 */
import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Sparkles, Zap, TrendingUp } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
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

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="relative"
    >
      <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 shadow-2xl overflow-hidden">
        {/* Декоративные анимированные круги */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="absolute top-0 right-0 w-64 h-64 bg-purple-300/30 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1.5
            }}
            className="absolute bottom-0 left-0 w-64 h-64 bg-blue-300/30 rounded-full blur-3xl"
          />
        </div>

        <CardContent className="p-8 relative z-10">
          {/* Заголовок с иконкой AI */}
          <div className="flex items-center justify-center gap-3 mb-6">
            <motion.div
              animate={{
                rotate: [0, 360],
                scale: [1, 1.1, 1],
              }}
              transition={{
                rotate: {
                  duration: 4,
                  repeat: Infinity,
                  ease: "linear"
                },
                scale: {
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }
              }}
              className="p-3 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl shadow-lg"
            >
              <Brain className="h-8 w-8 text-white" />
            </motion.div>
            <div>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                AI анализирует резюме
              </h3>
              <p className="text-sm text-gray-600">Пожалуйста, подождите...</p>
            </div>
          </div>

          {/* Статистика в карточках */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-white/80 backdrop-blur-sm rounded-xl p-4 text-center border border-purple-100 shadow-sm"
            >
              <div className="text-3xl font-bold text-purple-600">{analyzed}</div>
              <div className="text-xs text-gray-600 mt-1">Проанализировано</div>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-white/80 backdrop-blur-sm rounded-xl p-4 text-center border border-blue-100 shadow-sm"
            >
              <div className="text-3xl font-bold text-blue-600">{total}</div>
              <div className="text-xs text-gray-600 mt-1">Всего</div>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="bg-white/80 backdrop-blur-sm rounded-xl p-4 text-center border border-pink-100 shadow-sm"
            >
              <div className="text-3xl font-bold text-pink-600">{remainingCount}</div>
              <div className="text-xs text-gray-600 mt-1">Осталось</div>
            </motion.div>
          </div>

          {/* Прогресс-бар с анимацией */}
          <div className="space-y-3 mb-6">
            <div className="flex justify-between items-center text-sm font-medium">
              <span className="text-gray-700">Прогресс</span>
              <span className="text-purple-600 font-bold">{progress.toFixed(0)}%</span>
            </div>

            {/* Кастомный градиентный прогресс-бар */}
            <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden shadow-inner">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 rounded-full relative overflow-hidden"
              >
                {/* Анимированный блик */}
                <motion.div
                  animate={{
                    x: ['-100%', '200%'],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                  className="absolute inset-0 w-1/3 bg-gradient-to-r from-transparent via-white/30 to-transparent skew-x-12"
                />
              </motion.div>
            </div>

            {/* Информация о времени */}
            <div className="flex justify-between items-center text-xs text-gray-600">
              <div className="flex items-center gap-1">
                <Zap className="h-3 w-3 text-yellow-500" />
                <span>
                  {analyzed === 0 ? 'Подсчет времени...' :
                    minutes > 0 ? `≈ ${minutes} мин ${seconds} сек` : `≈ ${seconds} сек`}
                </span>
              </div>
              <div className="flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-500" />
                <span>{((analyzed / (elapsed / 1000)) * 60).toFixed(1)} резюме/мин</span>
              </div>
            </div>
          </div>

          {/* Анимированные частицы успеха */}
          {analyzed > 0 && (
            <div className="flex justify-center gap-1 mb-4">
              {[...Array(Math.min(5, Math.floor(analyzed / (total / 10))))].map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: i * 0.1, type: "spring" }}
                >
                  <Sparkles className="h-5 w-5 text-yellow-500" />
                </motion.div>
              ))}
            </div>
          )}

          {/* Кнопка остановки */}
          {onStop && (
            <Button
              onClick={onStop}
              variant="outline"
              className="w-full border-2 border-red-200 hover:bg-red-50 hover:border-red-300 transition-all"
            >
              <motion.div
                animate={{ rotate: [0, 5, -5, 0] }}
                transition={{ duration: 0.5, repeat: Infinity }}
              >
                ⏹️
              </motion.div>
              <span className="ml-2">Остановить анализ</span>
            </Button>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};
