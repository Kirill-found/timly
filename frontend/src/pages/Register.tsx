/**
 * Register - Регистрация
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
import { Eye, EyeOff, ArrowRight, ArrowLeft, Check } from 'lucide-react';
import { useAuth } from '@/store/AuthContext';

const formSchema = z.object({
  company_name: z
    .string()
    .min(2, { message: 'Минимум 2 символа' })
    .max(100, { message: 'Слишком длинное' }),
  full_name: z
    .string()
    .min(2, { message: 'Минимум 2 символа' })
    .max(50, { message: 'Слишком длинное' }),
  email: z
    .string()
    .min(1, { message: 'Введите email' })
    .email({ message: 'Некорректный email' }),
  password: z
    .string()
    .min(8, { message: 'Минимум 8 символов' })
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
      message: 'Нужны строчные, заглавные буквы и цифры'
    }),
});

type RegisterFormValues = z.infer<typeof formSchema>;

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
  });

  const onSubmit = async (values: RegisterFormValues) => {
    try {
      setLoading(true);
      clearError();
      await register(values);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      // Ошибка обработана в AuthContext
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center p-4 py-8">
      <div className="w-full max-w-md">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Header */}
          <div className="text-center mb-6">
            <Link to="/" className="inline-flex items-center gap-3 mb-4">
              <img src="/logo.jpg" alt="Timly" className="h-10 w-10 rounded-xl" />
              <span className="text-xl font-semibold text-zinc-100">Timly</span>
            </Link>
            <h1 className="text-2xl font-semibold text-zinc-100 mb-2">Создать аккаунт</h1>
            <p className="text-sm text-zinc-500">Начните использовать Timly бесплатно</p>
          </div>

          {/* Benefits */}
          <div className="mb-6 p-4 rounded-lg border border-zinc-800 bg-zinc-900/30">
            <div className="grid grid-cols-2 gap-3">
              {[
                '50 анализов бесплатно',
                'Без кредитной карты',
                'Интеграция с HH.ru',
                'Экспорт в Excel',
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-zinc-400">
                  <Check className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
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
                    name="company_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-zinc-300">Компания</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Название компании"
                            className="h-11 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500"
                            autoComplete="organization"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage className="text-red-400" />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="full_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-zinc-300">Ваше имя</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Иван Иванов"
                            className="h-11 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500"
                            autoComplete="name"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage className="text-red-400" />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-zinc-300">Email</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="hr@company.com"
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
                              placeholder="Минимум 8 символов"
                              className="h-11 bg-zinc-800/50 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-zinc-500 pr-10"
                              autoComplete="new-password"
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
                        <p className="text-[11px] text-zinc-600 mt-1">
                          Строчные, заглавные буквы и цифры
                        </p>
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
                        Создание...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        Создать аккаунт
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
              <div className="text-center">
                <p className="text-sm text-zinc-500">
                  Уже есть аккаунт?{' '}
                  <Link to="/login" className="text-zinc-300 hover:text-white transition-colors">
                    Войти
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

          {/* Terms */}
          <p className="mt-4 text-[11px] text-center text-zinc-600">
            Регистрируясь, вы соглашаетесь с условиями использования и политикой конфиденциальности
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Register;
