/**
 * Публичная страница для OAuth callback от HH.ru
 * НЕ требует авторизации - показывает код пользователю
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { CheckCircle, Copy, AlertCircle } from 'lucide-react';

const HHCallbackPublic: React.FC = () => {
  const navigate = useNavigate();
  const [code, setCode] = useState<string>('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Извлекаем code из URL
    const urlParams = new URLSearchParams(window.location.search);
    const oauthCode = urlParams.get('code');

    if (oauthCode) {
      setCode(oauthCode);
    }
  }, []);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleContinue = () => {
    // Перенаправляем на страницу входа
    navigate('/login');
  };

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
            <Button onClick={handleContinue} className="w-full">
              Вернуться к входу
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            Авторизация HH.ru успешна!
          </CardTitle>
          <CardDescription>
            Скопируйте код ниже и войдите в систему
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert className="border-green-200 bg-green-50">
            <AlertDescription className="text-green-700">
              <div className="space-y-2">
                <p className="font-semibold">Код авторизации получен!</p>
                <p className="text-sm">Следуйте инструкциям ниже для завершения подключения HH.ru</p>
              </div>
            </AlertDescription>
          </Alert>

          {/* Код для копирования */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Ваш код авторизации:</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={code}
                readOnly
                className="flex-1 px-3 py-2 border rounded-md bg-muted font-mono text-sm"
              />
              <Button
                onClick={handleCopy}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Copy className="h-4 w-4" />
                {copied ? 'Скопировано!' : 'Копировать'}
              </Button>
            </div>
          </div>

          {/* Инструкции */}
          <Alert>
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-semibold">Что делать дальше:</p>
                <ol className="list-decimal list-inside space-y-1 text-sm">
                  <li>Скопируйте код выше (нажмите кнопку "Копировать")</li>
                  <li>Нажмите кнопку "Войти в систему" ниже</li>
                  <li>Войдите в свой аккаунт Timly</li>
                  <li>Перейдите в раздел "Настройки"</li>
                  <li>Вставьте скопированный код в модальное окно</li>
                  <li>Нажмите "Подключить"</li>
                </ol>
              </div>
            </AlertDescription>
          </Alert>

          {/* Кнопка продолжения */}
          <Button onClick={handleContinue} className="w-full" size="lg">
            Войти в систему
          </Button>

          {/* Дополнительная информация */}
          <p className="text-xs text-muted-foreground text-center">
            Код действителен в течение 10 минут. Если возникли проблемы, повторите процесс авторизации.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default HHCallbackPublic;
