/**
 * ForgotPassword - Восстановление пароля
 * Design: Warm Professional - тёплый, доверительный
 * Typography: Clash Display + Satoshi
 * Palette: Warm White + Deep Navy + Warm Orange
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
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
import { ArrowLeft, Mail, CheckCircle, AlertCircle, Loader2, KeyRound, Shield } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'https://timly-hr.ru/api';

const emailSchema = z.object({
  email: z
    .string()
    .min(1, { message: 'Введите email' })
    .email({ message: 'Некорректный email' }),
});

const codeSchema = z.object({
  code: z
    .string()
    .min(6, { message: 'Код должен содержать 6 символов' })
    .max(6, { message: 'Код должен содержать 6 символов' }),
  newPassword: z
    .string()
    .min(8, { message: 'Минимум 8 символов' })
    .regex(/[A-Z]/, { message: 'Нужна заглавная буква' })
    .regex(/[a-z]/, { message: 'Нужна строчная буква' })
    .regex(/\d/, { message: 'Нужна цифра' }),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword'],
});

type EmailFormValues = z.infer<typeof emailSchema>;
type CodeFormValues = z.infer<typeof codeSchema>;

type Step = 'email' | 'code' | 'success';

const ForgotPassword: React.FC = () => {
  const [step, setStep] = useState<Step>('email');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');

  const emailForm = useForm<EmailFormValues>({
    resolver: zodResolver(emailSchema),
    defaultValues: { email: '' },
  });

  const codeForm = useForm<CodeFormValues>({
    resolver: zodResolver(codeSchema),
    defaultValues: { code: '', newPassword: '', confirmPassword: '' },
  });

  const onEmailSubmit = async (values: EmailFormValues) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: values.email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail?.message || 'Ошибка отправки запроса');
      }

      setEmail(values.email);
      setStep('code');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  const onCodeSubmit = async (values: CodeFormValues) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          code: values.code,
          new_password: values.newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail?.message || 'Неверный код или код истёк');
      }

      setStep('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  const renderEmailStep = () => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
    >
      <div className="text-center mb-8">
        <div className="w-16 h-16 rounded-2xl bg-[#f97316]/10 flex items-center justify-center mx-auto mb-5">
          <Mail className="h-8 w-8 text-[#f97316]" />
        </div>
        <h1
          className="text-2xl text-[#1e3a5f] mb-2"
          style={{ fontFamily: "'Clash Display', sans-serif", fontWeight: 600 }}
        >
          Забыли пароль?
        </h1>
        <p className="text-[#64748b]">
          Введите email, на который зарегистрирован аккаунт
        </p>
      </div>

      <div className="rounded-2xl border border-[#1e3a5f]/10 bg-white/80 backdrop-blur-sm shadow-xl shadow-[#1e3a5f]/5 p-6 lg:p-8">
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3"
          >
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <span className="text-red-600 text-sm">{error}</span>
          </motion.div>
        )}

        <Form {...emailForm}>
          <form onSubmit={emailForm.handleSubmit(onEmailSubmit)} className="space-y-5">
            <FormField
              control={emailForm.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-[#334155] font-medium">Email</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="your@email.com"
                      className="h-12 bg-[#faf8f5] border-[#1e3a5f]/15 text-[#1e3a5f] placeholder:text-[#94a3b8] focus:border-[#f97316] focus:ring-[#f97316]/20 rounded-xl transition-all"
                      autoComplete="email"
                      autoFocus
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-red-500" />
                </FormItem>
              )}
            />

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-[#f97316] hover:bg-[#ea580c] text-white font-semibold rounded-xl shadow-lg shadow-[#f97316]/25 transition-all hover:shadow-xl hover:shadow-[#f97316]/30 hover:-translate-y-0.5"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Отправка...
                </span>
              ) : (
                'Отправить код'
              )}
            </Button>
          </form>
        </Form>
      </div>
    </motion.div>
  );

  const renderCodeStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className="text-center mb-8">
        <div className="w-16 h-16 rounded-2xl bg-[#1e3a5f]/10 flex items-center justify-center mx-auto mb-5">
          <KeyRound className="h-8 w-8 text-[#1e3a5f]" />
        </div>
        <h1
          className="text-2xl text-[#1e3a5f] mb-2"
          style={{ fontFamily: "'Clash Display', sans-serif", fontWeight: 600 }}
        >
          Введите код
        </h1>
        <p className="text-[#64748b]">
          Код восстановления отправлен на <span className="text-[#1e3a5f] font-medium">{email}</span>
        </p>
      </div>

      <div className="rounded-2xl border border-[#1e3a5f]/10 bg-white/80 backdrop-blur-sm shadow-xl shadow-[#1e3a5f]/5 p-6 lg:p-8">
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3"
          >
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <span className="text-red-600 text-sm">{error}</span>
          </motion.div>
        )}

        <Form {...codeForm}>
          <form onSubmit={codeForm.handleSubmit(onCodeSubmit)} className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-medium text-[#334155]">Код восстановления</label>
              <input
                type="text"
                id="reset-code"
                autoComplete="one-time-code"
                placeholder="000000"
                maxLength={6}
                className="flex h-14 w-full rounded-xl border border-[#1e3a5f]/15 bg-[#faf8f5] px-4 py-3 text-[#1e3a5f] placeholder:text-[#94a3b8] focus:border-[#f97316] focus:ring-2 focus:ring-[#f97316]/20 focus:outline-none text-center text-2xl tracking-[0.5em] font-mono transition-all"
                autoFocus
                value={code}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, '').slice(0, 6);
                  setCode(val);
                  codeForm.setValue('code', val);
                }}
              />
            </div>

            <FormField
              control={codeForm.control}
              name="newPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-[#334155] font-medium">Новый пароль</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Минимум 8 символов"
                      className="h-12 bg-[#faf8f5] border-[#1e3a5f]/15 text-[#1e3a5f] placeholder:text-[#94a3b8] focus:border-[#f97316] focus:ring-[#f97316]/20 rounded-xl transition-all"
                      autoComplete="new-password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-red-500" />
                </FormItem>
              )}
            />

            <FormField
              control={codeForm.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-[#334155] font-medium">Подтвердите пароль</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Повторите пароль"
                      className="h-12 bg-[#faf8f5] border-[#1e3a5f]/15 text-[#1e3a5f] placeholder:text-[#94a3b8] focus:border-[#f97316] focus:ring-[#f97316]/20 rounded-xl transition-all"
                      autoComplete="new-password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-red-500" />
                </FormItem>
              )}
            />

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-[#f97316] hover:bg-[#ea580c] text-white font-semibold rounded-xl shadow-lg shadow-[#f97316]/25 transition-all hover:shadow-xl hover:shadow-[#f97316]/30 hover:-translate-y-0.5"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Сброс пароля...
                </span>
              ) : (
                'Сбросить пароль'
              )}
            </Button>
          </form>
        </Form>

        <div className="mt-5 text-center">
          <button
            type="button"
            onClick={() => {
              setStep('email');
              setError(null);
            }}
            className="text-sm text-[#64748b] hover:text-[#1e3a5f] transition-colors"
          >
            Отправить код повторно
          </button>
        </div>
      </div>
    </motion.div>
  );

  const renderSuccessStep = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <div className="text-center mb-8">
        <div className="w-16 h-16 rounded-2xl bg-[#059669]/10 flex items-center justify-center mx-auto mb-5">
          <CheckCircle className="h-8 w-8 text-[#059669]" />
        </div>
        <h1
          className="text-2xl text-[#1e3a5f] mb-2"
          style={{ fontFamily: "'Clash Display', sans-serif", fontWeight: 600 }}
        >
          Пароль изменён
        </h1>
        <p className="text-[#64748b]">
          Теперь вы можете войти с новым паролем
        </p>
      </div>

      <div className="rounded-2xl border border-[#1e3a5f]/10 bg-white/80 backdrop-blur-sm shadow-xl shadow-[#1e3a5f]/5 p-6 lg:p-8">
        <Link to="/login">
          <Button className="w-full h-12 bg-[#f97316] hover:bg-[#ea580c] text-white font-semibold rounded-xl shadow-lg shadow-[#f97316]/25 transition-all hover:shadow-xl hover:shadow-[#f97316]/30 hover:-translate-y-0.5">
            Войти в систему
          </Button>
        </Link>
      </div>
    </motion.div>
  );

  return (
    <>
      {/* Fonts */}
      <style>{`
        @import url('https://api.fontshare.com/v2/css?f[]=clash-display@600,700&f[]=satoshi@400,500,700&display=swap');
      `}</style>

      <div
        className="min-h-screen flex items-center justify-center p-6"
        style={{
          fontFamily: "'Satoshi', sans-serif",
          background: 'linear-gradient(135deg, #faf8f5 0%, #f5f0eb 50%, #faf8f5 100%)'
        }}
      >
        {/* Gradient mesh background */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#f97316]/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-[#1e3a5f]/5 rounded-full blur-3xl" />
        </div>

        <div className="w-full max-w-md">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <Link to="/" className="inline-flex items-center gap-3 group">
              <img
                src="/timly-logo.png"
                alt="timly"
                className="h-10 w-10 rounded-xl transition-transform group-hover:scale-105"
              />
              <span
                className="text-2xl font-semibold text-[#1e3a5f]"
                style={{ fontFamily: "'Clash Display', sans-serif" }}
              >
                timly
              </span>
            </Link>
          </motion.div>

          <AnimatePresence mode="wait">
            {step === 'email' && renderEmailStep()}
            {step === 'code' && renderCodeStep()}
            {step === 'success' && renderSuccessStep()}
          </AnimatePresence>

          {step !== 'success' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="mt-6 text-center"
            >
              <Link
                to="/login"
                className="inline-flex items-center gap-2 text-sm text-[#94a3b8] hover:text-[#1e3a5f] transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                Вернуться ко входу
              </Link>
            </motion.div>
          )}

          {/* Security note */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-8 flex items-center justify-center gap-2 text-xs text-[#94a3b8]"
          >
            <Shield className="h-3.5 w-3.5" />
            <span>Защищённое соединение</span>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default ForgotPassword;
