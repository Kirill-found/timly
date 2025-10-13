/**
 * Лендинг страница Timly
 * Публичная главная страница с описанием продукта
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { Rocket, Trophy, Clock, Users, Brain, Target, Zap } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Hero секция */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center space-y-8">
          {/* Логотип */}
          <div className="flex justify-center mb-6">
            <img src="/logo.jpg" alt="Timly Logo" className="h-32 w-32 rounded-full object-cover shadow-2xl ring-4 ring-blue-100" />
          </div>

          <h1 className="text-6xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
            Timly
          </h1>
          <p className="text-2xl font-semibold text-gray-700">
            AI-анализ резюме для рекрутеров
          </p>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Автоматизируйте отбор кандидатов с помощью искусственного интеллекта.
            Экономьте до 80% времени на первичном скрининге резюме.
          </p>
          <div className="flex gap-4 justify-center">
            <Button asChild size="lg" className="bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white shadow-lg hover:shadow-xl transition-all">
              <Link to="/register">
                <Rocket className="mr-2 h-5 w-5" />
                Начать бесплатно
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50">
              <Link to="/login">Войти</Link>
            </Button>
          </div>
        </div>

        {/* Преимущества */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">
          <Card className="border-blue-200 hover:shadow-lg transition-shadow bg-gradient-to-br from-blue-50 to-white">
            <CardHeader>
              <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center mb-2">
                <Zap className="h-6 w-6 text-blue-600" />
              </div>
              <CardTitle>Быстрый старт</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Интеграция с HH.ru за 2 минуты. Начните анализировать резюме сразу после регистрации.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-green-200 hover:shadow-lg transition-shadow bg-gradient-to-br from-green-50 to-white">
            <CardHeader>
              <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center mb-2">
                <Brain className="h-6 w-6 text-green-600" />
              </div>
              <CardTitle>Точный анализ</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                AI оценивает резюме по 10+ критериям: навыки, опыт, зарплатные ожидания.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-purple-200 hover:shadow-lg transition-shadow bg-gradient-to-br from-purple-50 to-white">
            <CardHeader>
              <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center mb-2">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
              <CardTitle>Экономия времени</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Обработка 100 резюме за 15 минут вместо 8 часов ручной работы.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-orange-200 hover:shadow-lg transition-shadow bg-gradient-to-br from-orange-50 to-white">
            <CardHeader>
              <div className="h-12 w-12 rounded-full bg-orange-100 flex items-center justify-center mb-2">
                <Target className="h-6 w-6 text-orange-600" />
              </div>
              <CardTitle>Лучшие кандидаты</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Система выделяет топ-кандидатов и дает рекомендации по каждому.
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        {/* Как это работает */}
        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold mb-8">Как это работает</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center mx-auto text-xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold">Подключите HH.ru</h3>
              <p className="text-muted-foreground">
                Добавьте API токен HH.ru в настройках за 1 минуту
              </p>
            </div>

            <div className="space-y-4">
              <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center mx-auto text-xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold">Синхронизируйте данные</h3>
              <p className="text-muted-foreground">
                Система автоматически загрузит ваши вакансии и отклики
              </p>
            </div>

            <div className="space-y-4">
              <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center mx-auto text-xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold">Получите результаты</h3>
              <p className="text-muted-foreground">
                AI проанализирует резюме и выделит лучших кандидатов
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 text-center bg-gradient-to-r from-blue-600 to-green-600 rounded-2xl p-12 text-white shadow-2xl">
          <h2 className="text-4xl font-bold mb-4">Готовы начать?</h2>
          <p className="mb-6 text-lg text-blue-50">
            Первые 50 анализов бесплатно. Кредитная карта не требуется.
          </p>
          <Button asChild size="lg" className="bg-white text-blue-600 hover:bg-gray-100 shadow-lg">
            <Link to="/register">
              <Rocket className="mr-2 h-5 w-5" />
              Создать аккаунт
            </Link>
          </Button>
          <p className="mt-4 text-sm text-blue-100">
            Уже есть аккаунт?{' '}
            <Link to="/login" className="text-white underline hover:text-blue-100 font-semibold">
              Войти
            </Link>
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-16 bg-white">
        <div className="container mx-auto px-4 py-8 text-center text-muted-foreground">
          <div className="flex justify-center mb-4">
            <img src="/logo.jpg" alt="Timly" className="h-12 w-12 rounded-full object-cover" />
          </div>
          <p>&copy; 2024 Timly. AI-powered Resume Screening Platform.</p>
          <div className="mt-4 space-x-4">
            <Link to="/login" className="text-blue-600 hover:text-blue-800 hover:underline">Войти</Link>
            <span>•</span>
            <Link to="/register" className="text-blue-600 hover:text-blue-800 hover:underline">Регистрация</Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;