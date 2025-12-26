/**
 * Landing - Timly HR Platform
 * Design: Dark Industrial - единый стиль с ЛК, плотная компоновка
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Check,
  X,
  Zap,
  Download,
  Shield,
  Clock,
  Users,
  BarChart3,
  ExternalLink,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const Landing: React.FC = () => {
  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const stagger = {
    visible: {
      transition: { staggerChildren: 0.1 },
    },
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.jpg" alt="Timly" className="h-8 w-8 rounded-lg" />
            <span className="text-lg font-semibold">Timly</span>
          </div>
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="sm" className="text-zinc-400 hover:text-zinc-100">
              <Link to="/login">Войти</Link>
            </Button>
            <Button asChild size="sm" className="bg-zinc-100 text-zinc-900 hover:bg-white">
              <Link to="/register">Начать бесплатно</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="grid lg:grid-cols-2 gap-12 items-center"
          >
            {/* Left: Text */}
            <div className="space-y-6">
              <motion.div variants={fadeIn}>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-800 text-xs text-zinc-400 mb-4">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                  Интеграция с HH.ru
                </div>
              </motion.div>

              <motion.h1
                variants={fadeIn}
                className="text-4xl lg:text-5xl font-semibold tracking-tight leading-[1.1]"
              >
                100 резюме за 10 минут.
                <br />
                <span className="text-zinc-500">AI находит лучших.</span>
              </motion.h1>

              <motion.p variants={fadeIn} className="text-lg text-zinc-400 leading-relaxed">
                Автоматический скрининг откликов с HeadHunter.
                Оценка по 15+ критериям. Топ-кандидаты в Excel.
              </motion.p>

              <motion.div variants={fadeIn} className="flex gap-3">
                <Button asChild size="lg" className="bg-zinc-100 text-zinc-900 hover:bg-white h-12 px-6">
                  <Link to="/register">
                    Попробовать бесплатно
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 h-12 px-6">
                  <Link to="/login">Войти</Link>
                </Button>
              </motion.div>

              <motion.div variants={fadeIn} className="flex items-center gap-6 text-sm text-zinc-500">
                <span className="flex items-center gap-1.5">
                  <Check className="h-4 w-4 text-green-500" />
                  50 анализов бесплатно
                </span>
                <span className="flex items-center gap-1.5">
                  <Check className="h-4 w-4 text-green-500" />
                  Без карты
                </span>
                <span className="flex items-center gap-1.5">
                  <Check className="h-4 w-4 text-green-500" />
                  2 минуты на старт
                </span>
              </motion.div>
            </div>

            {/* Right: Stats grid */}
            <motion.div variants={fadeIn}>
              <div className="grid grid-cols-2 gap-px bg-zinc-800 rounded-xl overflow-hidden">
                {[
                  { value: '10', unit: 'мин', label: 'на 100 резюме', sub: 'вместо 8 часов' },
                  { value: '95%', unit: '', label: 'точность оценки', sub: 'по 15+ критериям' },
                  { value: '80%', unit: '', label: 'экономия времени', sub: 'на скрининге' },
                  { value: '50', unit: '', label: 'анализов бесплатно', sub: 'в Trial тарифе' },
                ].map((stat, i) => (
                  <div key={i} className="bg-[#111] p-6">
                    <div className="text-3xl font-semibold tracking-tight tabular-nums">
                      {stat.value}
                      <span className="text-lg text-zinc-500">{stat.unit}</span>
                    </div>
                    <div className="text-sm text-zinc-400 mt-1">{stat.label}</div>
                    <div className="text-xs text-zinc-600 mt-0.5">{stat.sub}</div>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Problem → Solution */}
      <section className="border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="text-center mb-10">
              <h2 className="text-2xl font-semibold mb-2">Знакомая ситуация?</h2>
              <p className="text-zinc-500">Ручной скрининг vs Timly AI</p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Problem */}
              <motion.div variants={fadeIn}>
                <Card className="bg-red-500/5 border-red-500/20 h-full">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center">
                        <X className="h-4 w-4 text-red-500" />
                      </div>
                      <span className="font-medium text-red-400">Ручной отбор</span>
                    </div>
                    <div className="space-y-3">
                      {[
                        '8+ часов на просмотр 100 резюме',
                        'К вечеру все кандидаты "на одно лицо"',
                        'Субъективная оценка без критериев',
                        'Пропустили сильного — ушёл к конкуренту',
                        'Нет аналитики для руководства',
                      ].map((item, i) => (
                        <div key={i} className="flex items-start gap-2 text-sm text-zinc-400">
                          <X className="h-4 w-4 text-red-500/70 mt-0.5 flex-shrink-0" />
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Solution */}
              <motion.div variants={fadeIn}>
                <Card className="bg-green-500/5 border-green-500/20 h-full">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
                        <Check className="h-4 w-4 text-green-500" />
                      </div>
                      <span className="font-medium text-green-400">Timly AI</span>
                    </div>
                    <div className="space-y-3">
                      {[
                        '10-15 минут на 100 резюме',
                        'Объективная оценка каждого кандидата',
                        '15+ критериев: навыки, опыт, зарплата',
                        'Топ-кандидаты всегда наверху списка',
                        'Excel-отчёт с графиками и метриками',
                      ].map((item, i) => (
                        <div key={i} className="flex items-start gap-2 text-sm text-zinc-400">
                          <Check className="h-4 w-4 text-green-500/70 mt-0.5 flex-shrink-0" />
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="text-center mb-10">
              <h2 className="text-2xl font-semibold mb-2">Как это работает</h2>
              <p className="text-zinc-500">3 шага до первых результатов</p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-px bg-zinc-800 rounded-xl overflow-hidden">
              {[
                {
                  step: '01',
                  title: 'Подключите HH.ru',
                  desc: 'Добавьте API-токен HeadHunter в настройках. Занимает 2 минуты.',
                  icon: Users,
                },
                {
                  step: '02',
                  title: 'Синхронизируйте',
                  desc: 'Нажмите одну кнопку — система загрузит вакансии и отклики.',
                  icon: Zap,
                },
                {
                  step: '03',
                  title: 'Получите отчёт',
                  desc: 'AI проанализирует резюме и выдаст топ-кандидатов с оценками.',
                  icon: BarChart3,
                },
              ].map((item, i) => (
                <motion.div key={i} variants={fadeIn} className="bg-[#111] p-6 relative">
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-4xl font-bold text-zinc-800">{item.step}</div>
                    <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
                      <item.icon className="h-5 w-5 text-zinc-400" />
                    </div>
                  </div>
                  <h3 className="text-lg font-medium mb-2">{item.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Demo / Interface preview */}
      <section className="border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="text-center mb-10">
              <h2 className="text-2xl font-semibold mb-2">Результаты анализа</h2>
              <p className="text-zinc-500">Так выглядит отчёт по кандидатам</p>
            </motion.div>

            <motion.div variants={fadeIn}>
              <Card className="border-zinc-800 overflow-hidden">
                <CardContent className="p-0">
                  {/* Header */}
                  <div className="px-5 py-3 border-b border-zinc-800 bg-[#0f0f0f] flex items-center justify-between">
                    <span className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
                      Менеджер по продажам — 47 откликов
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-zinc-600">Экспорт</span>
                      <Download className="h-3.5 w-3.5 text-zinc-600" />
                    </div>
                  </div>

                  {/* Table */}
                  <div className="divide-y divide-zinc-800/50">
                    {[
                      { name: 'Артём Волков', score: 94, status: 'hire', skills: 92, exp: '7 лет', salary: '280 000 ₽' },
                      { name: 'Мария Соколова', score: 87, status: 'interview', skills: 85, exp: '4 года', salary: '180 000 ₽' },
                      { name: 'Дмитрий Новиков', score: 76, status: 'maybe', skills: 78, exp: '3 года', salary: '150 000 ₽' },
                      { name: 'Елена Петрова', score: 45, status: 'reject', skills: 42, exp: '1 год', salary: '120 000 ₽' },
                    ].map((c, i) => (
                      <div key={i} className="px-5 py-4 flex items-center gap-4 hover:bg-zinc-900/50 transition-colors">
                        {/* Avatar */}
                        <div className="w-9 h-9 rounded-lg bg-zinc-800 flex items-center justify-center text-[11px] font-medium text-zinc-500">
                          {c.name.split(' ').map(n => n[0]).join('')}
                        </div>

                        {/* Name */}
                        <div className="flex-1 min-w-0">
                          <div className="text-[13px] font-medium">{c.name}</div>
                          <div className="text-xs text-zinc-600">{c.exp} опыта · {c.salary}</div>
                        </div>

                        {/* Skills bar */}
                        <div className="w-24 hidden sm:block">
                          <div className="text-[10px] text-zinc-600 mb-1">Навыки {c.skills}%</div>
                          <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                            <div className="h-full bg-zinc-500 rounded-full" style={{ width: `${c.skills}%` }} />
                          </div>
                        </div>

                        {/* Score */}
                        <div className="text-right">
                          <div className="text-lg font-semibold tabular-nums">{c.score}</div>
                          <div className="text-[10px] text-zinc-600">баллов</div>
                        </div>

                        {/* Status */}
                        <span className={`px-2.5 py-1 rounded text-[11px] font-medium ${
                          c.status === 'hire' ? 'bg-green-500/15 text-green-500' :
                          c.status === 'interview' ? 'bg-blue-500/15 text-blue-500' :
                          c.status === 'maybe' ? 'bg-amber-500/15 text-amber-500' :
                          'bg-red-500/15 text-red-500'
                        }`}>
                          {c.status === 'hire' ? 'Нанять' :
                           c.status === 'interview' ? 'Интервью' :
                           c.status === 'maybe' ? 'Возможно' : 'Отказ'}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Footer */}
                  <div className="px-5 py-3 border-t border-zinc-800 bg-[#0f0f0f] flex items-center justify-between">
                    <div className="flex items-center gap-4 text-xs text-zinc-600">
                      <span><span className="text-green-500">12</span> нанять</span>
                      <span><span className="text-blue-500">18</span> интервью</span>
                      <span><span className="text-amber-500">9</span> возможно</span>
                      <span><span className="text-red-500">8</span> отказ</span>
                    </div>
                    <span className="text-xs text-zinc-600">Ср. балл: 72</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features grid */}
      <section className="border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="text-center mb-10">
              <h2 className="text-2xl font-semibold mb-2">Возможности</h2>
              <p className="text-zinc-500">Всё для эффективного найма</p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-px bg-zinc-800 rounded-xl overflow-hidden">
              {[
                {
                  icon: BarChart3,
                  title: 'AI-анализ резюме',
                  desc: 'Оценка по 15+ критериям: навыки, опыт, образование, соответствие вакансии',
                },
                {
                  icon: Users,
                  title: 'Интеграция с HH.ru',
                  desc: 'Автоматическая синхронизация вакансий и откликов одной кнопкой',
                },
                {
                  icon: Download,
                  title: 'Экспорт в Excel',
                  desc: 'Готовый отчёт с графиками, фильтрами и контактами кандидатов',
                },
                {
                  icon: Zap,
                  title: 'Быстрая обработка',
                  desc: '100 резюме за 10-15 минут вместо 8 часов ручной работы',
                },
                {
                  icon: Clock,
                  title: 'Экономия 80% времени',
                  desc: 'Занимайтесь собеседованиями, а не рутинным скринингом',
                },
                {
                  icon: Shield,
                  title: 'Безопасность',
                  desc: 'Данные зашифрованы и хранятся в защищённых дата-центрах РФ',
                },
              ].map((f, i) => (
                <motion.div key={i} variants={fadeIn} className="bg-[#111] p-6">
                  <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center mb-4">
                    <f.icon className="h-5 w-5 text-zinc-400" />
                  </div>
                  <h3 className="font-medium mb-2">{f.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">{f.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Who is it for */}
      <section className="border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="text-center mb-10">
              <h2 className="text-2xl font-semibold mb-2">Timly подходит вам, если</h2>
            </motion.div>

            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-4">
              {[
                { text: 'Используете HH.ru для найма', icon: ExternalLink },
                { text: 'Получаете 50+ откликов на вакансию', icon: Users },
                { text: 'Хотите тратить время на интервью, а не скрининг', icon: Clock },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-3 p-4 rounded-lg bg-zinc-900/50 border border-zinc-800">
                  <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center flex-shrink-0">
                    <Check className="h-4 w-4 text-green-500" />
                  </div>
                  <span className="text-sm text-zinc-300">{item.text}</span>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 py-20">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
            className="text-center"
          >
            <motion.h2 variants={fadeIn} className="text-3xl lg:text-4xl font-semibold mb-4">
              Попробуйте бесплатно
            </motion.h2>
            <motion.p variants={fadeIn} className="text-zinc-500 mb-8 max-w-lg mx-auto">
              50 анализов в подарок. Без кредитной карты. Настройка за 2 минуты.
            </motion.p>

            <motion.div variants={fadeIn} className="flex gap-3 justify-center">
              <Button asChild size="lg" className="bg-zinc-100 text-zinc-900 hover:bg-white h-12 px-8">
                <Link to="/register">
                  Начать бесплатно
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </motion.div>

            <motion.div variants={fadeIn} className="flex items-center justify-center gap-6 mt-6 text-sm text-zinc-600">
              <span>✓ 50 анализов бесплатно</span>
              <span>✓ Без автоплатежей</span>
              <span>✓ Отмена в любой момент</span>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <img src="/logo.jpg" alt="Timly" className="h-8 w-8 rounded-lg" />
              <span className="font-medium">Timly</span>
              <span className="text-zinc-600 text-sm">AI-скрининг резюме</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-zinc-500">
              <a href="mailto:support@timly-hr.ru" className="hover:text-zinc-300 transition-colors">
                support@timly-hr.ru
              </a>
              <span>© 2024 Timly</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
