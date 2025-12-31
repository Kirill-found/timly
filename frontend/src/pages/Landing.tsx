/**
 * Landing - Timly HR Platform - Refined Industrial
 * Clean, sophisticated, no AI-slop aesthetics
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ChevronDown, Mail, MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const Landing: React.FC = () => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [showStickyCta, setShowStickyCta] = useState(false);

  useEffect(() => {
    const handleScroll = () => setShowStickyCta(window.scrollY > 400);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const fadeIn = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } };
  const stagger = { visible: { transition: { staggerChildren: 0.08 } } };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100">
      {/* Header */}
      <header className="border-b border-zinc-800/60 sticky top-0 bg-[#09090b]/95 backdrop-blur-sm z-50">
        <div className="max-w-5xl mx-auto px-5 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <img src="/logo.jpg" alt="timly" className="h-7 w-7 rounded-md" />
            <span className="text-[15px] font-semibold tracking-tight">timly</span>
          </Link>
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="sm" className="text-zinc-400 hover:text-zinc-100 text-sm h-8">
              <Link to="/login">Войти</Link>
            </Button>
            <Button asChild size="sm" className="bg-zinc-100 text-zinc-900 hover:bg-white text-sm h-8 font-medium">
              <Link to="/register">Начать</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="border-b border-zinc-800/60">
        <div className="max-w-5xl mx-auto px-5 py-16 md:py-20">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <motion.div initial="hidden" animate="visible" variants={stagger}>
              <motion.p variants={fadeIn} className="text-[13px] text-zinc-500 mb-4 tracking-wide">
                Для HR-менеджеров и рекрутеров
              </motion.p>
              <motion.h1 variants={fadeIn} className="text-[2rem] md:text-[2.5rem] font-semibold tracking-tight leading-[1.15] mb-5">
                100 откликов на вакансию?<br />
                <span className="text-zinc-400">AI отсортирует за 10 минут.</span>
              </motion.h1>
              <motion.p variants={fadeIn} className="text-base text-zinc-500 leading-relaxed mb-8 max-w-md">
                Загрузите отклики с HeadHunter — получите список кандидатов с оценками и понятным объяснением, почему каждый подходит или нет.
              </motion.p>
              <motion.div variants={fadeIn} className="flex flex-col sm:flex-row gap-3 mb-8">
                <Button asChild size="lg" className="bg-zinc-100 text-zinc-900 hover:bg-white h-11 px-7 text-[15px] font-medium">
                  <Link to="/register">
                    Попробовать бесплатно
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </motion.div>
              <motion.div variants={fadeIn} className="flex flex-wrap items-center gap-x-6 gap-y-2 text-[13px] text-zinc-500">
                <span>50 анализов бесплатно</span>
                <span className="w-1 h-1 rounded-full bg-zinc-700" />
                <span>Без карты</span>
                <span className="w-1 h-1 rounded-full bg-zinc-700" />
                <span>Настройка 2 минуты</span>
              </motion.div>
            </motion.div>

            {/* Product Preview */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <Card className="border-zinc-800 bg-zinc-900/50">
                <CardContent className="p-0">
                  <div className="px-4 py-3 border-b border-zinc-800 flex items-center gap-2">
                    <div className="flex gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
                      <div className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
                      <div className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
                    </div>
                    <span className="text-xs text-zinc-600 ml-2">Результаты анализа</span>
                  </div>
                  <div className="p-4 space-y-2">
                    {[
                      { name: 'Анна Волкова', role: 'Менеджер по продажам', score: 92, tag: 'Нанять', accent: true },
                      { name: 'Игорь Петров', role: 'Sales manager', score: 78, tag: 'Интервью', accent: false },
                      { name: 'Мария Сидорова', role: 'Специалист по продажам', score: 54, tag: 'Возможно', accent: false },
                    ].map((item, i) => (
                      <div
                        key={i}
                        className={`p-3 rounded-lg border transition-colors ${
                          item.accent
                            ? 'bg-zinc-800/80 border-zinc-700'
                            : 'bg-zinc-900/50 border-zinc-800/50'
                        } ${i === 2 ? 'opacity-50' : ''}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-md bg-zinc-800 flex items-center justify-center text-xs font-medium text-zinc-400">
                              {item.name.split(' ').map(n => n[0]).join('')}
                            </div>
                            <div>
                              <p className="text-sm font-medium text-zinc-200">{item.name}</p>
                              <p className="text-xs text-zinc-600">{item.role}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-semibold text-zinc-200 tabular-nums">{item.score}</div>
                            <span className="text-[10px] text-zinc-500">{item.tag}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                    <p className="text-center text-xs text-zinc-600 pt-2">+47 кандидатов</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="border-b border-zinc-800/60 bg-zinc-900/30">
        <div className="max-w-5xl mx-auto px-5 py-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex -space-x-2">
                {['ЕК', 'АМ', 'ОС'].map((initials, i) => (
                  <div key={i} className="w-7 h-7 rounded-full bg-zinc-800 border-2 border-[#09090b] flex items-center justify-center text-[10px] font-medium text-zinc-500">
                    {initials}
                  </div>
                ))}
                <div className="w-7 h-7 rounded-full bg-zinc-800 border-2 border-[#09090b] flex items-center justify-center text-[10px] text-zinc-600">+</div>
              </div>
              <p className="text-sm text-zinc-500">
                <span className="text-zinc-300">500+</span> HR-специалистов
              </p>
            </div>
            <p className="text-sm text-zinc-600">
              12,000+ часов сэкономлено
            </p>
          </div>
        </div>
      </section>

      {/* Problems */}
      <section className="border-b border-zinc-800/60">
        <div className="max-w-5xl mx-auto px-5 py-16">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.p variants={fadeIn} className="text-xs uppercase tracking-widest text-zinc-600 mb-3">Знакомо?</motion.p>
            <motion.h2 variants={fadeIn} className="text-xl md:text-2xl font-semibold mb-10 max-w-lg leading-snug">
              Вы тратите 8 часов на чтение резюме, а в итоге всё равно не уверены, что никого не пропустили
            </motion.h2>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-4">
              {[
                'Резюме сливаются в одно после 30-го отклика',
                'Хорошие кандидаты теряются среди нерелевантных',
                'Нет объективных критериев — только интуиция',
              ].map((text, i) => (
                <div key={i} className="p-5 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
                  <p className="text-sm text-zinc-400 leading-relaxed">{text}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How AI works */}
      <section className="border-b border-zinc-800/60">
        <div className="max-w-5xl mx-auto px-5 py-16">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-10">
              <p className="text-xs uppercase tracking-widest text-zinc-600 mb-3">Как работает</p>
              <h2 className="text-xl md:text-2xl font-semibold mb-3">Прозрачная оценка по понятным критериям</h2>
              <p className="text-zinc-500 max-w-lg">Никакой магии. Вы всегда видите, почему AI поставил такой балл.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="grid md:grid-cols-2 gap-3 mb-14">
              {[
                { title: 'Соответствие требованиям', desc: 'AI сопоставляет навыки из вакансии с навыками в резюме' },
                { title: 'Опыт и карьера', desc: 'Анализирует релевантный опыт, рост по должностям' },
                { title: 'Red flags', desc: 'Частая смена работы, большие перерывы, несоответствие ЗП' },
                { title: 'Качество резюме', desc: 'Конкретные достижения vs "выполнял обязанности"' },
              ].map((item, i) => (
                <div key={i} className="p-5 rounded-lg bg-zinc-900/50 border border-zinc-800/50 hover:border-zinc-700/50 transition-colors">
                  <h3 className="font-medium mb-1.5 text-zinc-200">{item.title}</h3>
                  <p className="text-sm text-zinc-500">{item.desc}</p>
                </div>
              ))}
            </motion.div>

            {/* Example */}
            <motion.div variants={fadeIn}>
              <p className="text-xs uppercase tracking-widest text-zinc-600 mb-4">Пример оценки</p>
              <Card className="border-zinc-800 bg-zinc-900/50">
                <CardContent className="p-0">
                  <div className="px-5 py-4 border-b border-zinc-800">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-11 h-11 rounded-lg bg-zinc-800 flex items-center justify-center text-sm font-medium text-zinc-400">АВ</div>
                        <div>
                          <p className="font-medium text-zinc-100">Анна Волкова</p>
                          <p className="text-sm text-zinc-500">Менеджер по продажам · 5 лет</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-baseline gap-1">
                          <span className="text-3xl font-semibold text-zinc-100 tabular-nums">82</span>
                          <span className="text-sm text-zinc-600">/100</span>
                        </div>
                        <span className="text-xs text-zinc-500">Пригласить</span>
                      </div>
                    </div>
                  </div>
                  <div className="p-5">
                    <p className="text-xs uppercase tracking-widest text-zinc-600 mb-4">Почему такой балл</p>
                    <div className="space-y-2">
                      {[
                        { type: 'plus', title: 'Опыт B2B продаж 4 года', sub: 'Совпадает с требованием' },
                        { type: 'plus', title: 'Рост: менеджер → старший', sub: 'Позитивная динамика' },
                        { type: 'warn', title: 'Последняя работа 8 месяцев', sub: 'Уточнить причину ухода' },
                        { type: 'minus', title: 'Нет опыта с CRM Bitrix', sub: 'Указан в требованиях' },
                      ].map((item, i) => (
                        <div key={i} className="flex items-start gap-3 p-3 rounded-md bg-zinc-800/30">
                          <span className={`text-sm font-medium mt-0.5 ${
                            item.type === 'plus' ? 'text-zinc-400' : item.type === 'warn' ? 'text-zinc-500' : 'text-zinc-600'
                          }`}>
                            {item.type === 'plus' ? '+' : item.type === 'warn' ? '!' : '−'}
                          </span>
                          <div>
                            <p className="text-sm text-zinc-300">{item.title}</p>
                            <p className="text-xs text-zinc-600">{item.sub}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Your Control */}
      <section className="border-b border-zinc-800/60 bg-zinc-900/30">
        <div className="max-w-5xl mx-auto px-5 py-16">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-10">
              <p className="text-xs uppercase tracking-widest text-zinc-600 mb-3">Ваш контроль</p>
              <h2 className="text-xl md:text-2xl font-semibold mb-3">AI помогает, но решаете вы</h2>
              <p className="text-zinc-500 max-w-lg">Мы не удаляем кандидатов и не принимаем решения за вас.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-4">
              {[
                { title: 'Видите всех', desc: 'Все кандидаты остаются в списке. Никто не удаляется автоматически.' },
                { title: 'Можете изменить', desc: 'Не согласны с оценкой? Переоцените кандидата вручную.' },
                { title: 'Полное резюме', desc: 'Всегда видите оригинал. AI показывает выводы, но исходник рядом.' },
              ].map((item, i) => (
                <div key={i} className="p-5 rounded-lg bg-[#09090b] border border-zinc-800/50">
                  <h3 className="font-medium mb-1.5 text-zinc-200">{item.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Steps */}
      <section className="border-b border-zinc-800/60">
        <div className="max-w-5xl mx-auto px-5 py-16">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-12">
              <p className="text-xs uppercase tracking-widest text-zinc-600 mb-3">Начать просто</p>
              <h2 className="text-xl md:text-2xl font-semibold">3 шага до первых результатов</h2>
            </motion.div>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-10">
              {[
                { step: '01', title: 'Подключите HH.ru', desc: 'Авторизуйтесь через HeadHunter. Всё автоматически.' },
                { step: '02', title: 'Выберите вакансию', desc: 'Timly загрузит ваши вакансии и отклики.' },
                { step: '03', title: 'Получите результат', desc: 'Через 10-15 минут — список с баллами и объяснениями.' },
              ].map((item, i) => (
                <div key={i}>
                  <div className="text-5xl font-semibold text-zinc-800 mb-4 tabular-nums">{item.step}</div>
                  <h3 className="font-medium mb-2 text-zinc-200">{item.title}</h3>
                  <p className="text-sm text-zinc-500">{item.desc}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="border-b border-zinc-800/60 bg-zinc-900/30">
        <div className="max-w-5xl mx-auto px-5 py-16">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-10">
              <p className="text-xs uppercase tracking-widest text-zinc-600 mb-3">Отзывы</p>
              <h2 className="text-xl md:text-2xl font-semibold">Что говорят HR-менеджеры</h2>
            </motion.div>
            <motion.div variants={fadeIn} className="grid md:grid-cols-2 gap-4">
              {[
                {
                  quote: 'Раньше понедельник уходил на разбор откликов. Теперь за час вижу топ-20. Главное — понимаю, почему AI выбрал этих людей.',
                  name: 'Мария К.',
                  role: 'HR-менеджер, Retail'
                },
                {
                  quote: 'Боялась, что AI будет ошибаться. Но он не отсеивает — только сортирует. Экономлю 6 часов в неделю.',
                  name: 'Елена С.',
                  role: 'Рекрутер, IT'
                },
              ].map((item, i) => (
                <Card key={i} className="border-zinc-800 bg-[#09090b]">
                  <CardContent className="p-6">
                    <p className="text-sm text-zinc-400 leading-relaxed mb-6">"{item.quote}"</p>
                    <div className="flex items-center gap-3 pt-4 border-t border-zinc-800/50">
                      <div className="w-9 h-9 rounded-full bg-zinc-800 flex items-center justify-center text-xs font-medium text-zinc-500">
                        {item.name.split(' ')[0][0]}{item.name.split(' ')[1]?.[0] || ''}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-zinc-300">{item.name}</p>
                        <p className="text-xs text-zinc-600">{item.role}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* FAQ */}
      <section className="border-b border-zinc-800/60">
        <div className="max-w-5xl mx-auto px-5 py-16">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-10">
              <p className="text-xs uppercase tracking-widest text-zinc-600 mb-3">Вопросы</p>
              <h2 className="text-xl md:text-2xl font-semibold">Частые вопросы</h2>
            </motion.div>
            <motion.div variants={fadeIn} className="space-y-2 max-w-2xl">
              {[
                { q: 'AI точно не пропустит хорошего кандидата?', a: 'AI не отсеивает — только сортирует. Все резюме остаются в списке.' },
                { q: 'Как AI понимает, что важно для моей вакансии?', a: 'AI анализирует текст вашей вакансии и сопоставляет с резюме.' },
                { q: 'Что если я не согласен с оценкой?', a: 'Вы можете изменить оценку вручную. Ваше мнение важнее.' },
                { q: 'Мои данные в безопасности?', a: 'Данные хранятся в защищённых дата-центрах в России.' },
                { q: 'Это дорого?', a: '50 анализов бесплатно. Потом от 2 999 ₽/мес за 500 анализов.' },
              ].map((item, i) => (
                <div key={i} className="border border-zinc-800/50 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setOpenFaq(openFaq === i ? null : i)}
                    className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-zinc-900/30 transition-colors"
                  >
                    <span className="text-sm font-medium pr-4 text-zinc-300">{item.q}</span>
                    <ChevronDown className={`h-4 w-4 text-zinc-600 flex-shrink-0 transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                  </button>
                  <AnimatePresence>
                    {openFaq === i && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div className="px-5 pb-4">
                          <p className="text-sm text-zinc-500">{item.a}</p>
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
      <section className="border-b border-zinc-800/60">
        <div className="max-w-5xl mx-auto px-5 py-20">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={stagger}
            className="text-center"
          >
            <motion.h2 variants={fadeIn} className="text-2xl md:text-3xl font-semibold mb-4">
              Попробуйте на своих откликах
            </motion.h2>
            <motion.p variants={fadeIn} className="text-zinc-500 mb-8 max-w-md mx-auto">
              50 анализов бесплатно. Без карты. Результат через 10 минут.
            </motion.p>
            <motion.div variants={fadeIn}>
              <Button asChild size="lg" className="bg-zinc-100 text-zinc-900 hover:bg-white h-11 px-8 text-[15px] font-medium">
                <Link to="/register">
                  Начать бесплатно
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </motion.div>
            <motion.div variants={fadeIn} className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mt-8 text-[13px] text-zinc-600">
              <span>50 анализов бесплатно</span>
              <span className="w-1 h-1 rounded-full bg-zinc-700" />
              <span>Без автоплатежей</span>
              <span className="w-1 h-1 rounded-full bg-zinc-700" />
              <span>Отмена в любой момент</span>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800/60">
        <div className="max-w-5xl mx-auto px-5 py-10">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <div className="flex items-center gap-2.5 mb-3">
                <img src="/logo.jpg" alt="timly" className="h-7 w-7 rounded-md" />
                <span className="text-[15px] font-semibold tracking-tight">timly</span>
              </div>
              <p className="text-sm text-zinc-600 max-w-xs leading-relaxed">
                AI-помощник для скрининга резюме. Сортирует отклики, объясняет оценки, экономит время.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-medium mb-3 text-zinc-400">Контакты</h4>
              <div className="space-y-2">
                <a href="mailto:timly-hr@timly-hr.ru" className="flex items-center gap-2 text-sm text-zinc-600 hover:text-zinc-400 transition-colors">
                  <Mail className="h-4 w-4" />timly-hr@timly-hr.ru
                </a>
                <a href="https://t.me/timly_support_bot" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-zinc-600 hover:text-zinc-400 transition-colors">
                  <MessageCircle className="h-4 w-4" />Telegram
                </a>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium mb-3 text-zinc-400">Документы</h4>
              <div className="space-y-2">
                <Link to="/privacy" className="block text-sm text-zinc-600 hover:text-zinc-400 transition-colors">Политика конфиденциальности</Link>
                <Link to="/terms" className="block text-sm text-zinc-600 hover:text-zinc-400 transition-colors">Условия использования</Link>
                <Link to="/offer" className="block text-sm text-zinc-600 hover:text-zinc-400 transition-colors">Публичная оферта</Link>
              </div>
            </div>
          </div>
          <div className="pt-6 border-t border-zinc-800/50 flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-zinc-600">
            <span>© 2024 Timly</span>
            <span>Данные хранятся в РФ</span>
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
            className="fixed bottom-0 left-0 right-0 p-4 bg-[#09090b]/95 backdrop-blur-sm border-t border-zinc-800/60 lg:hidden z-40"
          >
            <Button asChild size="lg" className="w-full bg-zinc-100 text-zinc-900 hover:bg-white h-11 text-[15px] font-medium">
              <Link to="/register">
                Попробовать бесплатно
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Landing;
