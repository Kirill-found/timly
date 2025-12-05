/**
 * Новый лендинг Timly - темный стиль
 * Оптимизированная структура блоков
 */
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Rocket,
  Clock,
  Users,
  Brain,
  Target,
  Zap,
  CheckCircle2,
  Star,
  Shield,
  BarChart3,
  FileText,
  Download,
  Eye,
  ThumbsUp,
  Sparkles,
  ArrowRight,
  ChevronDown,
  Award,
  Play,
  MapPin,
  Phone,
  Mail,
  MessageCircle,
  XCircle,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const Landing: React.FC = () => {
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  // Анимационные варианты
  const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const scaleIn = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero секция */}
      <section className="relative overflow-hidden">
        {/* Декоративные элементы */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.4, 0.6, 0.4],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-gradient-to-br from-purple-500 to-pink-500 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1,
            }}
            className="absolute -bottom-40 -left-40 w-[600px] h-[600px] bg-gradient-to-br from-blue-500 to-purple-500 rounded-full blur-3xl"
          />
        </div>

        <div className="container relative mx-auto px-4 py-20">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
            className="text-center space-y-8"
          >
            {/* Логотип */}
            <motion.div variants={scaleIn} className="flex justify-center mb-6">
              <div className="relative">
                <motion.div
                  animate={{
                    boxShadow: [
                      '0 0 20px rgba(168, 85, 247, 0.5)',
                      '0 0 60px rgba(236, 72, 153, 0.5)',
                      '0 0 20px rgba(168, 85, 247, 0.5)',
                    ],
                  }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="h-32 w-32 rounded-3xl overflow-hidden"
                >
                  <img
                    src="/logo.jpg"
                    alt="Timly Logo"
                    className="h-full w-full object-cover"
                  />
                </motion.div>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                  className="absolute -inset-2 border-4 border-dashed border-purple-400 rounded-3xl"
                />
              </div>
            </motion.div>

            <motion.div variants={fadeInUp}>
              <Badge className="mb-4 text-sm px-4 py-2 bg-purple-500/20 text-purple-200 border-purple-400/30">
                <Sparkles className="w-4 h-4 mr-2 inline" />
                AI-технологии нового поколения
              </Badge>
            </motion.div>

            <motion.h1
              variants={fadeInUp}
              className="text-6xl md:text-7xl font-bold tracking-tight"
            >
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                Timly
              </span>
            </motion.h1>

            <motion.p
              variants={fadeInUp}
              className="text-3xl md:text-4xl font-bold text-white"
            >
              Умный ИИ-помощник для рекрутеров
            </motion.p>

            <motion.p
              variants={fadeInUp}
              className="text-xl text-purple-200 max-w-3xl mx-auto leading-relaxed"
            >
              <span className="font-bold text-white">
                Устали тратить 8 часов на просмотр 200 резюме?
              </span>
              <br />
              Пропускаете хороших кандидатов из-за усталости и рутины?
              <br />
              <span className="font-semibold text-purple-300">
                Timly анализирует 100 резюме за 10 минут
              </span>{' '}
              и находит лучших кандидатов, пока вы пьёте кофе.
            </motion.p>

            <motion.div variants={fadeInUp} className="flex gap-4 justify-center flex-wrap">
              <Button
                asChild
                size="lg"
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg hover:shadow-xl transition-all text-lg px-8 py-6"
              >
                <Link to="/register">
                  <Rocket className="mr-2 h-5 w-5" />
                  Начать бесплатно
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                className="bg-white/10 backdrop-blur-sm border-2 border-white/30 text-white hover:bg-white hover:text-purple-600 hover:border-white text-lg px-8 py-6 transition-all shadow-lg hover:shadow-xl"
              >
                <Link to="/login">
                  Войти
                </Link>
              </Button>
            </motion.div>

            <motion.div
              variants={fadeInUp}
              className="flex gap-8 justify-center text-sm text-purple-200 flex-wrap"
            >
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span>50 анализов бесплатно в Trial</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span>Без кредитной карты</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                <span>Готов за 2 минуты</span>
              </div>
            </motion.div>
          </motion.div>

          {/* Статистика */}
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20"
          >
            {[
              { value: 'Beta', label: 'Ранний доступ', icon: Sparkles },
              { value: '80%', label: 'Экономия времени', icon: Clock },
              { value: '50+', label: 'Компаний тестируют', icon: Users },
              { value: '2 мин', label: 'До первого анализа', icon: Zap },
            ].map((stat, i) => (
              <motion.div
                key={i}
                variants={fadeInUp}
                className="text-center p-6 rounded-2xl bg-purple-500/10 backdrop-blur-sm border border-purple-500/20 shadow-lg"
              >
                <stat.icon className="w-8 h-8 mx-auto mb-3 text-purple-400" />
                <div className="text-3xl font-bold text-white">{stat.value}</div>
                <div className="text-sm text-purple-200 mt-1">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Преимущества перед ручным отбором - БЛОК 2 */}
      <section className="py-20 bg-slate-900 relative overflow-hidden">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            className="text-center mb-16"
          >
            <Badge className="mb-4 text-sm px-4 py-2 bg-purple-500/20 text-purple-200 border-purple-400/30">
              <Award className="w-4 h-4 mr-2 inline" />
              Почему Timly
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              Преимущества перед{' '}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                ручным отбором
              </span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
            >
              <Card className="h-full border-2 border-red-500/20 bg-red-500/5 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-2xl text-red-300 flex items-center gap-2">
                    <Eye className="w-6 h-6" />
                    Ручной отбор
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-2 text-red-300">
                    <span className="text-xl">✗</span>
                    <span>8+ часов на просмотр 100 резюме</span>
                  </div>
                  <div className="flex items-start gap-2 text-red-300">
                    <span className="text-xl">✗</span>
                    <span>Субъективная оценка кандидатов</span>
                  </div>
                  <div className="flex items-start gap-2 text-red-300">
                    <span className="text-xl">✗</span>
                    <span>Риск пропустить сильного кандидата</span>
                  </div>
                  <div className="flex items-start gap-2 text-red-300">
                    <span className="text-xl">✗</span>
                    <span>Нет структурированной аналитики</span>
                  </div>
                  <div className="flex items-start gap-2 text-red-300">
                    <span className="text-xl">✗</span>
                    <span>Высокая стоимость рабочего времени</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={fadeInUp}
              transition={{ delay: 0.2 }}
            >
              <Card className="h-full border-2 border-green-500/20 bg-green-500/5 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-2xl text-green-300 flex items-center gap-2">
                    <Brain className="w-6 h-6" />
                    Timly AI
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-2 text-green-300">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <span>10-15 минут на анализ 100 резюме</span>
                  </div>
                  <div className="flex items-start gap-2 text-green-300">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <span>Объективная оценка по 15+ критериям</span>
                  </div>
                  <div className="flex items-start gap-2 text-green-300">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <span>Точность 95% - не упустите таланты</span>
                  </div>
                  <div className="flex items-start gap-2 text-green-300">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <span>Детальная аналитика и отчеты</span>
                  </div>
                  <div className="flex items-start gap-2 text-green-300">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <span>Экономия до 80% бюджета на рекрутинг</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Начните работу за 3 простых шага - БЛОК 3 */}
      <section className="py-20 bg-gradient-to-br from-purple-900 via-slate-900 to-purple-900">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            className="text-center mb-16"
          >
            <Badge className="mb-4 text-sm px-4 py-2 bg-purple-500/20 text-purple-200 border-purple-400/30">
              <Play className="w-4 h-4 mr-2 inline" />
              Процесс
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              Начните работу за{' '}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                3 простых шага
              </span>
            </h2>
            <p className="text-xl text-purple-200 max-w-2xl mx-auto">
              От регистрации до первых результатов — всего несколько минут
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-12 max-w-5xl mx-auto">
            {[
              {
                step: '1',
                title: 'Подключите HH.ru',
                description:
                  'Зарегистрируйтесь и добавьте API токен HeadHunter в настройках. Это займет всего 1-2 минуты.',
                icon: Users,
                color: 'purple',
              },
              {
                step: '2',
                title: 'Синхронизируйте данные',
                description:
                  'Нажмите одну кнопку, и система автоматически загрузит все ваши вакансии и отклики кандидатов.',
                icon: Zap,
                color: 'pink',
              },
              {
                step: '3',
                title: 'Получите результаты',
                description:
                  'Запустите AI-анализ одним кликом. Через 10-15 минут получите полный отчет с оценками и рекомендациями.',
                icon: Award,
                color: 'blue',
              },
            ].map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.2 }}
                className="relative"
              >
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white flex items-center justify-center mx-auto text-3xl font-bold shadow-lg">
                    {step.step}
                  </div>
                  <div className="h-16 w-16 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto">
                    <step.icon className="h-8 w-8 text-purple-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-white">{step.title}</h3>
                  <p className="text-purple-200 leading-relaxed">{step.description}</p>
                </div>
                {i < 2 && (
                  <div className="hidden md:block absolute top-10 left-full w-12 h-1 bg-gradient-to-r from-purple-500/50 to-transparent -ml-6" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Посмотрите результаты - БЛОК 4 */}
      <section className="py-20 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.1, 0.2, 0.1],
              rotate: [0, 90, 0],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            className="absolute top-20 -right-40 w-96 h-96 bg-purple-500 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.1, 0.2, 0.1],
              rotate: [0, -90, 0],
            }}
            transition={{
              duration: 15,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 2,
            }}
            className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-500 rounded-full blur-3xl"
          />
        </div>

        <div className="container relative mx-auto px-4">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            className="text-center mb-16"
          >
            <Badge className="mb-4 text-sm px-4 py-2 bg-purple-500/20 text-purple-200 border-purple-400/30">
              <Eye className="w-4 h-4 mr-2 inline" />
              Демонстрация
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                Посмотрите результаты
              </span>
            </h2>
            <p className="text-xl text-purple-100 max-w-2xl mx-auto">
              Реальный интерфейс платформы с результатами AI-анализа резюме
            </p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={scaleIn}
            className="max-w-7xl mx-auto"
          >
            {/* Interactive Demo Table */}
            <div className="relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 rounded-3xl blur opacity-30"></div>
              <div className="relative bg-white rounded-2xl overflow-hidden shadow-2xl border-2 border-purple-300/30">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gradient-to-r from-slate-50 to-purple-50 border-b-2 border-slate-200">
                      <tr>
                        <th className="text-left p-3 font-semibold text-slate-800 text-xs border-r border-slate-200">
                          Кандидат
                        </th>
                        <th className="text-left p-3 font-semibold text-slate-800 text-xs border-r border-slate-200">
                          Контакты
                        </th>
                        <th className="text-left p-3 font-semibold text-slate-800 text-xs border-r border-slate-200">
                          Опыт
                        </th>
                        <th className="text-left p-3 font-semibold text-slate-800 text-xs border-r border-slate-200">
                          Релевантность
                        </th>
                        <th className="text-left p-3 font-semibold text-slate-800 text-xs border-r border-slate-200">
                          Ожидания по ЗП
                        </th>
                        <th className="text-left p-3 font-semibold text-slate-800 text-xs border-r border-slate-200">
                          Локация
                        </th>
                        <th className="text-left p-3 font-semibold text-slate-800 text-xs">
                          Итоговая оценка
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        {
                          name: 'Артём Волков',
                          position: 'Senior Java Developer',
                          social: '@volkov_dev',
                          phone: '+7 (925) 123-4567',
                          email: 'a.volkov@mail.ru',
                          experience: '7 лет',
                          relevance: 98,
                          salary: '280 000 ₽',
                          location: 'Москва',
                          assessment: 'Отличный кандидат: соответствует всем требованиям',
                          badgeColor: 'bg-orange-500',
                          relevanceColor: 'bg-green-500',
                        },
                        {
                          name: 'Анна Соколова',
                          position: 'Middle Frontend Developer',
                          social: '@sokolova_anna',
                          phone: '+7 (916) 987-6543',
                          email: 'anna.s@gmail.com',
                          experience: '4 года',
                          relevance: 92,
                          salary: '180 000 ₽',
                          location: 'Санкт-Петербург',
                          assessment: 'Хороший кандидат: показывает быстрый рост',
                          badgeColor: 'bg-orange-500',
                          relevanceColor: 'bg-blue-500',
                        },
                        {
                          name: 'Дмитрий Новиков',
                          position: 'Senior Backend Developer',
                          social: '@novikov_dev',
                          phone: '+7 (903) 456-7890',
                          email: 'd.novikov@mail.ru',
                          experience: '6 лет',
                          relevance: 89,
                          salary: '250 000 ₽',
                          location: 'Новосибирск',
                          assessment: 'Подходящий кандидат: сильные навыки',
                          badgeColor: 'bg-orange-500',
                          relevanceColor: 'bg-yellow-500',
                        },
                      ].map((candidate, i) => (
                        <motion.tr
                          key={i}
                          initial={{ opacity: 0, x: -20 }}
                          whileInView={{ opacity: 1, x: 0 }}
                          viewport={{ once: true }}
                          transition={{ delay: i * 0.1 }}
                          className="border-b border-slate-100 hover:bg-purple-50/30 transition-colors"
                        >
                          <td className="p-3 border-r border-slate-100">
                            <div className="font-bold text-slate-900 text-sm mb-1">
                              {candidate.name}
                            </div>
                            <div className={`${candidate.badgeColor} text-white text-[10px] font-semibold px-2 py-1 rounded-full inline-block`}>
                              {candidate.position}
                            </div>
                          </td>

                          <td className="p-3 border-r border-slate-100">
                            <div className="space-y-1 text-[11px]">
                              <div className="flex items-center gap-1.5 text-blue-600">
                                <MessageCircle className="w-3 h-3 flex-shrink-0" />
                                <span>{candidate.social}</span>
                              </div>
                              <div className="flex items-center gap-1.5 text-slate-600">
                                <Phone className="w-3 h-3 flex-shrink-0" />
                                <span>{candidate.phone}</span>
                              </div>
                              <div className="flex items-center gap-1.5 text-slate-600">
                                <Mail className="w-3 h-3 flex-shrink-0" />
                                <span>{candidate.email}</span>
                              </div>
                            </div>
                          </td>

                          <td className="p-3 text-slate-900 border-r border-slate-100 text-center">
                            <div className="font-medium text-sm">{candidate.experience}</div>
                          </td>

                          <td className="p-3 border-r border-slate-100">
                            <div className="flex items-center gap-2">
                              <div className="flex-1">
                                <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    whileInView={{ width: `${candidate.relevance}%` }}
                                    viewport={{ once: true }}
                                    transition={{ duration: 1, delay: i * 0.1 + 0.3 }}
                                    className={`h-full ${candidate.relevanceColor}`}
                                  />
                                </div>
                              </div>
                              <div className="font-bold text-slate-900 text-sm min-w-[2ch]">
                                {candidate.relevance}
                              </div>
                            </div>
                          </td>

                          <td className="p-3 border-r border-slate-100">
                            <div className="font-semibold text-slate-900 text-sm">
                              {candidate.salary}
                            </div>
                          </td>

                          <td className="p-3 border-r border-slate-100">
                            <div className="flex items-center gap-1.5 text-slate-700">
                              <MapPin className="w-3 h-3 flex-shrink-0" />
                              <span className="text-xs">{candidate.location}</span>
                            </div>
                          </td>

                          <td className="p-3">
                            <div className="text-xs text-slate-700 leading-relaxed">
                              {candidate.assessment}
                            </div>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Feature cards */}
            <div className="grid md:grid-cols-3 gap-6 mt-12">
              {[
                {
                  icon: Users,
                  title: 'Собеседование',
                  description: 'Лучшие кандидаты с оценкой 80+ баллов',
                  iconColor: 'text-green-400',
                  bgColor: 'bg-green-500/10',
                  borderColor: 'border-green-500/20',
                },
                {
                  icon: ThumbsUp,
                  title: 'Возможно',
                  description: 'Кандидаты требующие дополнительной оценки',
                  iconColor: 'text-yellow-400',
                  bgColor: 'bg-yellow-500/10',
                  borderColor: 'border-yellow-500/20',
                },
                {
                  icon: XCircle,
                  title: 'Отклонить',
                  description: 'Не подходят по ключевым критериям',
                  iconColor: 'text-red-400',
                  bgColor: 'bg-red-500/10',
                  borderColor: 'border-red-500/20',
                },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  whileHover={{ scale: 1.05, y: -5 }}
                  className={`${item.bgColor} ${item.borderColor} border-2 rounded-2xl p-6 backdrop-blur-sm transition-all duration-300`}
                >
                  <item.icon className={`h-12 w-12 ${item.iconColor} mx-auto mb-4`} />
                  <h3 className="font-bold text-xl mb-2 text-white text-center">
                    {item.title}
                  </h3>
                  <p className="text-purple-100 text-sm text-center leading-relaxed">
                    {item.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Возможности - сокращенные до 6 пунктов - БЛОК 5 */}
      <section className="py-20 bg-slate-900">
        <div className="container mx-auto px-4">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeInUp}
            className="text-center mb-16"
          >
            <Badge className="mb-4 text-sm px-4 py-2 bg-purple-500/20 text-purple-200 border-purple-400/30">
              <Brain className="w-4 h-4 mr-2 inline" />
              Возможности
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-white">
              Все инструменты для{' '}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                идеального найма
              </span>
            </h2>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
          >
            {[
              {
                icon: Brain,
                title: 'AI-анализ резюме',
                description:
                  'Искусственный интеллект анализирует резюме по 15+ критериям: навыки, опыт, образование и многое другое.',
                gradient: 'from-purple-500 to-purple-600',
              },
              {
                icon: Target,
                title: 'Умное ранжирование',
                description:
                  'Система автоматически выставляет оценки кандидатам и сортирует их по релевантности вакансии.',
                gradient: 'from-pink-500 to-pink-600',
              },
              {
                icon: Zap,
                title: 'Мгновенная обработка',
                description:
                  'Анализируйте сотни резюме за минуты. 100 резюме за 10-15 минут вместо 8 часов ручной работы.',
                gradient: 'from-blue-500 to-blue-600',
              },
              {
                icon: Download,
                title: 'Экспорт в Excel',
                description:
                  'Выгружайте результаты в Excel с графиками, диаграммами и фильтрами для удобной работы.',
                gradient: 'from-purple-500 to-pink-500',
              },
              {
                icon: Users,
                title: 'Интеграция с HH.ru',
                description:
                  'Прямая интеграция с HeadHunter. Автоматическая синхронизация вакансий и откликов.',
                gradient: 'from-pink-500 to-blue-500',
              },
              {
                icon: Shield,
                title: 'Безопасность данных',
                description:
                  'Все данные надежно зашифрованы и хранятся в защищенных дата-центрах России.',
                gradient: 'from-blue-500 to-purple-500',
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                variants={fadeInUp}
                whileHover={{ scale: 1.03, y: -5 }}
                transition={{ duration: 0.2 }}
              >
                <Card className="h-full hover:shadow-2xl transition-all duration-300 border-2 border-purple-500/20 bg-purple-500/5 backdrop-blur-sm hover:border-purple-400/50">
                  <CardHeader>
                    <div
                      className={`h-16 w-16 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 shadow-lg hover:shadow-xl transition-shadow`}
                    >
                      <feature.icon className="h-8 w-8 text-white" />
                    </div>
                    <CardTitle className="text-xl text-white">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base leading-relaxed text-purple-200">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA секция */}
      <section className="py-20 bg-gradient-to-br from-purple-600 via-pink-600 to-blue-600 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC40Ij48cGF0aCBkPSJNMzYgMzBoLTJWMGgydjMwem0wIDMwdi0yaDMwdjJIMzZ6TTAgMzBoMzB2Mkgwdi0yem0zMCAwVjBoMnYzMGgtMnoiLz48L2c+PC9nPjwvc3ZnPg==')]" />
        </div>

        <div className="container relative mx-auto px-4 text-center">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp}>
              <Badge className="mb-6 text-sm px-4 py-2 bg-white/20 text-white border-white/30">
                <Sparkles className="w-4 h-4 mr-2 inline" />
                Присоединяйтесь к успешным компаниям
              </Badge>
            </motion.div>

            <motion.h2
              variants={fadeInUp}
              className="text-4xl md:text-6xl font-bold mb-6 text-white"
            >
              Готовы революционизировать найм?
            </motion.h2>

            <motion.p variants={fadeInUp} className="text-xl mb-8 text-white/90 max-w-2xl mx-auto">
              Начните бесплатно прямо сейчас. 50 анализов в Trial — в подарок.
              <br />
              Кредитная карта не требуется.
            </motion.p>

            <motion.div
              variants={fadeInUp}
              className="flex gap-4 justify-center flex-wrap mb-8"
            >
              <Button
                asChild
                size="lg"
                className="bg-white text-purple-600 hover:bg-gray-100 shadow-2xl text-lg px-10 py-7"
              >
                <Link to="/register">
                  <Rocket className="mr-2 h-6 w-6" />
                  Начать бесплатно
                  <ArrowRight className="ml-2 h-6 w-6" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                className="bg-white/10 backdrop-blur-sm border-2 border-white/50 text-white hover:bg-white hover:text-purple-600 hover:border-white text-lg px-10 py-7 transition-all shadow-lg hover:shadow-2xl hover:scale-105"
              >
                <Link to="/login">Уже есть аккаунт</Link>
              </Button>
            </motion.div>

            <motion.div
              variants={fadeInUp}
              className="flex gap-8 justify-center text-white/90 flex-wrap"
            >
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                <span>Быстрая регистрация</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                <span>50 анализов бесплатно</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                <span>Без автоплатежей</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-purple-800 bg-slate-900 text-white">
        <div className="container mx-auto px-4 py-12">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <img src="/logo.jpg" alt="Timly" className="h-12 w-12 rounded-xl object-cover" />
                <span className="text-2xl font-bold">Timly</span>
              </div>
              <p className="text-purple-300 text-sm">
                AI-платформа для автоматизации отбора кандидатов
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Продукт</h4>
              <ul className="space-y-2 text-sm text-purple-300">
                <li>
                  <a href="#features" className="hover:text-white transition-colors">
                    Возможности
                  </a>
                </li>
                <li>
                  <a href="#demo" className="hover:text-white transition-colors">
                    Демо
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Поддержка</h4>
              <ul className="space-y-2 text-sm text-purple-300">
                <li>
                  <a href="mailto:support@timly-hr.ru" className="hover:text-white transition-colors">
                    support@timly-hr.ru
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-purple-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-purple-300">
            <p>&copy; 2024 Timly. AI-powered Resume Screening Platform. Все права защищены.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
