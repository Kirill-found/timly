/**
 * Register - Регистрация
 * Design: Warm Professional - тёплый, доверительный
 * Typography: Clash Display + Satoshi
 * Palette: Warm White + Deep Navy + Warm Orange
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Eye, EyeOff, ArrowRight, ArrowLeft, Check, Sparkles, Users, FileText, Clock } from 'lucide-react';
import { useAuth } from '@/store/AuthContext';

// Timly Logo Component
const TimlyLogo = ({ className = "h-10 w-auto" }: { className?: string }) => (
  <svg viewBox="0 0 120 60" fill="none" className={className}>
    {/* Three connected people - heads */}
    <circle cx="25" cy="15" r="8" fill="#1e3a5f"/>
    <circle cx="60" cy="15" r="8" fill="#1e3a5f"/>
    <circle cx="95" cy="15" r="8" fill="#1e3a5f"/>
    {/* Bodies with holes (torso rings) */}
    <circle cx="25" cy="32" r="7" stroke="#1e3a5f" strokeWidth="4" fill="none"/>
    <circle cx="60" cy="32" r="7" stroke="#1e3a5f" strokeWidth="4" fill="none"/>
    <circle cx="95" cy="32" r="7" stroke="#1e3a5f" strokeWidth="4" fill="none"/>
    {/* Connecting wave with loops */}
    <path
      d="M18 42 Q25 55 32 42 Q40 30 48 42 Q55 55 62 42 Q70 30 78 42 Q85 55 92 42 Q99 30 102 42"
      stroke="#1e3a5f"
      strokeWidth="4"
      fill="none"
      strokeLinecap="round"
    />
  </svg>
);

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

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const stagger = {
    visible: {
      transition: {
        staggerChildren: 0.08
      }
    }
  };

  return (
    <>
      {/* Fonts */}
      <style>{`
        @import url('https://api.fontshare.com/v2/css?f[]=clash-display@600,700&f[]=satoshi@400,500,700&display=swap');
      `}</style>

      <div
        className="min-h-screen flex"
        style={{
          fontFamily: "'Satoshi', sans-serif",
          background: 'linear-gradient(135deg, #faf8f5 0%, #f5f0eb 50%, #faf8f5 100%)'
        }}
      >
        {/* Gradient mesh background */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-[#f97316]/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-[#1e3a5f]/5 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-[#f97316]/3 rounded-full blur-3xl" />
        </div>

        {/* Left side - Branding & Features */}
        <div className="hidden lg:flex lg:w-[45%] flex-col justify-between p-12 relative">
          {/* Decorative pattern */}
          <div className="absolute inset-0 opacity-[0.03]" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%231e3a5f' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />

          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
          >
            {/* Logo */}
            <motion.div variants={fadeIn}>
              <Link to="/" className="inline-flex items-center gap-3 mb-16 group">
                <TimlyLogo className="h-10 w-auto transition-transform group-hover:scale-105" />
                <span
                  className="text-2xl font-semibold text-[#1e3a5f] tracking-tight"
                  style={{ fontFamily: "'Clash Display', sans-serif" }}
                >
                  timly
                </span>
              </Link>
            </motion.div>

            {/* Headline */}
            <motion.h2
              variants={fadeIn}
              className="text-[2.5rem] leading-[1.1] text-[#1e3a5f] mb-6"
              style={{ fontFamily: "'Clash Display', sans-serif", fontWeight: 600 }}
            >
              Начните работать<br />
              <span className="text-[#f97316]">с AI-скринингом</span>
            </motion.h2>

            <motion.p variants={fadeIn} className="text-[#64748b] text-lg mb-12 max-w-md leading-relaxed">
              Регистрация занимает 2 минуты. 50 анализов резюме бесплатно — без карты и обязательств.
            </motion.p>

            {/* Features */}
            <motion.div variants={fadeIn} className="space-y-5">
              {[
                { icon: Sparkles, text: 'AI-оценка по 15+ критериям', color: '#f97316' },
                { icon: Users, text: 'Интеграция с HeadHunter', color: '#1e3a5f' },
                { icon: FileText, text: 'Экспорт отчётов в Excel', color: '#059669' },
                { icon: Clock, text: '100 резюме за 10 минут', color: '#f97316' },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  className="flex items-center gap-4"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.1 }}
                >
                  <div
                    className="w-11 h-11 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${item.color}10` }}
                  >
                    <item.icon className="h-5 w-5" style={{ color: item.color }} />
                  </div>
                  <span className="text-[#334155] font-medium">{item.text}</span>
                </motion.div>
              ))}
            </motion.div>

            {/* Stats */}
            <motion.div
              variants={fadeIn}
              className="mt-16 flex gap-10"
            >
              {[
                { value: '50', label: 'анализов бесплатно' },
                { value: '2 мин', label: 'на регистрацию' },
                { value: '80%', label: 'экономия времени' },
              ].map((stat, i) => (
                <div key={i}>
                  <div
                    className="text-3xl font-bold text-[#1e3a5f] tabular-nums"
                    style={{ fontFamily: "'Clash Display', sans-serif" }}
                  >
                    {stat.value}
                  </div>
                  <div className="text-sm text-[#94a3b8] mt-1">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-sm text-[#94a3b8]"
          >
            © 2024 timly. AI-скрининг резюме.
          </motion.div>
        </div>

        {/* Right side - Form */}
        <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
          <div className="w-full max-w-md">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            >
              {/* Mobile header */}
              <div className="text-center mb-8 lg:hidden">
                <Link to="/" className="inline-flex items-center gap-3 mb-6">
                  <TimlyLogo className="h-9 w-auto" />
                  <span
                    className="text-xl font-semibold text-[#1e3a5f]"
                    style={{ fontFamily: "'Clash Display', sans-serif" }}
                  >
                    timly
                  </span>
                </Link>
              </div>

              {/* Form header */}
              <div className="mb-8">
                <h1
                  className="text-2xl lg:text-3xl text-[#1e3a5f] mb-2"
                  style={{ fontFamily: "'Clash Display', sans-serif", fontWeight: 600 }}
                >
                  Создать аккаунт
                </h1>
                <p className="text-[#64748b]">Начните использовать timly бесплатно</p>
              </div>

              {/* Mobile Benefits */}
              <div className="lg:hidden mb-6 p-4 rounded-2xl border border-[#1e3a5f]/10 bg-white/60 backdrop-blur-sm">
                <div className="grid grid-cols-2 gap-3">
                  {[
                    '50 анализов бесплатно',
                    'Без кредитной карты',
                    'Интеграция с HH.ru',
                    'Экспорт в Excel',
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-[#334155]">
                      <Check className="h-4 w-4 text-[#059669] flex-shrink-0" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Form Card */}
              <div className="rounded-2xl border border-[#1e3a5f]/10 bg-white/80 backdrop-blur-sm shadow-xl shadow-[#1e3a5f]/5 p-6 lg:p-8">
                {/* Error */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm"
                  >
                    {error}
                  </motion.div>
                )}

                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                    <FormField
                      control={form.control}
                      name="company_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-[#334155] font-medium">Компания</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Название компании"
                              className="h-12 bg-[#faf8f5] border-[#1e3a5f]/15 text-[#1e3a5f] placeholder:text-[#94a3b8] focus:border-[#f97316] focus:ring-[#f97316]/20 rounded-xl transition-all"
                              autoComplete="organization"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage className="text-red-500" />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="full_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-[#334155] font-medium">Ваше имя</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Иван Иванов"
                              className="h-12 bg-[#faf8f5] border-[#1e3a5f]/15 text-[#1e3a5f] placeholder:text-[#94a3b8] focus:border-[#f97316] focus:ring-[#f97316]/20 rounded-xl transition-all"
                              autoComplete="name"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage className="text-red-500" />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-[#334155] font-medium">Email</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="hr@company.com"
                              className="h-12 bg-[#faf8f5] border-[#1e3a5f]/15 text-[#1e3a5f] placeholder:text-[#94a3b8] focus:border-[#f97316] focus:ring-[#f97316]/20 rounded-xl transition-all"
                              autoComplete="email"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage className="text-red-500" />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="password"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-[#334155] font-medium">Пароль</FormLabel>
                          <FormControl>
                            <div className="relative">
                              <Input
                                type={showPassword ? 'text' : 'password'}
                                placeholder="Минимум 8 символов"
                                className="h-12 bg-[#faf8f5] border-[#1e3a5f]/15 text-[#1e3a5f] placeholder:text-[#94a3b8] focus:border-[#f97316] focus:ring-[#f97316]/20 rounded-xl transition-all pr-12"
                                autoComplete="new-password"
                                {...field}
                              />
                              <button
                                type="button"
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-[#94a3b8] hover:text-[#1e3a5f] transition-colors"
                                onClick={() => setShowPassword(!showPassword)}
                              >
                                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                              </button>
                            </div>
                          </FormControl>
                          <FormMessage className="text-red-500" />
                          <p className="text-xs text-[#94a3b8] mt-1.5">
                            Строчные, заглавные буквы и цифры
                          </p>
                        </FormItem>
                      )}
                    />

                    <Button
                      type="submit"
                      disabled={loading}
                      className="w-full h-12 bg-[#f97316] hover:bg-[#ea580c] text-white font-semibold rounded-xl shadow-lg shadow-[#f97316]/25 transition-all hover:shadow-xl hover:shadow-[#f97316]/30 hover:-translate-y-0.5 mt-2"
                    >
                      {loading ? (
                        <span className="flex items-center gap-2">
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Создание...
                        </span>
                      ) : (
                        <span className="flex items-center gap-2">
                          Создать аккаунт
                          <ArrowRight className="h-5 w-5" />
                        </span>
                      )}
                    </Button>
                  </form>
                </Form>

                {/* Divider */}
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-[#1e3a5f]/10" />
                  </div>
                  <div className="relative flex justify-center">
                    <span className="px-4 bg-white text-sm text-[#94a3b8]">или</span>
                  </div>
                </div>

                {/* Links */}
                <div className="text-center">
                  <p className="text-[#64748b]">
                    Уже есть аккаунт?{' '}
                    <Link
                      to="/login"
                      className="text-[#f97316] hover:text-[#ea580c] font-medium transition-colors"
                    >
                      Войти
                    </Link>
                  </p>
                </div>
              </div>

              {/* Back to home */}
              <div className="mt-6 text-center">
                <Link
                  to="/"
                  className="inline-flex items-center gap-2 text-sm text-[#94a3b8] hover:text-[#1e3a5f] transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Вернуться на главную
                </Link>
              </div>

              {/* Terms */}
              <p className="mt-4 text-xs text-center text-[#94a3b8]">
                Регистрируясь, вы соглашаетесь с{' '}
                <Link to="/terms" className="text-[#64748b] hover:text-[#1e3a5f] transition-colors">
                  условиями использования
                </Link>
                {' '}и{' '}
                <Link to="/privacy" className="text-[#64748b] hover:text-[#1e3a5f] transition-colors">
                  политикой конфиденциальности
                </Link>
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Register;
