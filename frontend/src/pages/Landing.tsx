/**
 * Landing - Timly HR Platform
 * Design: Dark Industrial
 * Focus: AI объяснение, mobile-first (86% трафика)
 */
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Check,
  ChevronDown,
  Download,
  FileText,
  TrendingUp,
  AlertTriangle,
  Eye,
  Sliders,
  Shield,
  Mail,
  MessageCircle,
  Quote,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const Landing: React.FC = () => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);

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
      <header className="border-b border-zinc-800/50 sticky top-0 bg-[#0a0a0a]/95 backdrop-blur-sm z-50">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <img src="/logo.jpg" alt="timly" className="h-7 w-7 rounded-lg" />
            <span className="text-base font-semibold tracking-tight">timly</span>
          </Link>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" size="sm" className="text-zinc-400 hover:text-zinc-100 text-sm h-8">
              <Link to="/login">Войти</Link>
            </Button>
            <Button asChild size="sm" className="bg-zinc-100 text-zinc-900 hover:bg-white text-sm h-8">
              <Link to="/register">Начать</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero - Pain first, identification */}
      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-20">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="max-w-2xl"
          >
            {/* Badge - identification */}
            <motion.div variants={fadeIn} className="mb-6">
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-800/80 text-xs text-zinc-300 border border-zinc-700/50">
                Для HR-менеджеров и рекрутеров
              </span>
            </motion.div>

            {/* Pain-first headline */}
            <motion.h1
              variants={fadeIn}
              className="text-3xl md:text-4xl lg:text-5xl font-semibold tracking-tight leading-[1.15] mb-5"
            >
              100 откликов на вакансию?
              <br />
              <span className="text-zinc-500">AI отсортирует за 10 минут.</span>
            </motion.h1>

            <motion.p variants={fadeIn} className="text-base md:text-lg text-zinc-400 leading-relaxed mb-6 max-w-lg">
              Загрузите отклики с HeadHunter — получите список кандидатов
              с оценками и объяснением, почему каждый подходит или нет.
            </motion.p>

            {/* CTA */}
            <motion.div variants={fadeIn} className="flex flex-col sm:flex-row gap-3 mb-8">
              <Button asChild size="lg" className="bg-zinc-100 text-zinc-900 hover:bg-white h-11 px-6 text-sm font-medium">
                <Link to="/register">
                  Попробовать бесплатно
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </motion.div>

            {/* Trust signals */}
            <motion.div variants={fadeIn} className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-zinc-500">
              <span className="flex items-center gap-1.5">
                <Check className="h-3.5 w-3.5 text-zinc-400" />
                50 анализов бесплатно
              </span>
              <span className="flex items-center gap-1.5">
                <Check className="h-3.5 w-3.5 text-zinc-400" />
                Без карты
              </span>
              <span className="flex items-center gap-1.5">
                <Check className="h-3.5 w-3.5 text-zinc-400" />
                Настройка 2 минуты
              </span>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Social proof */}
      <section className="border-b border-zinc-800/50 bg-zinc-900/30">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <p className="text-sm text-zinc-500">
              <span className="text-zinc-300 font-medium">500+ HR-специалистов</span> экономят время с Timly
            </p>
            <div className="flex items-center gap-6 text-zinc-600">
              <span className="text-xs uppercase tracking-wider">Сэкономлено:</span>
              <span className="text-zinc-300 font-semibold tabular-nums">12,000+ часов</span>
            </div>
          </div>
        </div>
      </section>

      {/* Problem statement */}
      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={stagger}
          >
            <motion.p variants={fadeIn} className="text-xs uppercase tracking-wider text-zinc-600 mb-3">
              Знакомая ситуация?
            </motion.p>
            <motion.h2 variants={fadeIn} className="text-xl md:text-2xl font-semibold mb-8 max-w-lg">
              Вы тратите 8 часов на чтение резюме, а в итоге всё равно не уверены, что никого не пропустили
            </motion.h2>

            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-4">
              {[
                { text: 'Резюме сливаются в одно после 30-го отклика', icon: FileText },
                { text: 'Хорошие кандидаты теряются среди нерелевантных', icon: AlertTriangle },
                { text: 'Нет объективных критериев — только интуиция', icon: Eye },
              ].map((item, i) => (
                <div key={i} className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
                  <item.icon className="h-5 w-5 text-zinc-600 mb-3" />
                  <p className="text-sm text-zinc-400">{item.text}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How AI works - KEY SECTION */}
      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="mb-10">
              <p className="text-xs uppercase tracking-wider text-zinc-600 mb-3">Как работает AI</p>
              <h2 className="text-xl md:text-2xl font-semibold mb-3">
                Прозрачная оценка по понятным критериям
              </h2>
              <p className="text-zinc-500 max-w-lg">
                Никакой магии. Вы всегда видите, почему AI поставил такой балл.
              </p>
            </motion.div>

            {/* Criteria grid */}
            <motion.div variants={fadeIn} className="grid md:grid-cols-2 gap-4 mb-10">
              {[
                {
                  title: 'Соответствие требованиям',
                  desc: 'AI сопоставляет навыки из вакансии с навыками в резюме. Указали "1С" — проверит, есть ли опыт.',
                  icon: Check,
                },
                {
                  title: 'Опыт и карьера',
                  desc: 'Анализирует релевантный опыт, рост по должностям, длительность на позициях.',
                  icon: TrendingUp,
                },
                {
                  title: 'Red flags',
                  desc: 'Частая смена работы, большие перерывы, несоответствие зарплатных ожиданий.',
                  icon: AlertTriangle,
                },
                {
                  title: 'Качество резюме',
                  desc: 'Конкретные достижения vs "выполнял обязанности". Структурированность.',
                  icon: FileText,
                },
              ].map((item, i) => (
                <div key={i} className="p-5 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
                  <div className="flex items-start gap-4">
                    <div className="w-9 h-9 rounded-lg bg-zinc-800 flex items-center justify-center flex-shrink-0">
                      <item.icon className="h-4 w-4 text-zinc-400" />
                    </div>
                    <div>
                      <h3 className="font-medium mb-1.5">{item.title}</h3>
                      <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </motion.div>

            {/* Example evaluation - CRITICAL */}
            <motion.div variants={fadeIn}>
              <p className="text-xs uppercase tracking-wider text-zinc-600 mb-4">Пример оценки</p>
              <Card className="border-zinc-800 bg-zinc-900/50 overflow-hidden">
                <CardContent className="p-0">
                  {/* Header */}
                  <div className="px-4 py-3 border-b border-zinc-800/50 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-sm font-medium text-zinc-400">
                        АВ
                      </div>
                      <div>
                        <p className="font-medium text-sm">Анна Волкова</p>
                        <p className="text-xs text-zinc-600">Менеджер по продажам · 5 лет опыта</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-400 tabular-nums">82</div>
                      <div className="text-[10px] text-zinc-600 uppercase tracking-wide">балла</div>
                    </div>
                  </div>

                  {/* Why this score */}
                  <div className="p-4 space-y-3">
                    <p className="text-xs uppercase tracking-wider text-zinc-600 mb-2">Почему такой балл:</p>

                    <div className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-zinc-400">
                        <span className="text-zinc-300">Опыт B2B продаж 4 года</span> — совпадает с требованием вакансии
                      </p>
                    </div>

                    <div className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-zinc-400">
                        <span className="text-zinc-300">Рост: менеджер → старший менеджер</span> — позитивная динамика
                      </p>
                    </div>

                    <div className="flex items-start gap-2">
                      <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-zinc-400">
                        <span className="text-zinc-300">Последняя работа 8 месяцев</span> — уточнить причину ухода
                      </p>
                    </div>

                    <div className="flex items-start gap-2">
                      <AlertTriangle className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-zinc-400">
                        <span className="text-zinc-300">Нет опыта с CRM Bitrix</span> — указан в требованиях вакансии
                      </p>
                    </div>
                  </div>

                  {/* Recommendation */}
                  <div className="px-4 py-3 bg-zinc-800/30 border-t border-zinc-800/50">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-zinc-400">Рекомендация AI:</span>
                      <span className="px-2.5 py-1 rounded bg-blue-500/15 text-blue-400 text-xs font-medium">
                        Пригласить на интервью
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Your control - addressing anxiety */}
      <section className="border-b border-zinc-800/50 bg-zinc-900/30">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="mb-8">
              <p className="text-xs uppercase tracking-wider text-zinc-600 mb-3">Ваш контроль</p>
              <h2 className="text-xl md:text-2xl font-semibold mb-3">
                AI помогает, но решаете вы
              </h2>
              <p className="text-zinc-500 max-w-lg">
                Мы не удаляем кандидатов и не принимаем решения за вас.
              </p>
            </motion.div>

            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-4">
              {[
                {
                  icon: Eye,
                  title: 'Видите всех',
                  desc: 'Все кандидаты остаются в списке. Даже с низким баллом — никто не удаляется автоматически.',
                },
                {
                  icon: Sliders,
                  title: 'Можете изменить',
                  desc: 'Не согласны с оценкой? Переоцените кандидата вручную. AI учтёт ваше мнение.',
                },
                {
                  icon: FileText,
                  title: 'Полное резюме',
                  desc: 'Всегда видите оригинал резюме. AI показывает выводы, но исходник рядом.',
                },
              ].map((item, i) => (
                <div key={i} className="p-5 rounded-lg bg-[#0a0a0a] border border-zinc-800/50">
                  <item.icon className="h-5 w-5 text-zinc-500 mb-3" />
                  <h3 className="font-medium mb-1.5">{item.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How to start - simplified */}
      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="mb-8">
              <p className="text-xs uppercase tracking-wider text-zinc-600 mb-3">Начать просто</p>
              <h2 className="text-xl md:text-2xl font-semibold">3 шага до первых результатов</h2>
            </motion.div>

            <motion.div variants={fadeIn} className="grid md:grid-cols-3 gap-6">
              {[
                {
                  step: '01',
                  title: 'Подключите HH.ru',
                  desc: 'Авторизуйтесь через HeadHunter. Никаких API-токенов — всё автоматически.',
                },
                {
                  step: '02',
                  title: 'Выберите вакансию',
                  desc: 'Timly загрузит ваши вакансии и отклики. Выберите, какую анализировать.',
                },
                {
                  step: '03',
                  title: 'Получите результат',
                  desc: 'Через 10-15 минут — список кандидатов с баллами и объяснениями.',
                },
              ].map((item, i) => (
                <div key={i} className="relative">
                  <div className="text-5xl font-bold text-zinc-800/50 mb-3">{item.step}</div>
                  <h3 className="font-medium mb-2">{item.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="border-b border-zinc-800/50 bg-zinc-900/30">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="mb-8">
              <p className="text-xs uppercase tracking-wider text-zinc-600 mb-3">Отзывы</p>
              <h2 className="text-xl md:text-2xl font-semibold">Что говорят HR-менеджеры</h2>
            </motion.div>

            <motion.div variants={fadeIn} className="grid md:grid-cols-2 gap-4">
              {[
                {
                  quote: 'Раньше понедельник уходил на разбор откликов. Теперь за час вижу топ-20 и планирую собеседования. Главное — я понимаю, почему AI выбрал именно этих людей.',
                  name: 'Мария К.',
                  role: 'HR-менеджер, ритейл',
                },
                {
                  quote: 'Боялась, что AI будет ошибаться. Но он не отсеивает — только сортирует. Я всё равно смотрю всех, просто начинаю с лучших. Экономлю 6 часов в неделю.',
                  name: 'Елена С.',
                  role: 'Рекрутер, IT-компания',
                },
              ].map((item, i) => (
                <Card key={i} className="border-zinc-800 bg-[#0a0a0a]">
                  <CardContent className="p-5">
                    <Quote className="h-5 w-5 text-zinc-700 mb-3" />
                    <p className="text-sm text-zinc-400 leading-relaxed mb-4">
                      "{item.quote}"
                    </p>
                    <div>
                      <p className="text-sm font-medium">{item.name}</p>
                      <p className="text-xs text-zinc-600">{item.role}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* FAQ - addressing AI anxiety */}
      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-12 md:py-16">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={stagger}
          >
            <motion.div variants={fadeIn} className="mb-8">
              <p className="text-xs uppercase tracking-wider text-zinc-600 mb-3">Вопросы</p>
              <h2 className="text-xl md:text-2xl font-semibold">Частые вопросы про AI</h2>
            </motion.div>

            <motion.div variants={fadeIn} className="space-y-2 max-w-2xl">
              {[
                {
                  q: 'AI точно не пропустит хорошего кандидата?',
                  a: 'AI не отсеивает кандидатов — он сортирует их по релевантности. Все резюме остаются в списке. Даже если AI поставил низкий балл, вы можете посмотреть кандидата и переоценить его вручную.',
                },
                {
                  q: 'Как AI понимает, что важно для моей вакансии?',
                  a: 'AI анализирует текст вашей вакансии: требования к навыкам, опыту, образованию. Потом сопоставляет с данными из резюме. Вы видите, какие требования совпали, а какие нет.',
                },
                {
                  q: 'Что если я не согласен с оценкой?',
                  a: 'Вы всегда можете изменить оценку любого кандидата. Ваше мнение важнее. AI — это помощник, не начальник.',
                },
                {
                  q: 'Мои данные в безопасности?',
                  a: 'Данные хранятся в защищённых дата-центрах в России. Мы не передаём их третьим лицам. Шифрование на всех этапах.',
                },
                {
                  q: 'Это дорого?',
                  a: '50 анализов бесплатно, без карты. Потом от 2 999 ₽/мес за 500 анализов. Экономия 6+ часов в неделю окупает подписку с первого дня.',
                },
              ].map((item, i) => (
                <div
                  key={i}
                  className="border border-zinc-800/50 rounded-lg overflow-hidden"
                >
                  <button
                    onClick={() => setOpenFaq(openFaq === i ? null : i)}
                    className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-zinc-900/50 transition-colors"
                  >
                    <span className="text-sm font-medium pr-4">{item.q}</span>
                    <ChevronDown
                      className={`h-4 w-4 text-zinc-500 flex-shrink-0 transition-transform ${
                        openFaq === i ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                  {openFaq === i && (
                    <div className="px-4 pb-4">
                      <p className="text-sm text-zinc-500 leading-relaxed">{item.a}</p>
                    </div>
                  )}
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="border-b border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-16 md:py-20">
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
              <Button asChild size="lg" className="bg-zinc-100 text-zinc-900 hover:bg-white h-11 px-8 text-sm font-medium">
                <Link to="/register">
                  Начать бесплатно
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </motion.div>

            <motion.div variants={fadeIn} className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 mt-6 text-sm text-zinc-600">
              <span>50 анализов бесплатно</span>
              <span>Без автоплатежей</span>
              <span>Отмена в любой момент</span>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800/50">
        <div className="max-w-6xl mx-auto px-4 py-10">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            {/* Brand */}
            <div className="md:col-span-2">
              <div className="flex items-center gap-2 mb-3">
                <img src="/logo.jpg" alt="timly" className="h-7 w-7 rounded-lg" />
                <span className="text-base font-semibold tracking-tight">timly</span>
              </div>
              <p className="text-sm text-zinc-600 max-w-xs leading-relaxed">
                AI-помощник для скрининга резюме. Сортирует отклики, объясняет оценки, экономит время.
              </p>
            </div>

            {/* Contacts */}
            <div>
              <h4 className="text-sm font-medium mb-3">Контакты</h4>
              <div className="space-y-2">
                <a
                  href="mailto:timly-hr@timly-hr.ru"
                  className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
                >
                  <Mail className="h-4 w-4" />
                  timly-hr@timly-hr.ru
                </a>
                <a
                  href="https://t.me/timly_support_bot"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
                >
                  <MessageCircle className="h-4 w-4" />
                  Telegram
                </a>
              </div>
            </div>

            {/* Legal */}
            <div>
              <h4 className="text-sm font-medium mb-3">Документы</h4>
              <div className="space-y-2">
                <Link to="/privacy" className="block text-sm text-zinc-500 hover:text-zinc-300 transition-colors">
                  Политика конфиденциальности
                </Link>
                <Link to="/terms" className="block text-sm text-zinc-500 hover:text-zinc-300 transition-colors">
                  Условия использования
                </Link>
                <Link to="/offer" className="block text-sm text-zinc-500 hover:text-zinc-300 transition-colors">
                  Публичная оферта
                </Link>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-zinc-800/50 flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-zinc-600">
            <span>© 2024 Timly. Все права защищены.</span>
            <div className="flex items-center gap-3">
              <Shield className="h-3.5 w-3.5" />
              <span>Данные защищены и хранятся в РФ</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
