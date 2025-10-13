/**
 * Хук для загрузки и управления вакансиями
 * Автоматически загружает вакансии из API и синхронизирует с AppContext
 */
import { useEffect, useState } from 'react';
import { useApp } from '@/store/AppContext';
import { apiClient } from '@/services/api';

export const useVacancies = () => {
  const { vacancies, setVacancies, vacanciesLoading, setLoading } = useApp();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadVacancies = async () => {
      // Если уже загружены, не загружаем повторно
      if (vacancies.length > 0) {
        return;
      }

      try {
        setLoading('vacanciesLoading', true);
        setError(null);

        const data = await apiClient.getVacancies();
        setVacancies(data);
      } catch (err: any) {
        console.error('Error loading vacancies:', err);
        setError(err.response?.data?.error?.message || 'Ошибка загрузки вакансий');
      } finally {
        setLoading('vacanciesLoading', false);
      }
    };

    loadVacancies();
  }, []); // Загружаем только один раз при монтировании

  const refreshVacancies = async () => {
    try {
      setLoading('vacanciesLoading', true);
      setError(null);

      const data = await apiClient.getVacancies();
      setVacancies(data);
    } catch (err: any) {
      console.error('Error refreshing vacancies:', err);
      setError(err.response?.data?.error?.message || 'Ошибка обновления вакансий');
    } finally {
      setLoading('vacanciesLoading', false);
    }
  };

  return {
    vacancies,
    loading: vacanciesLoading,
    error,
    refreshVacancies
  };
};
