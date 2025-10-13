/**
 * Главная страница дашборда с вакансиями
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Alert,
  CircularProgress,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { vacanciesAPI, settingsAPI, Vacancy } from '../services/api';
import { useAuth } from '../hooks/useAuth';

const DashboardPage = () => {
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [hasToken, setHasToken] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { updateUser } = useAuth();

  // Загрузка вакансий
  const loadVacancies = async () => {
    try {
      const response = await vacanciesAPI.getList();
      setVacancies(response.data);
    } catch (err) {
      setError('Ошибка загрузки вакансий');
    } finally {
      setLoading(false);
    }
  };

  // Проверка токена HH.ru
  const checkToken = async () => {
    try {
      const response = await settingsAPI.verifyHHToken();
      setHasToken(response.data.has_token && response.data.token_verified);
    } catch (err) {
      setHasToken(false);
    }
  };

  // Синхронизация вакансий
  const syncVacancies = async () => {
    setSyncing(true);
    setError('');
    try {
      const response = await vacanciesAPI.sync();
      await loadVacancies();
      await updateUser();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка синхронизации');
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    checkToken();
    loadVacancies();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!hasToken) {
    return (
      <Container>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Для работы с вакансиями необходимо настроить токен HH.ru
        </Alert>
        <Button
          variant="contained"
          startIcon={<SettingsIcon />}
          onClick={() => navigate('/settings')}
        >
          Перейти в настройки
        </Button>
      </Container>
    );
  }

  return (
    <Container>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Мои вакансии
        </Typography>
        <Button
          variant="contained"
          startIcon={syncing ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
          onClick={syncVacancies}
          disabled={syncing}
        >
          {syncing ? 'Синхронизация...' : 'Синхронизировать'}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {vacancies.length === 0 ? (
        <Alert severity="info">
          У вас пока нет вакансий. Нажмите "Синхронизировать" для загрузки вакансий с HH.ru
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {vacancies.map((vacancy) => (
            <Grid item xs={12} md={6} lg={4} key={vacancy.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="div" gutterBottom>
                    {vacancy.title}
                  </Typography>
                  {vacancy.company_name && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {vacancy.company_name}
                    </Typography>
                  )}
                  <Box display="flex" gap={1} mt={2}>
                    <Chip
                      icon={<PeopleIcon />}
                      label={`${vacancy.applications_count || 0} откликов`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                  {vacancy.last_synced_at && (
                    <Typography variant="caption" display="block" mt={1}>
                      Обновлено: {new Date(vacancy.last_synced_at).toLocaleDateString('ru-RU')}
                    </Typography>
                  )}
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    onClick={() => navigate(`/vacancy/${vacancy.id}`)}
                  >
                    Подробнее
                  </Button>
                  <Tooltip title="Анализировать отклики">
                    <IconButton
                      size="small"
                      onClick={async () => {
                        try {
                          await vacanciesAPI.analyze(vacancy.id);
                          setError('');
                        } catch (err) {
                          setError('Ошибка запуска анализа');
                        }
                      }}
                    >
                      <AnalyticsIcon />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default DashboardPage;