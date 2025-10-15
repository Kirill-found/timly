/**
 * Публичная страница для OAuth callback от HH.ru
 * Автоматически перенаправляет в Settings с кодом
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '@/store/AuthContext';

const HHCallbackPublic: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [code, setCode] = useState<string>('');

  useEffect(() => {
    // Извлекаем code из URL
    const urlParams = new URLSearchParams(window.location.search);
    const oauthCode = urlParams.get('code');

    if (oauthCode) {
      setCode(oauthCode);
      // Сохраняем код для использования после входа
      sessionStorage.setItem('hh_oauth_code', oauthCode);

      // Если пользователь уже авторизован - сразу перенаправляем в Settings
      if (isAuthenticated) {
        navigate('/settings');
      }
    }
  }, [isAuthenticated, navigate]);

  if (!code) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              Ошибка OAuth
            </CardTitle>
            <CardDescription>
              Код авторизации не найден в URL
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert variant="destructive">
              <AlertDescription>
                Пожалуйста, повторите процесс авторизации через HH.ru
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Если уже авторизован - показываем загрузку пока редиректим
  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-muted-foreground">Перенаправление в настройки...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Если не авторизован - показываем что нужно войти
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            Авторизация HH.ru успешна!
          </CardTitle>
          <CardDescription>
            Войдите в систему для завершения подключения
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert className="border-green-200 bg-green-50">
            <AlertDescription className="text-green-700">
              <div className="space-y-2">
                <p className="font-semibold">Код авторизации получен!</p>
                <p className="text-sm">Войдите в свой аккаунт Timly - токен HH.ru будет подключен автоматически</p>
              </div>
            </AlertDescription>
          </Alert>

          <button
            onClick={() => navigate('/login')}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 rounded-md font-medium"
          >
            Войти в систему
          </button>

          <p className="text-xs text-muted-foreground text-center">
            Код действителен в течение 10 минут
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default HHCallbackPublic;
