import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { apiClient } from '@/services/api';

/**
 * Страница обработки OAuth callback от HH.ru
 * Принимает code, обменивает на access_token и сохраняет
 */
const HHCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState<string>('Обработка авторизации...');
  const [employerInfo, setEmployerInfo] = useState<any>(null);

  useEffect(() => {
    const handleCallback = async () => {
      // Получаем code из URL параметров
      const code = searchParams.get('code');
      const error = searchParams.get('error');

      // Проверка на ошибку от HH.ru
      if (error) {
        setStatus('error');
        setMessage(`Ошибка авторизации: ${searchParams.get('error_description') || error}`);
        setTimeout(() => navigate('/settings'), 3000);
        return;
      }

      if (!code) {
        setStatus('error');
        setMessage('Код авторизации не получен');
        setTimeout(() => navigate('/settings'), 3000);
        return;
      }

      try {
        // Обмениваем code на access_token через backend
        const response = await apiClient.exchangeHHCode(code);

        if (response.data.token_saved && response.data.token_valid) {
          setStatus('success');
          setMessage('Токен HH.ru успешно сохранён и проверен!');
          setEmployerInfo(response.data.employer_info);

          // Перенаправляем на настройки через 2 секунды
          setTimeout(() => navigate('/settings'), 2000);
        } else {
          setStatus('error');
          setMessage('Токен получен, но не прошёл валидацию');
          setTimeout(() => navigate('/settings'), 3000);
        }
      } catch (err: any) {
        console.error('OAuth callback error:', err);
        setStatus('error');
        setMessage(
          err.response?.data?.error?.message ||
          err.message ||
          'Ошибка при сохранении токена'
        );
        setTimeout(() => navigate('/settings'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {status === 'processing' && <Loader2 className="h-5 w-5 animate-spin text-primary" />}
            {status === 'success' && <CheckCircle2 className="h-5 w-5 text-green-600" />}
            {status === 'error' && <XCircle className="h-5 w-5 text-red-600" />}

            {status === 'processing' && 'Авторизация HH.ru'}
            {status === 'success' && 'Успешно!'}
            {status === 'error' && 'Ошибка'}
          </CardTitle>
          <CardDescription>
            {status === 'processing' && 'Пожалуйста, подождите...'}
            {status === 'success' && 'Подключение к HH.ru завершено'}
            {status === 'error' && 'Не удалось подключиться к HH.ru'}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <Alert variant={status === 'error' ? 'destructive' : 'default'}>
            <AlertDescription>{message}</AlertDescription>
          </Alert>

          {status === 'success' && employerInfo && (
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-medium mb-2">Информация о работодателе:</h4>
              <div className="space-y-1 text-sm">
                {employerInfo.name && (
                  <p><span className="text-muted-foreground">Компания:</span> {employerInfo.name}</p>
                )}
                {employerInfo.manager_name && (
                  <p><span className="text-muted-foreground">Менеджер:</span> {employerInfo.manager_name}</p>
                )}
              </div>
            </div>
          )}

          {status === 'processing' && (
            <div className="flex justify-center py-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}

          <p className="text-sm text-muted-foreground text-center">
            {status === 'success' && 'Перенаправление на страницу настроек...'}
            {status === 'error' && 'Перенаправление через несколько секунд...'}
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default HHCallback;
