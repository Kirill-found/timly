/**
 * Главный контекст приложения Timly
 * Управление глобальным состоянием вакансий и анализов
 */
import React, { createContext, useContext, useReducer } from 'react';
import type { Vacancy, Application, AnalysisResult, SyncJob } from '@/types';

// Типы состояния
interface AppState {
  // Вакансии
  vacancies: Vacancy[];
  currentVacancy: Vacancy | null;
  vacanciesLoading: boolean;

  // Отклики
  applications: Application[];
  applicationsLoading: boolean;

  // Анализы
  analysisResults: AnalysisResult[];
  analysisLoading: boolean;

  // Синхронизация
  activeSyncJobs: SyncJob[];
  syncHistory: SyncJob[];

  // Общие состояния
  globalLoading: boolean;
  error: string | null;
}

// Типы действий
type AppAction =
  | { type: 'SET_LOADING'; payload: { key: keyof AppState; loading: boolean } }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_VACANCIES'; payload: Vacancy[] }
  | { type: 'SET_CURRENT_VACANCY'; payload: Vacancy | null }
  | { type: 'UPDATE_VACANCY'; payload: Vacancy }
  | { type: 'SET_APPLICATIONS'; payload: Application[] }
  | { type: 'ADD_APPLICATION'; payload: Application }
  | { type: 'UPDATE_APPLICATION'; payload: Application }
  | { type: 'SET_ANALYSIS_RESULTS'; payload: AnalysisResult[] }
  | { type: 'ADD_ANALYSIS_RESULT'; payload: AnalysisResult }
  | { type: 'UPDATE_ANALYSIS_RESULT'; payload: AnalysisResult }
  | { type: 'SET_SYNC_JOBS'; payload: SyncJob[] }
  | { type: 'ADD_SYNC_JOB'; payload: SyncJob }
  | { type: 'UPDATE_SYNC_JOB'; payload: SyncJob }
  | { type: 'CLEAR_DATA' };

// Начальное состояние
const initialState: AppState = {
  vacancies: [],
  currentVacancy: null,
  vacanciesLoading: false,
  applications: [],
  applicationsLoading: false,
  analysisResults: [],
  analysisLoading: false,
  activeSyncJobs: [],
  syncHistory: [],
  globalLoading: false,
  error: null,
};

// Reducer
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        [action.payload.key]: action.payload.loading,
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };

    case 'SET_VACANCIES':
      return {
        ...state,
        vacancies: action.payload,
      };

    case 'SET_CURRENT_VACANCY':
      return {
        ...state,
        currentVacancy: action.payload,
      };

    case 'UPDATE_VACANCY':
      return {
        ...state,
        vacancies: state.vacancies.map((v) =>
          v.id === action.payload.id ? action.payload : v
        ),
        currentVacancy:
          state.currentVacancy?.id === action.payload.id
            ? action.payload
            : state.currentVacancy,
      };

    case 'SET_APPLICATIONS':
      return {
        ...state,
        applications: action.payload,
      };

    case 'ADD_APPLICATION':
      return {
        ...state,
        applications: [...state.applications, action.payload],
      };

    case 'UPDATE_APPLICATION':
      return {
        ...state,
        applications: state.applications.map((app) =>
          app.id === action.payload.id ? action.payload : app
        ),
      };

    case 'SET_ANALYSIS_RESULTS':
      return {
        ...state,
        analysisResults: action.payload,
      };

    case 'ADD_ANALYSIS_RESULT':
      return {
        ...state,
        analysisResults: [...state.analysisResults, action.payload],
      };

    case 'UPDATE_ANALYSIS_RESULT':
      return {
        ...state,
        analysisResults: state.analysisResults.map((result) =>
          result.id === action.payload.id ? action.payload : result
        ),
      };

    case 'SET_SYNC_JOBS':
      return {
        ...state,
        syncHistory: action.payload,
        activeSyncJobs: action.payload.filter(
          (job) => job.status === 'pending' || job.status === 'processing'
        ),
      };

    case 'ADD_SYNC_JOB':
      return {
        ...state,
        syncHistory: [action.payload, ...state.syncHistory],
        activeSyncJobs: [...state.activeSyncJobs, action.payload],
      };

    case 'UPDATE_SYNC_JOB':
      return {
        ...state,
        syncHistory: state.syncHistory.map((job) =>
          job.id === action.payload.id ? action.payload : job
        ),
        activeSyncJobs: state.activeSyncJobs
          .map((job) => (job.id === action.payload.id ? action.payload : job))
          .filter((job) => job.status === 'pending' || job.status === 'processing'),
      };

    case 'CLEAR_DATA':
      return initialState;

    default:
      return state;
  }
};

// Контекст
interface AppContextType extends AppState {
  setLoading: (key: keyof AppState, loading: boolean) => void;
  setError: (error: string | null) => void;
  setVacancies: (vacancies: Vacancy[]) => void;
  setCurrentVacancy: (vacancy: Vacancy | null) => void;
  updateVacancy: (vacancy: Vacancy) => void;
  setApplications: (applications: Application[]) => void;
  addApplication: (application: Application) => void;
  updateApplication: (application: Application) => void;
  setAnalysisResults: (results: AnalysisResult[]) => void;
  addAnalysisResult: (result: AnalysisResult) => void;
  updateAnalysisResult: (result: AnalysisResult) => void;
  setSyncJobs: (jobs: SyncJob[]) => void;
  addSyncJob: (job: SyncJob) => void;
  updateSyncJob: (job: SyncJob) => void;
  clearData: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Провайдер
export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const setLoading = (key: keyof AppState, loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: { key, loading } });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const setVacancies = (vacancies: Vacancy[]) => {
    dispatch({ type: 'SET_VACANCIES', payload: vacancies });
  };

  const setCurrentVacancy = (vacancy: Vacancy | null) => {
    dispatch({ type: 'SET_CURRENT_VACANCY', payload: vacancy });
  };

  const updateVacancy = (vacancy: Vacancy) => {
    dispatch({ type: 'UPDATE_VACANCY', payload: vacancy });
  };

  const setApplications = (applications: Application[]) => {
    dispatch({ type: 'SET_APPLICATIONS', payload: applications });
  };

  const addApplication = (application: Application) => {
    dispatch({ type: 'ADD_APPLICATION', payload: application });
  };

  const updateApplication = (application: Application) => {
    dispatch({ type: 'UPDATE_APPLICATION', payload: application });
  };

  const setAnalysisResults = (results: AnalysisResult[]) => {
    dispatch({ type: 'SET_ANALYSIS_RESULTS', payload: results });
  };

  const addAnalysisResult = (result: AnalysisResult) => {
    dispatch({ type: 'ADD_ANALYSIS_RESULT', payload: result });
  };

  const updateAnalysisResult = (result: AnalysisResult) => {
    dispatch({ type: 'UPDATE_ANALYSIS_RESULT', payload: result });
  };

  const setSyncJobs = (jobs: SyncJob[]) => {
    dispatch({ type: 'SET_SYNC_JOBS', payload: jobs });
  };

  const addSyncJob = (job: SyncJob) => {
    dispatch({ type: 'ADD_SYNC_JOB', payload: job });
  };

  const updateSyncJob = (job: SyncJob) => {
    dispatch({ type: 'UPDATE_SYNC_JOB', payload: job });
  };

  const clearData = () => {
    dispatch({ type: 'CLEAR_DATA' });
  };

  const value: AppContextType = {
    ...state,
    setLoading,
    setError,
    setVacancies,
    setCurrentVacancy,
    updateVacancy,
    setApplications,
    addApplication,
    updateApplication,
    setAnalysisResults,
    addAnalysisResult,
    updateAnalysisResult,
    setSyncJobs,
    addSyncJob,
    updateSyncJob,
    clearData,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Хук для использования контекста
export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext;