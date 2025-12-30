/**
 * Страница загрузки и анализа резюме
 * Загрузка PDF/Excel файлов с AI анализом
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Upload, FileText, FileSpreadsheet, Trash2, Star, StarOff,
  Loader2, AlertCircle, CheckCircle, Brain, Filter,
  Users, TrendingUp, Phone, Mail, MapPin, Briefcase
} from 'lucide-react';

import { apiClient } from '@/services/api';

interface UploadedCandidate {
  id: string;
  source: 'pdf' | 'excel';
  original_filename: string;
  full_name: string;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  phone: string | null;
  title: string | null;
  city: string | null;
  salary_expectation: number | null;
  experience_years: number | null;
  skills: string[];
  is_analyzed: boolean;
  ai_score: number | null;
  ai_recommendation: string | null;
  ai_summary: string | null;
  ai_strengths: string[];
  ai_weaknesses: string[];
  ai_red_flags: string[];
  is_favorite: boolean;
  is_contacted: boolean;
  notes: string | null;
  created_at: string;
}

interface Vacancy {
  id: string;
  title: string;
}

