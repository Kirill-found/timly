/**
 * DataLoader - компонент для автоматической загрузки данных при старте
 * Загружает вакансии и отклики из API в глобальное состояние
 */
import { useEffect } from 'react';
import { useAuth } from '@/store/AuthContext';
import { useApp } from '@/store/AppContext';
import { apiClient } from '@/services/api';

export const DataLoader: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const { setVacancies, setApplications, setLoading } = useApp();

  useEffect(() => {
    const loadData = async () => {
      if (!isAuthenticated || !user) {
        return;
      }

      try {
        // Загружаем вакансии
        setLoading('vacanciesLoading', true);
        const vacancies = await apiClient.getVacancies();

        console.log('[DataLoader] API response:', vacancies);
        console.log('[DataLoader] Is array?', Array.isArray(vacancies));

        if (Array.isArray(vacancies)) {
          setVacancies(vacancies);
          console.log(`[DataLoader] Loaded ${vacancies.length} vacancies`);
        } else {
          console.error('[DataLoader] API returned non-array:', typeof vacancies, vacancies);
          setVacancies([]);
        }
      } catch (err) {
        console.error('[DataLoader] Error loading vacancies:', err);
        setVacancies([]);
      } finally {
        setLoading('vacanciesLoading', false);
      }
    };

    loadData();
  }, [isAuthenticated, user]); // Загружаем при изменении статуса авторизации

  return null; // Этот компонент не рендерит ничего
};
