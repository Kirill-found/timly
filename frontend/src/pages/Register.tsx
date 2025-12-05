/**
 * Страница регистрации Timly
 * Современный дизайн с анимациями и дополнительной информацией
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Mail,
  Lock,
  User,
  Eye,
  EyeOff,
  AlertCircle,
  Building,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Gift,
  Zap,
} from 'lucide-react';
import { useAuth } from '@/store/AuthContext';

const formSchema = z.object({
  company_name: z
    .string()
    .min(2, { message: 'Название должно содержать минимум 2 символа' })
    .max(100, { message: 'Название слишком длинное' }),
  full_name: z
    .string()
    .min(2, { message: 'Имя должно содержать минимум 2 символа' })
    .max(50, { message: 'Имя слишком длинное' }),
  email: z
    .string()
    .min(1, { message: 'Введите ваш email' })
    .email({ message: 'Некорректный email адрес' }),
  password: z
    .string()
    .min(8, { message: 'Пароль должен содержать минимум 8 символов' })
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
      message: 'Пароль должен содержать строчные, заглавные буквы и цифры'
    }),
})

type RegisterFormValues = z.infer<typeof formSchema>

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { register, error, clearError } = useAuth();

  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      company_name: '',
      full_name: '',
      email: '',
      password: '',
    },
  })

  const onSubmit = async (values: RegisterFormValues) => {
    try {
      setLoading(true);
      clearError();

      await register(values);

      // Перенаправление на dashboard после успешной регистрации
      navigate('/dashboard', { replace: true });
    } catch (error) {
      // Ошибка уже обработана в AuthContext
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4 py-12">
      {/* Анимированный градиентный фон */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-600 via-pink-600 to-orange-600" />

      {/* Декоративные плавающие элементы */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3],
            x: [0, -50, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 11,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute top-10 left-10 w-96 h-96 bg-white/10 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.4, 0.2],
            x: [0, 50, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 13,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 1.5,
          }}
          className="absolute bottom-10 right-10 w-96 h-96 bg-orange-400/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.15, 1],
            opacity: [0.2, 0.35, 0.2],
          }}
          transition={{
            duration: 9,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 2,
          }}
          className="absolute top-1/3 left-1/3 w-96 h-96 bg-pink-400/15 rounded-full blur-3xl"
        />
      </div>

      {/* Основной контент */}
      <div className="relative w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-8 items-center">
        {/* Левая часть - информация */}
        <motion.div
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0, x: -50 },
            visible: { opacity: 1, x: 0 },
          }}
          transition={{ duration: 0.6 }}
          className="hidden lg:block text-white space-y-8 px-8"
        >
          <div className="space-y-4">
            <Badge className="bg-white/20 text-white border-white/30 backdrop-blur-sm">
              <Gift className="w-4 h-4 mr-2" />
              50 анализов бесплатно
            </Badge>

            <h1 className="text-5xl font-bold leading-tight">
              Начните автоматизировать <br />
              <span className="bg-gradient-to-r from-white to-orange-100 bg-clip-text text-transparent">
                рекрутинг сегодня
              </span>
            </h1>

            <p className="text-xl text-white/90 leading-relaxed">
              Присоединяйтесь к 500+ компаниям, которые уже используют Timly для умного отбора кандидатов
            </p>
          </div>

          <div className="space-y-4">
            {[
              {
                icon: Gift,
                title: '50 бесплатных анализов',
                description: 'Начните без оплаты и кредитной карты',
              },
              {
                icon: Zap,
                title: 'Готов за 2 минуты',
                description: 'Простая настройка интеграции с HH.ru',
              },
              {
                icon: Sparkles,
                title: 'AI-анализ в один клик',
                description: 'Автоматическая оценка всех кандидатов',
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="flex items-start gap-4 bg-white/10 backdrop-blur-sm rounded-2xl p-4"
              >
                <div className="h-12 w-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{feature.title}</h3>
                  <p className="text-white/80 text-sm">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 space-y-3">
            <h3 className="font-semibold text-lg">Что включено:</h3>
            <div className="space-y-2">
              {[
                '50 анализов резюме при регистрации',
                'Полный AI-анализ по 15+ критериям',
                'Экспорт результатов в Excel',
                'Интеграция с HeadHunter',
                'Техническая поддержка',
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-green-300 flex-shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Правая часть - форма регистрации */}
        <motion.div
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0 },
          }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Card className="shadow-2xl border-0 bg-white/95 backdrop-blur-xl">
            <CardHeader className="text-center space-y-6 pb-8">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="flex justify-center"
              >
                <div className="relative">
                  <motion.div
                    animate={{
                      boxShadow: [
                        '0 0 20px rgba(147, 51, 234, 0.3)',
                        '0 0 40px rgba(236, 72, 153, 0.4)',
                        '0 0 20px rgba(147, 51, 234, 0.3)',
                      ],
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                    className="h-24 w-24 rounded-3xl overflow-hidden"
                  >
                    <img
                      src="/logo.jpg"
                      alt="Timly Logo"
                      className="h-full w-full object-cover"
                    />
                  </motion.div>
                  <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl opacity-20 blur-xl" />
                </div>
              </motion.div>

              <div className="space-y-2">
                <CardTitle className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Создать аккаунт
                </CardTitle>
                <CardDescription className="text-base text-gray-600">
                  Заполните форму и начните использовать Timly бесплатно
                </CardDescription>
              </div>

              <Badge className="bg-gradient-to-r from-purple-600 to-pink-600 text-white border-0">
                <Gift className="w-4 h-4 mr-2" />
                Первые 50 анализов в подарок
              </Badge>
            </CardHeader>

            <CardContent className="space-y-6">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Alert variant="destructive" className="border-red-200">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                </motion.div>
              )}

              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="company_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-base font-semibold">
                          Название компании
                        </FormLabel>
                        <FormControl>
                          <div className="relative group">
                            <Building className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 group-focus-within:text-purple-600 transition-colors" />
                            <Input
                              placeholder="ООО Рога и копыта"
                              className="pl-12 h-12 text-base border-2 border-gray-200 focus:border-purple-600 transition-all"
                              autoComplete="organization"
                              {...field}
                            />
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="full_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-base font-semibold">
                          Полное имя
                        </FormLabel>
                        <FormControl>
                          <div className="relative group">
                            <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 group-focus-within:text-purple-600 transition-colors" />
                            <Input
                              placeholder="Иван Иванов"
                              className="pl-12 h-12 text-base border-2 border-gray-200 focus:border-purple-600 transition-all"
                              autoComplete="name"
                              {...field}
                            />
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-base font-semibold">
                          Рабочий Email
                        </FormLabel>
                        <FormControl>
                          <div className="relative group">
                            <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 group-focus-within:text-purple-600 transition-colors" />
                            <Input
                              placeholder="hr@company.com"
                              className="pl-12 h-12 text-base border-2 border-gray-200 focus:border-purple-600 transition-all"
                              autoComplete="email"
                              {...field}
                            />
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-base font-semibold">Пароль</FormLabel>
                        <FormControl>
                          <div className="relative group">
                            <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 group-focus-within:text-purple-600 transition-colors" />
                            <Input
                              type={showPassword ? 'text' : 'password'}
                              placeholder="Создайте надежный пароль"
                              className="pl-12 pr-12 h-12 text-base border-2 border-gray-200 focus:border-purple-600 transition-all"
                              autoComplete="new-password"
                              {...field}
                            />
                            <button
                              type="button"
                              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                              onClick={() => setShowPassword(!showPassword)}
                            >
                              {showPassword ? (
                                <EyeOff className="h-5 w-5" />
                              ) : (
                                <Eye className="h-5 w-5" />
                              )}
                            </button>
                          </div>
                        </FormControl>
                        <FormMessage />
                        <p className="text-xs text-gray-500 mt-1">
                          Минимум 8 символов: строчные, заглавные буквы и цифры
                        </p>
                      </FormItem>
                    )}
                  />

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-12 text-base bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all"
                  >
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        >
                          <Sparkles className="h-5 w-5" />
                        </motion.div>
                        Создаем аккаунт...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        Создать бесплатный аккаунт
                        <ArrowRight className="h-5 w-5" />
                      </span>
                    )}
                  </Button>
                </form>
              </Form>

              <div className="space-y-4">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-200" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-white text-gray-500">или</span>
                  </div>
                </div>

                <div className="text-center space-y-3">
                  <p className="text-gray-600">
                    Уже есть аккаунт?{' '}
                    <Link
                      to="/login"
                      className="text-purple-600 hover:text-purple-800 font-semibold hover:underline transition-colors"
                    >
                      Войти
                    </Link>
                  </p>

                  <Link
                    to="/"
                    className="text-gray-500 hover:text-gray-700 text-sm hover:underline block transition-colors"
                  >
                    ← Вернуться на главную
                  </Link>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-100">
                <p className="text-xs text-center text-gray-500 leading-relaxed">
                  Регистрируясь, вы соглашаетесь с{' '}
                  <a href="#" className="text-purple-600 hover:text-purple-800 hover:underline">
                    условиями использования
                  </a>
                  {' '}и{' '}
                  <a href="#" className="text-purple-600 hover:text-purple-800 hover:underline">
                    политикой конфиденциальности
                  </a>
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Мобильная версия преимуществ */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="lg:hidden absolute bottom-8 left-0 right-0 px-4"
      >
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 text-white text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Gift className="h-5 w-5" />
            <span className="font-semibold">50 анализов бесплатно</span>
          </div>
          <div className="text-sm text-white/80">
            Без кредитной карты • Готов за 2 минуты
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Register;
