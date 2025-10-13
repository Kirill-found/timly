/**
 * Страница настроек (токен HH.ru)
 */
import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Box,
  Alert,
  CircularProgress,
  Link,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { settingsAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';

const SettingsPage = () => {
  const [token, setToken] = useState('');
  const [hasToken, setHasToken] = useState(false);
  const [tokenVerified, setTokenVerified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const { updateUser } = useAuth();

  // Проверка текущего статуса токена
  const checkTokenStatus = async () => {
    setChecking(true);
    try {
      const response = await settingsAPI.verifyHHToken();
      setHasToken(response.data.has_token);
      setTokenVerified(response.data.token_verified);
      if (!response.data.token_verified && response.data.has_token) {
        setError('Токен недействителен. Обновите токен.');
      }
    } catch (err) {
      setError('Ошибка проверки токена');
    } finally {
      setChecking(false);
    }
  };

  // Сохранение токена
  const saveToken = async () => {
    setLoading(true);
    setError('');
    setMessage('');
    
    try {
      await settingsAPI.updateHHToken(token);
      setMessage('Токен успешно сохранён и проверен');
      setToken('');
      await checkTokenStatus();
      await updateUser();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка сохранения токена');
    } finally {
      setLoading(false);
    }
  };

  // Удаление токена
  const deleteToken = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить токен?')) {
      return;
    }
    
    setLoading(true);
    setError('');
    setMessage('');
    
    try {
      await settingsAPI.deleteHHToken();
      setMessage('Токен успешно удалён');
      setHasToken(false);
      setTokenVerified(false);
      await updateUser();
    } catch (err) {
      setError('Ошибка удаления токена');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkTokenStatus();
  }, []);

  if (checking) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="md">
      <Typography variant="h4" component="h1" gutterBottom>
        Настройки
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Интеграция с HH.ru
        </Typography>
        
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          {hasToken && tokenVerified ? (
            <>
              <CheckCircleIcon color="success" />
              <Typography color="success.main">
                Токен настроен и активен
              </Typography>
            </>
          ) : hasToken ? (
            <>
              <ErrorIcon color="error" />
              <Typography color="error.main">
                Токен настроен, но недействителен
              </Typography>
            </>
          ) : (
            <>
              <ErrorIcon color="warning" />
              <Typography color="warning.main">
                Токен не настроен
              </Typography>
            </>
          )}
        </Box>

        {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Typography variant="body2" color="text.secondary" paragraph>
          Для работы с HH.ru необходим токен доступа к API. 
          Получить токен можно в личном кабинете работодателя на HH.ru в разделе 
          {' '}
          <Link href="https://hh.ru/employer/api" target="_blank" rel="noopener">
            "Интеграция и API"
          </Link>
        </Typography>

        <TextField
          fullWidth
          label="Токен HH.ru"
          type="password"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Введите токен доступа"
          margin="normal"
          helperText="Токен будет зашифрован и безопасно сохранён"
        />

        <Box display="flex" gap={2} mt={2}>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={saveToken}
            disabled={!token || loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Сохранить токен'}
          </Button>
          
          {hasToken && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={deleteToken}
              disabled={loading}
            >
              Удалить токен
            </Button>
          )}
        </Box>
      </Paper>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Инструкция по получению токена
        </Typography>
        <ol>
          <li>Войдите в личный кабинет работодателя на HH.ru</li>
          <li>Перейдите в раздел "Настройки" → "Интеграция и API"</li>
          <li>Создайте новое приложение или используйте существующее</li>
          <li>Скопируйте токен доступа (Access Token)</li>
          <li>Вставьте токен в поле выше и нажмите "Сохранить"</li>
        </ol>
        
        <Alert severity="info" sx={{ mt: 2 }}>
          Важно: токен даёт доступ к вашим вакансиям и откликам на HH.ru. 
          Никому не передавайте ваш токен!
        </Alert>
      </Paper>
    </Container>
  );
};

export default SettingsPage;