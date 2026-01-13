/**
 * Landing - Timly HR Platform
 *
 * Design Direction: "Warm Professional" - human-centric, trustworthy, distinctive
 * NOT generic AI slop - bold choices, memorable details
 *
 * Typography: Clash Display (headlines) + Satoshi (body)
 * Palette: Deep Navy (#1e3a5f) + Warm Orange (#f97316) + Warm White (#faf8f5)
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  ChevronDown,
  Mail,
  MessageCircle,
  Shield,
  Eye,
  Lock,
  CheckCircle2,
  Clock,
  Users,
  TrendingUp,
  Target,
  BarChart3,
  Briefcase
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const Landing: React.FC = () => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [showStickyCta, setShowStickyCta] = useState(false);

  useEffect(() => {
    const handleScroll = () => setShowStickyCta(window.scrollY > 500);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const fadeIn = {
    hidden: { opacity: 0, y: 24 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.25, 0.1, 0.25, 1] } }
  };
  const stagger = { visible: { transition: { staggerChildren: 0.12 } } };

  return (
    <div className="min-h-screen bg-[#faf8f5] text-[#1c1917]" style={{ fontFamily: "'Satoshi', sans-serif" }}>
      {/* Fonts: Clash Display + Satoshi from Fontshare */}
      <style>{`
        @import url('https://api.fontshare.com/v2/css?f[]=clash-display@600,700&f[]=satoshi@400,500,700&display=swap');
        .font-display { font-family: 'Clash Display', sans-serif; letter-spacing: -0.02em; }
        .font-body { font-family: 'Satoshi', sans-serif; }
      `}</style>

      {/* Header */}
      <header className="border-b border-[#1e3a5f]/10 sticky top-0 bg-[#faf8f5]/95 backdrop-blur-sm z-50">
        <div className="max-w-5xl mx-auto px-5 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-[#1e3a5f] flex items-center justify-center">
              <span className="text-white font-bold text-base font-display">T</span>
            </div>
            <span className="text-xl font-display font-semibold text-[#1e3a5f]">timly</span>
          </Link>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[#1e3a5f]/70">
            <a href="#how-it-works" className="hover:text-[#1e3a5f] transition-colors">Как работает</a>
            <a href="#pricing" className="hover:text-[#1e3a5f] transition-colors">Тарифы</a>
            <a href="#faq" className="hover:text-[#1e3a5f] transition-colors">Вопросы</a>
          </nav>
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="sm" className="text-[#1e3a5f] hover:text-[#1e3a5f] hover:bg-[#1e3a5f]/5 text-sm h-10 font-medium">
              <Link to="/login">Войти</Link>
            </Button>
            <Button asChild size="sm" className="bg-[#1e3a5f] hover:bg-[#1e3a5f]/90 text-white text-sm h-10 px-5 font-medium">
              <Link to="/register">Начать</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero - with gradient mesh background */}
      <section className="relative overflow-hidden">
        {/* Gradient mesh background */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-[#f97316]/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-[#1e3a5f]/8 rounded-full blur-3xl" />
        </div>

        <div className="max-w-5xl mx-auto px-5 py-20 md:py-28">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <motion.div initial="hidden" animate="visible" variants={stagger}>
              {/* Removed AI-slop badge - straight to the point */}

              <motion.h1 variants={fadeIn} className="font-display text-[2.75rem] md:text-[3.5rem] leading-[1.05] mb-6 text-[#1e3a5f] font-semibold">
                Разберите 100 откликов<br />
                <span className="text-[#f97316]">за 15 минут</span>
              </motion.h1>

              <motion.p variants={fadeIn} className="text-lg text-[#1e3a5f]/70 leading-relaxed mb-10 max-w-md">
                Подключите HeadHunter — получите отсортированный список кандидатов с понятными оценками и объяснениями.
              </motion.p>

              <motion.div variants={fadeIn} className="flex flex-col sm:flex-row gap-4 mb-8">
                <Button asChild size="lg" className="bg-[#f97316] hover:bg-[#ea580c] text-white h-14 px-10 text-base font-semibold rounded-xl shadow-lg shadow-[#f97316]/25 transition-all hover:shadow-xl hover:shadow-[#f97316]/30 hover:-translate-y-0.5">
                  <Link to="/register">
                    Проанализировать 50 резюме бесплатно
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              </motion.div>

              <motion.div variants={fadeIn} className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-[#1e3a5f]/60 mb-10">
                <span className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-[#059669]" />
                  50 резюме бесплатно
                </span>
                <span className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-[#059669]" />
                  Без карты
                </span>
                <span className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-[#059669]" />
                  Настройка 2 минуты
                </span>
              </motion.div>

              {/* Security - simplified */}
              <motion.div variants={fadeIn} className="flex items-center gap-3 text-sm text-[#1e3a5f]/50">
                <Shield className="w-4 h-4" />
                <span>Только чтение откликов · Данные в России</span>
              </motion.div>
            </motion.div>

            {/* Product Preview - with slight rotation for visual interest */}
            <motion.div
              initial={{ opacity: 0, y: 30, rotate: 0 }}
              animate={{ opacity: 1, y: 0, rotate: -1 }}
              transition={{ delay: 0.3, duration: 0.7, ease: [0.25, 0.1, 0.25, 1] }}
              className="relative"
            >
              {/* Decorative element */}
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-[#f97316]/20 rounded-full blur-2xl" />

              <div className="bg-white rounded-2xl border border-[#1e3a5f]/10 shadow-2xl shadow-[#1e3a5f]/10 overflow-hidden">
                <div className="px-5 py-4 border-b border-[#1e3a5f]/5 flex items-center justify-between bg-[#1e3a5f]/[0.02]">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-[#1e3a5f]/20" />
                      <div className="w-3 h-3 rounded-full bg-[#1e3a5f]/20" />
                      <div className="w-3 h-3 rounded-full bg-[#1e3a5f]/20" />
                    </div>
                    <span className="text-sm text-[#1e3a5f]/60 font-medium">Менеджер по продажам — 98 откликов</span>
                  </div>
                </div>
                <div className="p-5 space-y-3">
                  {[
                    { name: 'Анна Волкова', role: 'Менеджер по продажам, 5 лет', score: 87, tag: 'Пригласить', level: 'high' },
                    { name: 'Дмитрий Козлов', role: 'Sales Manager, 3 года', score: 74, tag: 'Рассмотреть', level: 'medium' },
                    { name: 'Игорь Сидоров', role: 'Продавец-консультант, 1 год', score: 41, tag: 'Не подходит', level: 'low' },
                  ].map((item, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + i * 0.12 }}
                      className={`p-4 rounded-xl border transition-all hover:shadow-md cursor-pointer ${
                        item.level === 'high'
                          ? 'bg-[#059669]/5 border-[#059669]/20 hover:border-[#059669]/40'
                          : item.level === 'low'
                          ? 'bg-[#dc2626]/5 border-[#dc2626]/20'
                          : 'bg-white border-[#1e3a5f]/10 hover:border-[#1e3a5f]/20'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-11 h-11 rounded-xl flex items-center justify-center text-sm font-semibold ${
                            item.level === 'high' ? 'bg-[#059669]/10 text-[#059669]' :
                            item.level === 'low' ? 'bg-[#dc2626]/10 text-[#dc2626]' :
                            'bg-[#1e3a5f]/5 text-[#1e3a5f]'
                          }`}>
                            {item.name.split(' ').map(n => n[0]).join('')}
                          </div>
                          <div>
                            <p className="font-medium text-[#1e3a5f]">{item.name}</p>
                            <p className="text-sm text-[#1e3a5f]/50">{item.role}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-2xl font-display font-semibold tabular-nums ${
                            item.level === 'high' ? 'text-[#059669]' :
                            item.level === 'low' ? 'text-[#dc2626]' :
                            'text-[#d97706]'
                          }`}>
                            {item.score}
                          </div>
                          <span className={`text-xs font-medium ${
                            item.level === 'high' ? 'text-[#059669]' :
                            item.level === 'low' ? 'text-[#dc2626]' :
                            'text-[#d97706]'
                          }`}>
                            {item.tag}
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                  <p className="text-center text-sm text-[#1e3a5f]/40 pt-2">+ ещё 95 кандидатов</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="border-b border-[#1e3a5f]/5 bg-white">
        <div className="max-w-5xl mx-auto px-5 py-20 md:py-24">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.p variants={fadeIn} className="text-sm font-medium text-[#f97316] mb-3">Знакомо?</motion.p>
            <motion.h2 variants={fadeIn} className="font-display text-2xl md:text-[2rem] mb-12 max-w-xl leading-snug font-semibold text-[#1e3a5f]">
              Вы тратите часы на чтение резюме, а в итоге всё равно не уверены, что никого не пропустили
            </motion.h2>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-5">
              {[
                { icon: Clock, text: 'После 30-го отклика все резюме сливаются в одно' },
                { icon: Users, text: 'Хорошие кандидаты теряются среди нерелевантных' },
                { icon: Eye, text: 'Нет объективных критериев — только интуиция и усталость' },
              ].map((item, i) => (
                <div key={i} className="p-6 rounded-2xl bg-[#faf8f5] border border-[#1e3a5f]/5 hover:border-[#1e3a5f]/15 transition-colors">
                  <item.icon className="w-6 h-6 text-[#1e3a5f]/40 mb-4" />
                  <p className="text-[#1e3a5f]/70 leading-relaxed">{item.text}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* What Timly Analyzes - NEW SECTION */}
      <section className="border-b border-[#1e3a5f]/5">
        <div className="max-w-5xl mx-auto px-5 py-20 md:py-24">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.p variants={fadeIn} className="text-sm font-medium text-[#f97316] mb-3">Что анализируем</motion.p>
            <motion.h2 variants={fadeIn} className="font-display text-2xl md:text-[2rem] mb-4 font-semibold text-[#1e3a5f]">
              Не keyword-matching, а понимание контекста
            </motion.h2>
            <motion.p variants={fadeIn} className="text-[#1e3a5f]/60 mb-12 max-w-lg">
              AI анализирует резюме как опытный рекрутер — смотрит на картину целиком, а не ищет ключевые слова.
            </motion.p>
            <motion.div variants={fadeIn} className="grid md:grid-cols-4 gap-4">
              {[
                { icon: Briefcase, title: 'Релевантный опыт', desc: 'Соответствие требованиям вакансии' },
                { icon: TrendingUp, title: 'Карьерный рост', desc: 'Динамика развития кандидата' },
                { icon: Target, title: 'Стабильность', desc: 'Частота смены работы в контексте' },
                { icon: BarChart3, title: 'Потенциальные риски', desc: 'Красные флаги и что уточнить' },
              ].map((item, i) => (
                <div key={i} className="p-5 rounded-xl bg-white border border-[#1e3a5f]/5 hover:border-[#f97316]/30 hover:shadow-lg hover:shadow-[#f97316]/5 transition-all">
                  <item.icon className="w-5 h-5 text-[#f97316] mb-3" />
                  <h3 className="font-semibold text-[#1e3a5f] mb-1">{item.title}</h3>
                  <p className="text-sm text-[#1e3a5f]/50">{item.desc}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-b border-[#1e3a5f]/5 bg-white">
        <div className="max-w-5xl mx-auto px-5 py-20 md:py-24">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.p variants={fadeIn} className="text-sm font-medium text-[#f97316] mb-3">Как это работает</motion.p>
            <motion.h2 variants={fadeIn} className="font-display text-2xl md:text-[2rem] mb-4 font-semibold text-[#1e3a5f]">
              3 шага до результата
            </motion.h2>
            <motion.p variants={fadeIn} className="text-[#1e3a5f]/60 mb-12 max-w-lg">
              Никакой сложной настройки. Подключите HH, выберите вакансию — готово.
            </motion.p>

            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-8 mb-16">
              {[
                {
                  step: '01',
                  title: 'Подключите HeadHunter',
                  desc: 'Авторизуйтесь через OAuth. Мы получим доступ только к чтению откликов.'
                },
                {
                  step: '02',
                  title: 'Выберите вакансию',
                  desc: 'Timly автоматически загрузит все отклики на выбранную вакансию.'
                },
                {
                  step: '03',
                  title: 'Получите результат',
                  desc: 'Через 10-15 минут — отсортированный список с оценками и объяснениями.'
                },
              ].map((item, i) => (
                <div key={i} className="relative">
                  <div className="font-display text-6xl text-[#1e3a5f]/10 mb-4 font-semibold">{item.step}</div>
                  <h3 className="font-semibold text-lg mb-2 text-[#1e3a5f]">{item.title}</h3>
                  <p className="text-[#1e3a5f]/60 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </motion.div>

            {/* Example analysis */}
            <motion.div variants={fadeIn}>
              <p className="text-sm font-medium text-[#f97316] mb-4">Пример оценки кандидата</p>
              <div className="bg-[#faf8f5] rounded-2xl border border-[#1e3a5f]/10 shadow-lg shadow-[#1e3a5f]/5 overflow-hidden">
                <div className="px-6 py-5 border-b border-[#1e3a5f]/5 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[#059669]/10 flex items-center justify-center text-lg font-semibold text-[#059669]">АВ</div>
                    <div>
                      <p className="font-semibold text-[#1e3a5f]">Анна Волкова</p>
                      <p className="text-sm text-[#1e3a5f]/50">Менеджер по продажам · 5 лет опыта</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-display font-semibold text-[#059669] tabular-nums">87</span>
                      <span className="text-[#1e3a5f]/30">/100</span>
                    </div>
                    <span className="text-sm font-medium text-[#059669]">Пригласить</span>
                  </div>
                </div>
                <div className="p-6">
                  <p className="text-sm font-medium text-[#1e3a5f]/50 mb-4">Почему такой балл:</p>
                  <div className="grid md:grid-cols-2 gap-3">
                    {[
                      { type: 'plus', title: 'Опыт B2B продаж 4 года', sub: 'Соответствует требованиям' },
                      { type: 'plus', title: 'Карьерный рост', sub: 'Менеджер → Старший менеджер' },
                      { type: 'warn', title: 'Последняя работа 8 мес', sub: 'Для менеджера продаж среднее — 1.5 года. Уточнить причину' },
                      { type: 'minus', title: 'Нет опыта с Bitrix', sub: 'Указан в требованиях вакансии' },
                    ].map((item, i) => (
                      <div key={i} className={`flex items-start gap-3 p-3 rounded-xl ${
                        item.type === 'plus' ? 'bg-[#059669]/5' : item.type === 'warn' ? 'bg-[#d97706]/5' : 'bg-[#1e3a5f]/5'
                      }`}>
                        <span className={`text-lg font-bold ${
                          item.type === 'plus' ? 'text-[#059669]' : item.type === 'warn' ? 'text-[#d97706]' : 'text-[#1e3a5f]/40'
                        }`}>
                          {item.type === 'plus' ? '+' : item.type === 'warn' ? '!' : '−'}
                        </span>
                        <div>
                          <p className="font-medium text-[#1e3a5f]">{item.title}</p>
                          <p className="text-sm text-[#1e3a5f]/50">{item.sub}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Your Control */}
      <section className="border-b border-[#1e3a5f]/5">
        <div className="max-w-5xl mx-auto px-5 py-20 md:py-24">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.p variants={fadeIn} className="text-sm font-medium text-[#f97316] mb-3">Ваш контроль</motion.p>
            <motion.h2 variants={fadeIn} className="font-display text-2xl md:text-[2rem] mb-4 font-semibold text-[#1e3a5f]">
              Система помогает, но решаете вы
            </motion.h2>
            <motion.p variants={fadeIn} className="text-[#1e3a5f]/60 mb-10 max-w-lg">
              Мы не удаляем кандидатов и не принимаем решения за вас.
            </motion.p>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-5">
              {[
                {
                  title: 'Видите всех кандидатов',
                  desc: 'Все резюме остаются в списке. Никто не отсеивается автоматически — только сортировка.',
                  icon: Users
                },
                {
                  title: 'Можете изменить оценку',
                  desc: 'Не согласны с баллом? Переоцените кандидата вручную. Ваше мнение важнее.',
                  icon: Eye
                },
                {
                  title: 'Полное резюме рядом',
                  desc: 'Всегда видите оригинал резюме с HH. Система показывает выводы, но исходник доступен.',
                  icon: CheckCircle2
                },
              ].map((item, i) => (
                <div key={i} className="p-6 rounded-2xl bg-white border border-[#1e3a5f]/5 hover:border-[#f97316]/20 transition-colors">
                  <item.icon className="w-6 h-6 text-[#f97316] mb-4" />
                  <h3 className="font-semibold text-lg mb-2 text-[#1e3a5f]">{item.title}</h3>
                  <p className="text-[#1e3a5f]/60 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Security Section - simplified, less prominent */}
      <section className="border-b border-[#1e3a5f]/5 bg-white">
        <div className="max-w-5xl mx-auto px-5 py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="grid md:grid-cols-4 gap-6">
              <div className="flex items-start gap-3">
                <Eye className="w-5 h-5 text-[#1e3a5f]/40 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-[#1e3a5f] mb-1">Только чтение</h3>
                  <p className="text-sm text-[#1e3a5f]/50">Не можем изменять или удалять данные</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Lock className="w-5 h-5 text-[#1e3a5f]/40 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-[#1e3a5f] mb-1">Не пишем кандидатам</h3>
                  <p className="text-sm text-[#1e3a5f]/50">Никаких действий от вашего имени</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-[#1e3a5f]/40 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-[#1e3a5f] mb-1">Данные в России</h3>
                  <p className="text-sm text-[#1e3a5f]/50">Серверы в РФ, ФЗ-152</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-[#1e3a5f]/40 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-[#1e3a5f] mb-1">Отключение в клик</h3>
                  <p className="text-sm text-[#1e3a5f]/50">Отзовите доступ в настройках HH</p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="border-b border-[#1e3a5f]/5">
        <div className="max-w-5xl mx-auto px-5 py-20 md:py-24">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.p variants={fadeIn} className="text-sm font-medium text-[#f97316] mb-3">Тарифы</motion.p>
            <motion.h2 variants={fadeIn} className="font-display text-2xl md:text-[2rem] mb-4 font-semibold text-[#1e3a5f]">
              Простые и понятные цены
            </motion.h2>
            <motion.p variants={fadeIn} className="text-[#1e3a5f]/60 mb-10 max-w-lg">
              Начните бесплатно. Без привязки карты, без автоматических списаний.
            </motion.p>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-5">
              {/* Free */}
              <div className="p-6 rounded-2xl bg-white border border-[#1e3a5f]/10">
                <p className="text-sm font-medium text-[#1e3a5f]/50 mb-2">Бесплатно</p>
                <div className="flex items-baseline gap-1 mb-4">
                  <span className="text-4xl font-display font-semibold text-[#1e3a5f]">0 ₽</span>
                </div>
                <p className="text-[#1e3a5f]/60 mb-6">Попробуйте на своих откликах</p>
                <ul className="space-y-3 mb-6">
                  {['50 резюме при регистрации', '10 загрузок резюме', 'Базовые отчёты'].map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-[#1e3a5f]/70">
                      <CheckCircle2 className="w-4 h-4 text-[#059669]" />
                      {item}
                    </li>
                  ))}
                </ul>
                <Button asChild variant="outline" className="w-full h-12 border-[#1e3a5f]/20 text-[#1e3a5f] hover:bg-[#1e3a5f]/5 font-medium rounded-xl">
                  <Link to="/register">Начать бесплатно</Link>
                </Button>
              </div>

              {/* Starter */}
              <div className="p-6 rounded-2xl bg-white border border-[#1e3a5f]/10">
                <p className="text-sm font-medium text-[#1e3a5f]/50 mb-2">Starter</p>
                <div className="flex items-baseline gap-1 mb-4">
                  <span className="text-4xl font-display font-semibold text-[#1e3a5f]">2 999 ₽</span>
                  <span className="text-[#1e3a5f]/40">/мес</span>
                </div>
                <p className="text-[#1e3a5f]/60 mb-6">Для активного найма</p>
                <ul className="space-y-3 mb-6">
                  {['200 анализов резюме', '50 загрузок резюме', 'Экспорт в Excel', 'Приоритетная поддержка'].map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-[#1e3a5f]/70">
                      <CheckCircle2 className="w-4 h-4 text-[#059669]" />
                      {item}
                    </li>
                  ))}
                </ul>
                <Button asChild className="w-full h-12 bg-[#1e3a5f] hover:bg-[#1e3a5f]/90 text-white font-medium rounded-xl">
                  <Link to="/register">Выбрать тариф</Link>
                </Button>
              </div>

              {/* Professional */}
              <div className="p-6 rounded-2xl bg-[#1e3a5f] text-white relative">
                <div className="absolute -top-3 left-6 px-3 py-1 bg-[#f97316] text-white text-xs font-semibold rounded-full shadow-lg">
                  Популярный
                </div>
                <p className="text-sm font-medium text-white/60 mb-2">Professional</p>
                <div className="flex items-baseline gap-1 mb-4">
                  <span className="text-4xl font-display font-semibold text-white">5 999 ₽</span>
                  <span className="text-white/50">/мес</span>
                </div>
                <p className="text-white/70 mb-6">Для HR-отделов</p>
                <ul className="space-y-3 mb-6">
                  {['Безлимит анализов', 'Безлимит загрузок', 'Поиск по базе резюме', 'API доступ', 'Персональный онбординг'].map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-white/90">
                      <CheckCircle2 className="w-4 h-4 text-[#f97316]" />
                      {item}
                    </li>
                  ))}
                </ul>
                <Button asChild className="w-full h-12 bg-[#f97316] hover:bg-[#ea580c] text-white font-semibold rounded-xl">
                  <Link to="/register">Выбрать тариф</Link>
                </Button>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="border-b border-[#1e3a5f]/5 bg-white">
        <div className="max-w-5xl mx-auto px-5 py-20 md:py-24">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={stagger}
          >
            <motion.p variants={fadeIn} className="text-sm font-medium text-[#f97316] mb-3">Вопросы</motion.p>
            <motion.h2 variants={fadeIn} className="font-display text-2xl md:text-[2rem] mb-10 font-semibold text-[#1e3a5f]">
              Частые вопросы
            </motion.h2>
            <motion.div variants={fadeIn} className="space-y-3 max-w-2xl">
              {[
                {
                  q: 'Система точно не пропустит хорошего кандидата?',
                  a: 'Система не отсеивает кандидатов — только сортирует по релевантности. Все резюме остаются в списке, вы видите каждого кандидата и можете изменить оценку.'
                },
                {
                  q: 'Безопасно ли подключать HeadHunter?',
                  a: 'Да. Мы используем официальный OAuth от HH и получаем доступ только к чтению откликов. Не можем публиковать вакансии, писать кандидатам или изменять данные. Вы можете отозвать доступ в любой момент.'
                },
                {
                  q: 'Как система оценивает кандидатов?',
                  a: 'Мы анализируем соответствие навыков, релевантный опыт, карьерную траекторию и потенциальные риски. Каждая оценка сопровождается объяснением — вы видите, почему кандидат получил такой балл.'
                },
                {
                  q: 'Что если я не согласен с оценкой?',
                  a: 'Вы можете изменить оценку любого кандидата вручную. Система помогает с первичной сортировкой, но финальное решение всегда за вами.'
                },
                {
                  q: 'Есть ли автоматическое продление подписки?',
                  a: 'Нет скрытых списаний. Бесплатный период не требует карты. Платный тариф оплачивается вручную, без автопродления.'
                },
              ].map((item, i) => (
                <div key={i} className="border border-[#1e3a5f]/10 rounded-xl overflow-hidden bg-[#faf8f5]">
                  <button
                    onClick={() => setOpenFaq(openFaq === i ? null : i)}
                    className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-[#1e3a5f]/[0.02] transition-colors"
                  >
                    <span className="font-medium text-[#1e3a5f] pr-4">{item.q}</span>
                    <ChevronDown className={`h-5 w-5 text-[#1e3a5f]/40 flex-shrink-0 transition-transform duration-200 ${openFaq === i ? 'rotate-180' : ''}`} />
                  </button>
                  <AnimatePresence>
                    {openFaq === i && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div className="px-6 pb-5">
                          <p className="text-[#1e3a5f]/60 leading-relaxed">{item.a}</p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-[#1e3a5f]">
        <div className="max-w-5xl mx-auto px-5 py-20 md:py-24">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
            className="text-center"
          >
            <motion.h2 variants={fadeIn} className="font-display text-3xl md:text-4xl mb-4 text-white font-semibold">
              Попробуйте на своих откликах
            </motion.h2>
            <motion.p variants={fadeIn} className="text-white/70 mb-8 max-w-md mx-auto text-lg">
              50 резюме бесплатно. Без карты. Результат через 15 минут.
            </motion.p>
            <motion.div variants={fadeIn}>
              <Button asChild size="lg" className="bg-[#f97316] hover:bg-[#ea580c] text-white h-14 px-10 text-base font-semibold rounded-xl shadow-lg shadow-[#f97316]/30 transition-all hover:shadow-xl hover:-translate-y-0.5">
                <Link to="/register">
                  Проанализировать 50 резюме бесплатно
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0f1c2e] text-white/60">
        <div className="max-w-5xl mx-auto px-5 py-12">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-9 h-9 rounded-xl bg-[#1e3a5f] flex items-center justify-center">
                  <span className="text-white font-bold text-base font-display">T</span>
                </div>
                <span className="text-xl font-display font-semibold text-white">timly</span>
              </div>
              <p className="text-white/50 max-w-xs leading-relaxed">
                Помогаем HR-специалистам быстрее находить подходящих кандидатов. Сортируем отклики, объясняем оценки.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Контакты</h4>
              <div className="space-y-3">
                <a href="mailto:hello@timly-hr.ru" className="flex items-center gap-2 text-sm text-white/50 hover:text-white transition-colors">
                  <Mail className="h-4 w-4" />hello@timly-hr.ru
                </a>
                <a href="https://t.me/timly_support" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-white/50 hover:text-white transition-colors">
                  <MessageCircle className="h-4 w-4" />Telegram поддержка
                </a>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Документы</h4>
              <div className="space-y-3">
                <Link to="/privacy" className="block text-sm text-white/50 hover:text-white transition-colors">Политика конфиденциальности</Link>
                <Link to="/terms" className="block text-sm text-white/50 hover:text-white transition-colors">Условия использования</Link>
                <Link to="/offer" className="block text-sm text-white/50 hover:text-white transition-colors">Публичная оферта</Link>
              </div>
            </div>
          </div>
          <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-white/40">
            <span>© 2024 Timly. Все права защищены.</span>
            <span>Данные хранятся на серверах в РФ</span>
          </div>
        </div>
      </footer>

      {/* Mobile Sticky CTA */}
      <AnimatePresence>
        {showStickyCta && (
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            className="fixed bottom-0 left-0 right-0 p-4 bg-[#faf8f5]/95 backdrop-blur-sm border-t border-[#1e3a5f]/10 lg:hidden z-40"
          >
            <Button asChild size="lg" className="w-full bg-[#f97316] hover:bg-[#ea580c] text-white h-12 text-base font-semibold shadow-lg rounded-xl">
              <Link to="/register">
                Проанализировать 50 резюме бесплатно
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Landing;
