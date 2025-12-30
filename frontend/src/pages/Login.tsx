/**
 * Login - Вход в систему
 * Design: Dark Industrial - единый стиль
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Eye, EyeOff, ArrowRight, ArrowLeft, BarChart3, Users, Download, Zap } from 'lucide-react';
import { useAuth } from '@/store/AuthContext';

const formSchema = z.object({
  email: z
    .string()
    .min(1, { message: 'Введите email' })
    .email({ message: 'Некорректный email' }),
  password: z
    .string()
    .min(6, { message: 'Минимум 6 символов' }),
});

type LoginFormValues = z.infer<typeof formSchema>;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { login, error, clearError } = useAuth();

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (values: LoginFormValues) => {
    try {
      setLoading(true);
      clearError();
      await login(values);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      // Ошибка обработана в AuthContext
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex">
      {/* Left side - Features */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#0f0f0f] border-r border-zinc-800 flex-col justify-between p-12">
        <div>
          <Link to="/" className="inline-flex items-center gap-2.5 mb-12">
            <img src="/logo.jpg" alt="timly" className="h-10 w-10 rounded-xl" />
            <span className="text-xl font-semibold text-zinc-100 tracking-tight">timly<span className="text-zinc-500">.</span></span>
          </Link>

          <h2 className="text-3xl font-semibold text-zinc-100 mb-4 leading-tight">
            Автоматизируйте<br />скрининг резюме
          </h2>
          <p className="text-zinc-500 mb-10 max-w-sm">
            AI анализирует отклики с HH.ru и выдаёт топ-кандидатов за минуты вместо часов.
          </p>

          <div className="space-y-4">
            {[
              { icon: BarChart3, text: 'AI-оценка по 15+ критериям' },
              { icon: Users, text: 'Интеграция с HeadHunter' },
              { icon: Download, text: 'Экспорт отчётов в Excel' },
              { icon: Zap, text: '100 резюме за 10 минут' },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-zinc-800 flex items-center justify-center">
                  <item.icon className="h-4 w-4 text-zinc-400" />
                </div>
                <span className="text-sm text-zinc-400">{item.text}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="text-xs text-zinc-600">
          © 2024 timly. AI-скрининг резюме.
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {/* Mobile header */}
            <div className="text-center mb-8">
              <Link to="/" className="lg:hidden inline-flex items-center gap-2.5 mb-6">
                <img src="/logo.jpg" alt="timly" className="h-10 w-10 rounded-xl" />
                <span className="text-xl font-semibold text-zinc-100 tracking-tight">timly<span className="text-zinc-500">.</span></span>
              </Link>
              <h1 className="text-2xl font-semibold text-zinc-100 mb-2">Вход в систему</h1>
              <p className="text-sm text-zinc-500">Введите данные для входа в аккаунт</p>
            </div>

          {/* Form Card */}
          <Card className="border-zinc-800 bg-zinc-900/50">
            <CardContent className="p-6">
              {/* Error */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                >
                  {error}
                </motion.div>
              )}

              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-zinc-300">Email</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="your@email.com"
                            className="h-11 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500"
                            autoComplete="email"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage className="text-red-400" />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-zinc-300">Пароль</FormLabel>
                        <FormControl>
                          <div className="relative">
                            <Input
                              type={showPassword ? 'text' : 'password'}
                              placeholder="Введите пароль"
                              className="h-11 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500 pr-10"
                              autoComplete="current-password"
                              {...field}
                            />
                            <button
                              type="button"
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 transition-colors"
                              onClick={() => setShowPassword(!showPassword)}
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                          </div>
                        </FormControl>
                        <FormMessage className="text-red-400" />
                      </FormItem>
                    )}
                  />

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-11 bg-zinc-100 text-zinc-900 hover:bg-white font-medium"
                  >
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-zinc-400 border-t-zinc-900 rounded-full animate-spin" />
                        Вход...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        Войти
                        <ArrowRight className="h-4 w-4" />
                      </span>
                    )}
                  </Button>
                </form>
              </Form>

              {/* Divider */}
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-zinc-800" />
                </div>
                <div className="relative flex justify-center">
                  <span className="px-3 bg-zinc-900/50 text-xs text-zinc-600">или</span>
                </div>
              </div>

              {/* Links */}
              <div className="text-center space-y-3">
                <Link
                  to="/forgot-password"
                  className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
                >
                  Забыли пароль?
                </Link>
                <p className="text-sm text-zinc-500">
                  Нет аккаунта?{' '}
                  <Link to="/register" className="text-zinc-300 hover:text-white transition-colors">
                    Зарегистрироваться
                  </Link>
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Back to home */}
          <div className="mt-6 text-center">
            <Link
              to="/"
              className="inline-flex items-center gap-2 text-sm text-zinc-600 hover:text-zinc-400 transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Вернуться на главную
            </Link>
          </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Login;
