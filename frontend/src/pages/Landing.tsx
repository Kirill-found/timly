/**
 * Landing - Timly HR Platform - Warm Industrial
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Check, ChevronDown, FileText, TrendingUp, AlertTriangle, Eye, Sliders, Shield, Mail, MessageCircle, Quote, Star, Clock, Users, Zap, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const Landing: React.FC = () => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [showStickyCtaMobile, setShowStickyCtaMobile] = useState(false);

  useEffect(() => {
    const handleScroll = () => setShowStickyCtaMobile(window.scrollY > 400);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const fadeIn = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } };
  const stagger = { visible: { transition: { staggerChildren: 0.1 } } };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-100">
      <header className="border-b border-zinc-800/50 sticky top-0 bg-[#0a0a0a]/95 backdrop-blur-sm z-50">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <img src="/logo.jpg" alt="timly" className="h-7 w-7 rounded-lg" />
            <span className="text-base font-semibold tracking-tight">timly</span>
          </Link>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" size="sm" className="text-zinc-400 hover:text-zinc-100 text-sm h-8"><Link to="/login">Войти</Link></Button>
            <Button asChild size="sm" className="bg-emerald-500 text-white hover:bg-emerald-400 text-sm h-8 font-medium shadow-lg shadow-emerald-500/20"><Link to="/register">Начать</Link></Button>
          </div>
        </div>
      </header>

      <section className="border-b border-zinc-800/50 overflow-hidden">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-16">
          <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
            <motion.div initial="hidden" animate="visible" variants={stagger}>
              <motion.div variants={fadeIn} className="mb-5">
                <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 text-sm text-emerald-400 border border-emerald-500/20 font-medium">
                  <Users className="h-3.5 w-3.5" />Для HR-менеджеров и рекрутеров
                </span>
              </motion.div>
              <motion.h1 variants={fadeIn} className="text-3xl md:text-4xl lg:text-[2.75rem] font-semibold tracking-tight leading-[1.15] mb-5">
                100 откликов на вакансию?<br /><span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">AI отсортирует за 10 минут.</span>
              </motion.h1>
              <motion.p variants={fadeIn} className="text-base md:text-lg text-zinc-400 leading-relaxed mb-6 max-w-lg">
                Загрузите отклики с HeadHunter — получите список кандидатов с оценками и <span className="text-zinc-200">понятным объяснением</span>, почему каждый подходит или нет.
              </motion.p>
              <motion.div variants={fadeIn} className="flex flex-col sm:flex-row gap-3 mb-6">
                <Button asChild size="lg" className="bg-emerald-500 text-white hover:bg-emerald-400 h-12 px-8 text-base font-medium shadow-xl shadow-emerald-500/25 transition-all hover:shadow-emerald-500/40 hover:scale-[1.02]">
                  <Link to="/register">Попробовать бесплатно<ArrowRight className="ml-2 h-4 w-4" /></Link>
                </Button>
              </motion.div>
              <motion.div variants={fadeIn} className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
                <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-emerald-500" /><span className="text-zinc-300">50 анализов бесплатно</span></span>
                <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-emerald-500" /><span className="text-zinc-300">Без карты</span></span>
                <span className="flex items-center gap-1.5"><Clock className="h-4 w-4 text-emerald-500" /><span className="text-zinc-300">Настройка 2 минуты</span></span>
              </motion.div>
            </motion.div>

            <motion.div initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3, duration: 0.6 }} className="relative">
              <div className="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 via-teal-500/10 to-blue-500/20 rounded-2xl blur-2xl opacity-50" />
              <Card className="relative border-zinc-700/50 bg-zinc-900/90 shadow-2xl overflow-hidden">
                <CardContent className="p-0">
                  <div className="px-4 py-3 border-b border-zinc-800 flex items-center gap-2">
                    <div className="flex gap-1.5"><div className="w-3 h-3 rounded-full bg-zinc-700" /><div className="w-3 h-3 rounded-full bg-zinc-700" /><div className="w-3 h-3 rounded-full bg-zinc-700" /></div>
                    <span className="text-xs text-zinc-500 ml-2">timly — Результаты анализа</span>
                  </div>
                  <div className="p-4 space-y-3">
                    <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-sm font-bold text-white">АВ</div>
                          <div><p className="font-medium text-sm text-zinc-100">Анна Волкова</p><p className="text-xs text-zinc-500">Менеджер по продажам</p></div>
                        </div>
                        <div className="text-right"><div className="text-xl font-bold text-emerald-400">92</div><span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-medium">Нанять</span></div>
                      </div>
                    </div>
                    <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-sm font-bold text-white">ИП</div>
                          <div><p className="font-medium text-sm text-zinc-100">Игорь Петров</p><p className="text-xs text-zinc-500">Sales manager</p></div>
                        </div>
                        <div className="text-right"><div className="text-xl font-bold text-blue-400">78</div><span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-medium">Интервью</span></div>
                      </div>
                    </div>
                    <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50 opacity-60">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-sm font-bold text-white">МС</div>
                          <div><p className="font-medium text-sm text-zinc-100">Мария Сидорова</p><p className="text-xs text-zinc-500">Специалист по продажам</p></div>
                        </div>
                        <div className="text-right"><div className="text-xl font-bold text-amber-400">54</div><span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-medium">Возможно</span></div>
                      </div>
                    </div>
                    <div className="text-center text-xs text-zinc-600 pt-1">+47 кандидатов отсортировано...</div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="border-b border-zinc-800/50 bg-gradient-to-r from-zinc-900/50 via-emerald-950/20 to-zinc-900/50">
        <div className="max-w-6xl mx-auto px-4 py-5">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex -space-x-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-400 to-rose-500 border-2 border-[#0a0a0a] flex items-center justify-center text-[10px] font-bold text-white">ЕК</div>
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 border-2 border-[#0a0a0a] flex items-center justify-center text-[10px] font-bold text-white">АМ</div>
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 border-2 border-[#0a0a0a] flex items-center justify-center text-[10px] font-bold text-white">ОС</div>
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 border-2 border-[#0a0a0a] flex items-center justify-center text-[10px] font-bold text-white">+</div>
              </div>
              <p className="text-sm text-zinc-400"><span className="text-zinc-100 font-semibold">500+ HR-специалистов</span> экономят время с Timly</p>
            </div>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2"><Zap className="h-4 w-4 text-amber-400" /><span className="text-sm"><span className="text-zinc-100 font-semibold tabular-nums">12,000+</span> <span className="text-zinc-500">часов сэкономлено</span></span></div>
              <div className="flex items-center gap-1">{[...Array(5)].map((_, i) => <Star key={i} className="h-4 w-4 fill-amber-400 text-amber-400" />)}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-14 md:py-18">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.p variants={fadeIn} className="text-xs uppercase tracking-wider text-emerald-500 font-medium mb-3">Знакомая ситуация?</motion.p>
            <motion.h2 variants={fadeIn} className="text-xl md:text-2xl font-semibold mb-8 max-w-xl">Вы тратите <span className="text-red-400">8 часов</span> на чтение резюме, а в итоге всё равно не уверены, что никого не пропустили</motion.h2>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-4">
              {[
                { text: 'Резюме сливаются в одно после 30-го отклика', icon: FileText, color: 'red' },
                { text: 'Хорошие кандидаты теряются среди нерелевантных', icon: AlertTriangle, color: 'amber' },
                { text: 'Нет объективных критериев — только интуиция', icon: Eye, color: 'blue' },
              ].map((item, i) => (
                <div key={i} className="p-5 rounded-xl bg-zinc-900/50 border border-zinc-800/50 hover:border-zinc-700/50 transition-colors">
                  <div className={`w-10 h-10 rounded-lg mb-4 flex items-center justify-center ${item.color === 'red' ? 'bg-red-500/10' : item.color === 'amber' ? 'bg-amber-500/10' : 'bg-blue-500/10'}`}>
                    <item.icon className={`h-5 w-5 ${item.color === 'red' ? 'text-red-400' : item.color === 'amber' ? 'text-amber-400' : 'text-blue-400'}`} />
                  </div>
                  <p className="text-sm text-zinc-300 leading-relaxed">{item.text}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-14 md:py-18">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-10">
              <p className="text-xs uppercase tracking-wider text-emerald-500 font-medium mb-3">Как работает AI</p>
              <h2 className="text-xl md:text-2xl font-semibold mb-3">Прозрачная оценка по понятным критериям</h2>
              <p className="text-zinc-400 max-w-lg">Никакой магии. Вы всегда видите, <span className="text-zinc-200">почему</span> AI поставил такой балл.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="grid md:grid-cols-2 gap-4 mb-12">
              {[
                { title: 'Соответствие требованиям', desc: 'AI сопоставляет навыки из вакансии с навыками в резюме.', icon: Check, color: 'emerald' },
                { title: 'Опыт и карьера', desc: 'Анализирует релевантный опыт, рост по должностям.', icon: TrendingUp, color: 'blue' },
                { title: 'Red flags', desc: 'Частая смена работы, большие перерывы, несоответствие ЗП.', icon: AlertTriangle, color: 'amber' },
                { title: 'Качество резюме', desc: 'Конкретные достижения vs "выполнял обязанности".', icon: FileText, color: 'violet' },
              ].map((item, i) => (
                <div key={i} className="p-5 rounded-xl bg-zinc-900/50 border border-zinc-800/50 hover:border-zinc-700 transition-all group">
                  <div className="flex items-start gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${item.color === 'emerald' ? 'bg-emerald-500/10' : item.color === 'blue' ? 'bg-blue-500/10' : item.color === 'amber' ? 'bg-amber-500/10' : 'bg-violet-500/10'}`}>
                      <item.icon className={`h-5 w-5 ${item.color === 'emerald' ? 'text-emerald-400' : item.color === 'blue' ? 'text-blue-400' : item.color === 'amber' ? 'text-amber-400' : 'text-violet-400'}`} />
                    </div>
                    <div><h3 className="font-medium mb-1.5 text-zinc-100">{item.title}</h3><p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p></div>
                  </div>
                </div>
              ))}
            </motion.div>

            <motion.div variants={fadeIn}>
              <p className="text-xs uppercase tracking-wider text-zinc-500 mb-4">Пример оценки кандидата</p>
              <Card className="border-zinc-700/50 bg-zinc-900/80 overflow-hidden shadow-xl">
                <CardContent className="p-0">
                  <div className="px-5 py-4 border-b border-zinc-800 bg-gradient-to-r from-emerald-950/30 to-transparent">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-lg font-bold text-white shadow-lg shadow-emerald-500/20">АВ</div>
                        <div><p className="font-semibold text-zinc-100">Анна Волкова</p><p className="text-sm text-zinc-500">Менеджер по продажам · 5 лет опыта</p></div>
                      </div>
                      <div className="text-right">
                        <div className="flex items-baseline gap-1"><span className="text-4xl font-bold text-emerald-400 tabular-nums">82</span><span className="text-sm text-zinc-600">/100</span></div>
                        <span className="inline-block mt-1 px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-400 text-xs font-semibold">Пригласить на интервью</span>
                      </div>
                    </div>
                  </div>
                  <div className="p-5">
                    <p className="text-xs uppercase tracking-wider text-zinc-600 mb-4 font-medium">Почему такой балл:</p>
                    <div className="space-y-3">
                      <div className="flex items-start gap-3 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                        <CheckCircle className="h-5 w-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                        <div><p className="text-sm text-zinc-200 font-medium">Опыт B2B продаж 4 года</p><p className="text-xs text-zinc-500 mt-0.5">Совпадает с требованием вакансии</p></div>
                      </div>
                      <div className="flex items-start gap-3 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                        <CheckCircle className="h-5 w-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                        <div><p className="text-sm text-zinc-200 font-medium">Рост: менеджер → старший менеджер</p><p className="text-xs text-zinc-500 mt-0.5">Позитивная карьерная динамика</p></div>
                      </div>
                      <div className="flex items-start gap-3 p-3 rounded-lg bg-amber-500/5 border border-amber-500/10">
                        <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5 flex-shrink-0" />
                        <div><p className="text-sm text-zinc-200 font-medium">Последняя работа 8 месяцев</p><p className="text-xs text-zinc-500 mt-0.5">Рекомендуем уточнить причину ухода</p></div>
                      </div>
                      <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                        <XCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
                        <div><p className="text-sm text-zinc-200 font-medium">Нет опыта с CRM Bitrix</p><p className="text-xs text-zinc-500 mt-0.5">Указан в требованиях вакансии</p></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="border-b border-zinc-800/50 bg-zinc-900/30">
        <div className="max-w-6xl mx-auto px-4 py-14 md:py-18">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-8">
              <p className="text-xs uppercase tracking-wider text-blue-400 font-medium mb-3">Ваш контроль</p>
              <h2 className="text-xl md:text-2xl font-semibold mb-3">AI помогает, но <span className="text-blue-400">решаете вы</span></h2>
              <p className="text-zinc-400 max-w-lg">Мы не удаляем кандидатов и не принимаем решения за вас.</p>
            </motion.div>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-4">
              {[
                { icon: Eye, title: 'Видите всех', desc: 'Все кандидаты остаются в списке. Никто не удаляется автоматически.' },
                { icon: Sliders, title: 'Можете изменить', desc: 'Не согласны с оценкой? Переоцените кандидата вручную.' },
                { icon: FileText, title: 'Полное резюме', desc: 'Всегда видите оригинал резюме. AI показывает выводы, но исходник рядом.' },
              ].map((item, i) => (
                <div key={i} className="p-5 rounded-xl bg-[#0a0a0a] border border-zinc-800/50 hover:border-blue-500/30 transition-colors group">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4 group-hover:bg-blue-500/15 transition-colors">
                    <item.icon className="h-5 w-5 text-blue-400" />
                  </div>
                  <h3 className="font-medium mb-1.5 text-zinc-100">{item.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-14 md:py-18">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-10">
              <p className="text-xs uppercase tracking-wider text-emerald-500 font-medium mb-3">Начать просто</p>
              <h2 className="text-xl md:text-2xl font-semibold">3 шага до первых результатов</h2>
            </motion.div>
            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-8">
              {[
                { step: '01', title: 'Подключите HH.ru', desc: 'Авторизуйтесь через HeadHunter. Всё автоматически.', color: 'emerald' },
                { step: '02', title: 'Выберите вакансию', desc: 'Timly загрузит ваши вакансии и отклики.', color: 'blue' },
                { step: '03', title: 'Получите результат', desc: 'Через 10-15 минут — список с баллами и объяснениями.', color: 'violet' },
              ].map((item, i) => (
                <div key={i} className="relative group">
                  <div className={`text-6xl font-bold mb-4 transition-colors ${item.color === 'emerald' ? 'text-emerald-500/20 group-hover:text-emerald-500/30' : item.color === 'blue' ? 'text-blue-500/20 group-hover:text-blue-500/30' : 'text-violet-500/20 group-hover:text-violet-500/30'}`}>{item.step}</div>
                  <h3 className="font-semibold mb-2 text-zinc-100">{item.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="border-b border-zinc-800/50 bg-zinc-900/30">
        <div className="max-w-6xl mx-auto px-4 py-14 md:py-18">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-8">
              <p className="text-xs uppercase tracking-wider text-amber-400 font-medium mb-3">Отзывы</p>
              <h2 className="text-xl md:text-2xl font-semibold">Что говорят HR-менеджеры</h2>
            </motion.div>
            <motion.div variants={fadeIn} className="grid md:grid-cols-2 gap-5">
              {[
                { quote: 'Раньше понедельник уходил на разбор откликов. Теперь за час вижу топ-20. Главное — понимаю, почему AI выбрал этих людей.', name: 'Мария Ковалёва', role: 'HR-менеджер', company: 'Retail Group', avatar: 'МК', color: 'rose' },
                { quote: 'Боялась, что AI будет ошибаться. Но он не отсеивает — только сортирует. Экономлю 6 часов в неделю.', name: 'Елена Смирнова', role: 'Рекрутер', company: 'TechStart', avatar: 'ЕС', color: 'blue' },
              ].map((item, i) => (
                <Card key={i} className="border-zinc-800 bg-[#0a0a0a] hover:border-zinc-700 transition-colors">
                  <CardContent className="p-6">
                    <div className="flex gap-1 mb-4">{[...Array(5)].map((_, j) => <Star key={j} className="h-4 w-4 fill-amber-400 text-amber-400" />)}</div>
                    <Quote className="h-6 w-6 text-zinc-800 mb-3" />
                    <p className="text-sm text-zinc-300 leading-relaxed mb-5">"{item.quote}"</p>
                    <div className="flex items-center gap-3 pt-4 border-t border-zinc-800">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white ${item.color === 'rose' ? 'bg-gradient-to-br from-rose-400 to-pink-500' : 'bg-gradient-to-br from-blue-400 to-indigo-500'}`}>{item.avatar}</div>
                      <div><p className="text-sm font-medium text-zinc-100">{item.name}</p><p className="text-xs text-zinc-500">{item.role} · {item.company}</p></div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-14 md:py-18">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-50px" }} variants={stagger}>
            <motion.div variants={fadeIn} className="mb-8">
              <p className="text-xs uppercase tracking-wider text-zinc-500 font-medium mb-3">Вопросы</p>
              <h2 className="text-xl md:text-2xl font-semibold">Частые вопросы про AI</h2>
            </motion.div>
            <motion.div variants={fadeIn} className="space-y-2 max-w-2xl">
              {[
                { q: 'AI точно не пропустит хорошего кандидата?', a: 'AI не отсеивает — только сортирует. Все резюме остаются в списке.' },
                { q: 'Как AI понимает, что важно для моей вакансии?', a: 'AI анализирует текст вашей вакансии и сопоставляет с резюме.' },
                { q: 'Что если я не согласен с оценкой?', a: 'Вы можете изменить оценку. Ваше мнение важнее.' },
                { q: 'Мои данные в безопасности?', a: 'Данные хранятся в защищённых дата-центрах в России.' },
                { q: 'Это дорого?', a: '50 анализов бесплатно. Потом от 2 999 ₽/мес за 500 анализов.' },
              ].map((item, i) => (
                <div key={i} className="border border-zinc-800/50 rounded-xl overflow-hidden hover:border-zinc-700 transition-colors">
                  <button onClick={() => setOpenFaq(openFaq === i ? null : i)} className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-zinc-900/50 transition-colors">
                    <span className="text-sm font-medium pr-4 text-zinc-200">{item.q}</span>
                    <ChevronDown className={`h-4 w-4 text-zinc-500 flex-shrink-0 transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                  </button>
                  <AnimatePresence>
                    {openFaq === i && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }}>
                        <div className="px-5 pb-4"><p className="text-sm text-zinc-500 leading-relaxed">{item.a}</p></div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="border-b border-zinc-800/50 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-emerald-950/20 via-transparent to-transparent" />
        <div className="max-w-6xl mx-auto px-4 py-16 md:py-24 relative">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger} className="text-center">
            <motion.h2 variants={fadeIn} className="text-2xl md:text-3xl font-semibold mb-4">Попробуйте на <span className="text-emerald-400">своих откликах</span></motion.h2>
            <motion.p variants={fadeIn} className="text-zinc-400 mb-8 max-w-md mx-auto">50 анализов бесплатно. Без карты. Результат через 10 минут.</motion.p>
            <motion.div variants={fadeIn}>
              <Button asChild size="lg" className="bg-emerald-500 text-white hover:bg-emerald-400 h-12 px-10 text-base font-medium shadow-xl shadow-emerald-500/25 transition-all hover:shadow-emerald-500/40 hover:scale-[1.02]">
                <Link to="/register">Начать бесплатно<ArrowRight className="ml-2 h-4 w-4" /></Link>
              </Button>
            </motion.div>
            <motion.div variants={fadeIn} className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mt-8 text-sm text-zinc-500">
              <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-emerald-500/60" />50 анализов бесплатно</span>
              <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-emerald-500/60" />Без автоплатежей</span>
              <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-emerald-500/60" />Отмена в любой момент</span>
            </motion.div>
          </motion.div>
        </div>
      </section>

      <footer className="border-t border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-10">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <div className="flex items-center gap-2 mb-3"><img src="/logo.jpg" alt="timly" className="h-7 w-7 rounded-lg" /><span className="text-base font-semibold tracking-tight">timly</span></div>
              <p className="text-sm text-zinc-500 max-w-xs leading-relaxed">AI-помощник для скрининга резюме. Сортирует отклики, объясняет оценки, экономит время.</p>
            </div>
            <div>
              <h4 className="text-sm font-medium mb-3 text-zinc-300">Контакты</h4>
              <div className="space-y-2">
                <a href="mailto:timly-hr@timly-hr.ru" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-emerald-400 transition-colors"><Mail className="h-4 w-4" />timly-hr@timly-hr.ru</a>
                <a href="https://t.me/timly_support_bot" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-emerald-400 transition-colors"><MessageCircle className="h-4 w-4" />Telegram</a>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium mb-3 text-zinc-300">Документы</h4>
              <div className="space-y-2">
                <Link to="/privacy" className="block text-sm text-zinc-500 hover:text-zinc-300 transition-colors">Политика конфиденциальности</Link>
                <Link to="/terms" className="block text-sm text-zinc-500 hover:text-zinc-300 transition-colors">Условия использования</Link>
                <Link to="/offer" className="block text-sm text-zinc-500 hover:text-zinc-300 transition-colors">Публичная оферта</Link>
              </div>
            </div>
          </div>
          <div className="pt-6 border-t border-zinc-800/50 flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-zinc-600">
            <span>© 2024 Timly. Все права защищены.</span>
            <div className="flex items-center gap-2"><Shield className="h-3.5 w-3.5 text-emerald-500/50" /><span>Данные защищены и хранятся в РФ</span></div>
          </div>
        </div>
      </footer>

      <AnimatePresence>
        {showStickyCtaMobile && (
          <motion.div initial={{ y: 100, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 100, opacity: 0 }} className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a] to-transparent lg:hidden z-40">
            <Button asChild size="lg" className="w-full bg-emerald-500 text-white hover:bg-emerald-400 h-12 text-base font-medium shadow-xl shadow-emerald-500/25">
              <Link to="/register">Попробовать бесплатно<ArrowRight className="ml-2 h-4 w-4" /></Link>
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Landing;
