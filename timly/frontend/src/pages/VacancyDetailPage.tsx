/**
 * Страница детального просмотра вакансии и откликов
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
} from '@mui/icons-material';
import { vacanciesAPI, Application } from '../services/api';

const VacancyDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  // Загрузка откликов
  const loadApplications = async () => {
    if (!id) return;
    
    setLoading(true);
    try {
      const response = await vacanciesAPI.getApplications(id);
      setApplications(response.data);
    } catch (err) {
      setError('Ошибка загрузки откликов');
    } finally {
      setLoading(false);
    }
  };

  // Запуск анализа
  const startAnalysis = async (analyzeAll = false) => {
    if (!id) return;
    
    setAnalyzing(true);
    setError('');
    try {
      await vacanciesAPI.analyze(id, analyzeAll);
      // Начинаем периодически обновлять список для отслеживания прогресса
      const interval = setInterval(async () => {
        const response = await vacanciesAPI.getApplications(id);
        setApplications(response.data);
        
        // Проверяем, все ли отклики обработаны
        const allProcessed = response.data.every(
          (app: Application) => app.status === 'completed' || app.status === 'error'
        );
        
        if (allProcessed) {
          clearInterval(interval);
          setAnalyzing(false);
        }
      }, 3000); // Обновляем каждые 3 секунды
      
      // Останавливаем через 5 минут в любом случае
      setTimeout(() => {
        clearInterval(interval);
        setAnalyzing(false);
      }, 300000);
    } catch (err) {
      setError('Ошибка запуска анализа');
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    loadApplications();
  }, [id]);

  // Функция для отображения статуса
  const getStatusChip = (status: string) => {
    switch (status) {
      case 'completed':
        return <Chip label="Обработан" color="success" size="small" />;
      case 'analyzing':
        return <Chip label="Анализируется" color="info" size="small" />;
      case 'error':
        return <Chip label="Ошибка" color="error" size="small" />;
      default:
        return <Chip label="Ожидает" color="default" size="small" />;
    }
  };

  // Функция для отображения оценки
  const getScoreChip = (score?: number) => {
    if (score === undefined || score === null) return null;
    
    let color: 'success' | 'warning' | 'error' = 'error';
    if (score >= 70) color = 'success';
    else if (score >= 40) color = 'warning';
    
    return <Chip label={`${score}%`} color={color} size="small" />;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <IconButton onClick={() => navigate('/dashboard')}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1" sx={{ flexGrow: 1 }}>
          Отклики на вакансию
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadApplications}
        >
          Обновить
        </Button>
        <Button
          variant="contained"
          startIcon={analyzing ? <CircularProgress size={20} color="inherit" /> : <AnalyticsIcon />}
          onClick={() => startAnalysis(false)}
          disabled={analyzing}
        >
          {analyzing ? 'Анализ...' : 'Анализировать новые'}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      {analyzing && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Идёт анализ откликов с помощью AI. Это может занять несколько минут...
          <LinearProgress sx={{ mt: 1 }} />
        </Alert>
      )}

      {applications.length === 0 ? (
        <Alert severity="info">
          По этой вакансии пока нет откликов
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Кандидат</TableCell>
                <TableCell>Контакты</TableCell>
                <TableCell align="center">Оценка</TableCell>
                <TableCell>Резюме AI</TableCell>
                <TableCell align="center">Статус</TableCell>
                <TableCell>Дата</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {applications.map((application) => (
                <TableRow key={application.id}>
                  <TableCell>
                    <Typography variant="body2">
                      {application.candidate_name || 'Имя не указано'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" flexDirection="column" gap={0.5}>
                      {application.candidate_email && (
                        <Box display="flex" alignItems="center" gap={0.5}>
                          <EmailIcon fontSize="small" color="action" />
                          <Typography variant="caption">
                            {application.candidate_email}
                          </Typography>
                        </Box>
                      )}
                      {application.candidate_phone && (
                        <Box display="flex" alignItems="center" gap={0.5}>
                          <PhoneIcon fontSize="small" color="action" />
                          <Typography variant="caption">
                            {application.candidate_phone}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    {getScoreChip(application.score)}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ maxWidth: 400 }}>
                      {application.ai_summary || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    {getStatusChip(application.status)}
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {new Date(application.created_at).toLocaleDateString('ru-RU')}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
};

export default VacancyDetailPage;