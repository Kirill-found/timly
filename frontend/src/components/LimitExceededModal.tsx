/**
 * Модальное окно при достижении лимита анализов
 * Показывается когда пользователь исчерпал свой лимит по тарифу
 */
import React from 'react';
import { AlertTriangle, Sparkles, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface LimitExceededModalProps {
  isOpen: boolean;
  onClose: () => void;
  subscriptionInfo?: {
    plan_type: string;
    analyses_used: number;
    analyses_limit: number;
  };
}

export const LimitExceededModal: React.FC<LimitExceededModalProps> = ({
  isOpen,
  onClose,
  subscriptionInfo
}) => {
  const handleUpgrade = () => {
    window.location.href = '/subscription';
  };

  const getPlanName = (planType?: string) => {
    switch (planType) {
      case 'trial':
        return 'Trial (Пробный)';
      case 'free':
        return 'Free (Бесплатный)';
      case 'starter':
        return 'Starter';
      case 'professional':
        return 'Professional';
      case 'enterprise':
        return 'Enterprise';
      default:
        return 'Текущий';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 bg-orange-100 rounded-full">
              <AlertTriangle className="h-8 w-8 text-orange-600" />
            </div>
          </div>
          <DialogTitle className="text-center text-xl">
            Достигнут лимит анализов
          </DialogTitle>
          <DialogDescription className="text-center">
            {subscriptionInfo && (
              <div className="mt-4 space-y-3">
                <p className="text-base">
                  Вы использовали <span className="font-bold text-orange-600">{subscriptionInfo.analyses_used}</span> из <span className="font-bold">{subscriptionInfo.analyses_limit}</span> доступных анализов
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-900">
                    Текущий тариф: <span className="font-semibold">{getPlanName(subscriptionInfo.plan_type)}</span>
                  </p>
                </div>
              </div>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 my-4">
          <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Sparkles className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-green-900 mb-1">
                  Обновите тариф для продолжения
                </h4>
                <p className="text-sm text-green-700">
                  Получите больше анализов и дополнительные возможности
                </p>
              </div>
            </div>
          </div>

          {subscriptionInfo?.plan_type === 'trial' && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
              <div className="flex items-center gap-2 text-purple-900">
                <TrendingUp className="h-4 w-4" />
                <p className="text-sm font-medium">
                  Специальное предложение для Trial пользователей!
                </p>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            className="w-full sm:w-auto"
          >
            Закрыть
          </Button>
          <Button
            onClick={handleUpgrade}
            className="w-full sm:w-auto bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Обновить тариф
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
