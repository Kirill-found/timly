/**
 * Страница настроек
 * Настройка HH.ru токена и параметров анализа
 */
import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Key, CheckCircle, XCircle, Info, Save, ExternalLink } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { apiClient } from '@/services/api';
import { useAuth } from '@/store/AuthContext';

const Settings: React.FC = () => {
  const { user, refreshProfile } = useAuth();
  const [hhToken, setHhToken] = useState('');
  const [isTestingToken, setIsTestingToken] = useState(false);
  const [isSavingToken, setIsSavingToken] = useState(false);
  const [tokenStatus, setTokenStatus] = useState<{
    valid: boolean;
    message: string;
    employer?: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showOAuthModal, setShowOAuthModal] = useState(false);
  const [oauthCode, setOauthCode] = useState('');
  const [isExchangingCode, setIsExchangingCode] = useState(false);

  const handleOAuthConnect = () => {
    // HH.ru OAuth параметры
    const clientId = 'H1F4CKSVJ1360RB6KTOAG6NRQD8AQVLFDRLIPSLJ4N3I5164VRLC9JJU45AUVLTH';
    const redirectUri = 'https://timly-hr.ru/auth/hh-callback';
    const authUrl = `https://hh.ru/oauth/authorize?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}`;

    // Открываем модальное окно для ввода кода
    setShowOAuthModal(true);

    // Перенаправляем в текущем окне
    window.location.href = authUrl;
  };

  const handleCodeExchange = async () => {
    if (!oauthCode.trim()) {
      setError('Введите код авторизации');
      return;
    }

    setIsExchangingCode(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await apiClient.exchangeHHCode(oauthCode);

      if (response.data?.token_saved && response.data?.token_valid) {
        setSuccessMessage('Токен HH.ru успешно сохранён и проверен!');
        setShowOAuthModal(false);
        setOauthCode('');

        // Обновляем профиль пользователя
        await refreshProfile();
      } else {
        setError('Токен получен, но не прошёл валидацию');
      }
    } catch (err: any) {
      console.error('OAuth exchange error:', err);

      // Обработка ошибки 401 - истёкший токен
      if (err.response?.status === 401) {
        setError('Ваша сессия истекла. Пожалуйста, перезагрузите страницу и войдите заново.');
      } else {
        setError(
          err.response?.data?.error?.message ||
          err.response?.data?.detail?.message ||
          err.message ||
          'Ошибка при обмене кода на токен'
        );
      }
    } finally {
      setIsExchangingCode(false);
    }
  };

  // Автоматическая обработка OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      // Автоматически обмениваем код на токен
      setOauthCode(code);
      setIsExchangingCode(true);
      setError(null);
      setSuccessMessage(null);

      apiClient.exchangeHHCode(code)
        .then(async (response) => {
          if (response.data?.token_saved && response.data?.token_valid) {
            setSuccessMessage('Токен HH.ru успешно сохранён и проверен!');
            // Обновляем профиль пользователя
            await refreshProfile();
            // Убираем code из URL
            window.history.replaceState({}, document.title, '/settings');
          } else {
            setError('Токен получен, но не прошёл валидацию');
          }
        })
        .catch((err: any) => {
          console.error('OAuth exchange error:', err);
          if (err.response?.status === 401) {
            setError('Ваша сессия истекла. Пожалуйста, перезагрузите страницу и войдите заново.');
          } else {
            setError(
              err.response?.data?.error?.message ||
              err.response?.data?.detail?.message ||
              err.message ||
              'Ошибка при обмене кода на токен'
            );
          }
        })
        .finally(() => {
          setIsExchangingCode(false);
          setOauthCode('');
        });
    }
  }, [refreshProfile]);

  useEffect(() => {
    // Очистка сообщений через 5 секунд
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const testToken = async () => {
    if (!hhToken.trim()) {
      setError('Введите токен HH.ru');
      return;
    }

    setIsTestingToken(true);
    setError(null);
    setTokenStatus(null);

    try {
      // Временно устанавливаем токен для проверки
      const tempClient = apiClient;
      const response = await fetch('https://api.hh.ru/me', {
        headers: {
          'Authorization': `Bearer ${hhToken}`,
          'User-Agent': 'Timly/1.0 (timly.ru)'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTokenStatus({
          valid: true,
          message: 'Токен действителен',
          employer: data.employer?.name || data.email
        });
      } else {
        setTokenStatus({
          valid: false,
          message: 'Токен недействителен или истек'
        });
      }
    } catch (err: any) {
      console.error('Error testing token:', err);
      setError('Ошибка при проверке токена');
    } finally {
      setIsTestingToken(false);
    }
  };

  const saveToken = async () => {
    if (!hhToken.trim()) {
      setError('Введите токен HH.ru');
      return;
    }

    if (tokenStatus && !tokenStatus.valid) {
      setError('Невозможно сохранить недействительный токен');
      return;
    }

    setIsSavingToken(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await apiClient.updateHHToken(hhToken);

      if (response.success) {
        setSuccessMessage('HH.ru токен успешно сохранен');
        setHhToken(''); // Очищаем поле после сохранения
        setTokenStatus(null);

        // Обновляем профиль пользователя
        await refreshProfile();
      }
    } catch (err: any) {
      console.error('Error saving token:', err);
      setError(err.response?.data?.error?.message || 'Ошибка при сохранении токена');
    } finally {
      setIsSavingToken(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Настройки</h1>
        <p className="text-muted-foreground">
          Настройка интеграции с HH.ru и параметров анализа
        </p>
      </div>

      {/* Ошибки */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Успех */}
      {successMessage && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">{successMessage}</AlertDescription>
        </Alert>
      )}

      {/* Статус токена */}
      {user?.has_hh_token && user?.token_verified && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">
            HH.ru токен настроен и проверен
          </AlertDescription>
        </Alert>
      )}

      {/* HH.ru токен */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            HH.ru API Токен
          </CardTitle>
          <CardDescription>
            Токен работодателя для доступа к вакансиям и откликам
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Простой способ - OAuth */}
          <div className="p-4 border-2 border-primary/20 rounded-lg bg-primary/5">
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <ExternalLink className="h-4 w-4" />
              Рекомендуемый способ
            </h3>
            <p className="text-sm text-muted-foreground mb-3">
              Автоматическое подключение через HH.ru OAuth (занимает 30 секунд)
            </p>
            <Button
              onClick={handleOAuthConnect}
              className="w-full bg-red-500 hover:bg-red-600 text-white"
              size="lg"
            >
              <ExternalLink className="mr-2 h-4 w-4" />
              Подключить через HH.ru
            </Button>
          </div>

          {/* Разделитель */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                или ручная настройка
              </span>
            </div>
          </div>

          {/* Ручной способ - копирование токена */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-semibold">Ручной способ (если OAuth не работает):</p>
                <ol className="list-decimal list-inside space-y-1 text-sm">
                  <li>Перейдите на <a href="https://hh.ru/oauth/authorize?response_type=code&client_id=H1F4CKSVJ1360RB6KTOAG6NRQD8AQVLFDRLIPSLJ4N3I5164VRLC9JJU45AUVLTH&redirect_uri=https://timly-hr.ru/auth/hh-callback" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">страницу авторизации</a></li>
                  <li>Войдите как работодатель</li>
                  <li>Скопируйте код из URL (параметр code=...)</li>
                  <li>Обменяйте код на токен через <a href="https://httpie.io/app" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">httpie.io</a></li>
                  <li>Вставьте полученный access_token ниже</li>
                </ol>
              </div>
            </AlertDescription>
          </Alert>

          {/* Поле токена */}
          <div className="space-y-2">
            <Label htmlFor="hh-token">Access Token</Label>
            <Input
              id="hh-token"
              type="password"
              placeholder="Введите ваш HH.ru access token..."
              value={hhToken}
              onChange={(e) => {
                setHhToken(e.target.value);
                setTokenStatus(null); // Сбрасываем статус при изменении
              }}
            />
          </div>

          {/* Статус проверки */}
          {tokenStatus && (
            <Alert variant={tokenStatus.valid ? "default" : "destructive"}>
              {tokenStatus.valid ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <XCircle className="h-4 w-4" />
              )}
              <AlertDescription>
                <div className="font-semibold">{tokenStatus.message}</div>
                {tokenStatus.employer && (
                  <div className="text-sm mt-1">Работодатель: {tokenStatus.employer}</div>
                )}
              </AlertDescription>
            </Alert>
          )}

          {/* Кнопки */}
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={testToken}
              disabled={!hhToken.trim() || isTestingToken}
              className="hover:bg-gray-100 hover:border-gray-400 transition-all"
            >
              {isTestingToken ? (
                <>Проверка...</>
              ) : (
                <>
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Проверить токен
                </>
              )}
            </Button>

            <Button
              onClick={saveToken}
              disabled={!hhToken.trim() || isSavingToken}
              className="bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSavingToken ? (
                <>Сохранение...</>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Сохранить токен
                </>
              )}
            </Button>
          </div>

          {/* Подсказка */}
          <p className="text-sm text-muted-foreground">
            💡 Вы можете сохранить токен сразу, или проверить его валидность перед сохранением
          </p>
        </CardContent>
      </Card>

      {/* Параметры анализа */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5" />
            Параметры AI анализа
          </CardTitle>
          <CardDescription>
            Настройка параметров автоматического анализа резюме
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              Настройки AI анализа будут доступны в следующей версии
            </AlertDescription>
          </Alert>

          <div className="space-y-3 opacity-50 pointer-events-none">
            <div className="flex items-center justify-between">
              <div>
                <Label>Автоматический анализ</Label>
                <p className="text-sm text-muted-foreground">
                  Запускать анализ автоматически после синхронизации
                </p>
              </div>
              <input type="checkbox" className="h-5 w-5" disabled />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Минимальный балл</Label>
                <p className="text-sm text-muted-foreground">
                  Порог для автоматического отклонения (0-100)
                </p>
              </div>
              <Input type="number" className="w-20" placeholder="40" disabled />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Пакетный анализ</Label>
                <p className="text-sm text-muted-foreground">
                  Количество резюме для одновременной обработки
                </p>
              </div>
              <Input type="number" className="w-20" placeholder="5" disabled />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Информация об аккаунте */}
      <Card>
        <CardHeader>
          <CardTitle>Информация об аккаунте</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-muted-foreground">Email</div>
              <div className="font-medium">{user?.email}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Компания</div>
              <div className="font-medium">{user?.company_name || '—'}</div>
            </div>
            <div>
              <div className="text-muted-foreground">Роль</div>
              <div className="font-medium">
                {user?.role === 'admin' ? 'Администратор' : 'Пользователь'}
              </div>
            </div>
            <div>
              <div className="text-muted-foreground">HH.ru интеграция</div>
              <div className="font-medium">
                {user?.has_hh_token ? (
                  <span className="text-green-600">Настроена</span>
                ) : (
                  <span className="text-yellow-600">Не настроена</span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Модальное окно для ввода OAuth кода */}
      <Dialog open={showOAuthModal} onOpenChange={setShowOAuthModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Подключение HH.ru</DialogTitle>
            <DialogDescription>
              Скопируйте код авторизации из адресной строки открывшегося окна
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <ol className="list-decimal list-inside space-y-1 text-sm">
                  <li>В открывшемся окне авторизуйтесь на HH.ru</li>
                  <li>После авторизации вас перенаправит на другую страницу</li>
                  <li>Скопируйте значение параметра <code className="bg-muted px-1 rounded">code=</code> из URL</li>
                  <li>Вставьте код в поле ниже</li>
                </ol>
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label htmlFor="oauth-code">Код авторизации</Label>
              <Input
                id="oauth-code"
                placeholder="Вставьте код из URL (после code=...)"
                value={oauthCode}
                onChange={(e) => setOauthCode(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && oauthCode.trim()) {
                    handleCodeExchange();
                  }
                }}
              />
              <p className="text-xs text-muted-foreground">
                Пример: https://timly-hr.ru/settings?<span className="font-semibold">code=ABC123XYZ</span>
              </p>
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => {
                setShowOAuthModal(false);
                setOauthCode('');
                setError(null);
              }}
              disabled={isExchangingCode}
            >
              Отмена
            </Button>
            <Button
              onClick={handleCodeExchange}
              disabled={!oauthCode.trim() || isExchangingCode}
              className="bg-green-600 hover:bg-green-700"
            >
              {isExchangingCode ? 'Обработка...' : 'Подключить'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Settings;
