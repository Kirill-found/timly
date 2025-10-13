/**
 * Страница регистрации Timly
 * Создание нового аккаунта для HR-специалистов
 */
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Mail, Lock, User, Eye, EyeOff, AlertCircle, Building } from 'lucide-react';
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
    <div className="min-h-screen flex items-center justify-center p-6"
         style={{ background: 'linear-gradient(135deg, hsl(var(--secondary)), hsl(var(--primary)))' }}>
      <Card className="w-full max-w-lg shadow-2xl">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <img src="/logo.jpg" alt="Timly Logo" className="h-20 w-20 rounded-full object-cover shadow-lg" />
          </div>
          <CardTitle className="text-3xl font-bold text-primary">
            Присоединяйтесь к Timly
          </CardTitle>
          <CardDescription className="text-base">
            Автоматизируйте найм с помощью AI
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="company_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Название компании</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                        <Input
                          placeholder="ООО Рога и копыта"
                          className="pl-10"
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
                    <FormLabel>Полное имя</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                        <Input
                          placeholder="Иван Иванов"
                          className="pl-10"
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
                    <FormLabel>Рабочий Email</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                        <Input
                          placeholder="hr@company.com"
                          className="pl-10"
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
                    <FormLabel>Пароль</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                        <Input
                          type={showPassword ? "text" : "password"}
                          placeholder="Создайте надежный пароль"
                          className="pl-10 pr-10"
                          autoComplete="new-password"
                          {...field}
                        />
                        <button
                          type="button"
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </FormControl>
                    <FormMessage />
                    <p className="text-xs text-muted-foreground mt-1">
                      Минимум 8 символов: строчные, заглавные буквы и цифры
                    </p>
                  </FormItem>
                )}
              />

              <Button
                type="submit"
                disabled={loading}
                className="w-full h-12 text-base bg-gradient-to-r from-blue-600 to-green-600 text-white hover:from-blue-700 hover:to-green-700 font-semibold shadow-md"
              >
                {loading ? 'Создаем аккаунт...' : 'Зарегистрироваться'}
              </Button>
            </form>
          </Form>

          <div className="text-center space-y-4">
            <p className="text-muted-foreground">
              Уже есть аккаунт?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-800 hover:underline font-medium">
                Войти
              </Link>
            </p>

            <p className="text-xs text-muted-foreground leading-relaxed">
              Регистрируясь, вы соглашаетесь с{' '}
              <a href="#" className="text-blue-600 hover:text-blue-800 hover:underline">условиями использования</a>
              {' '}и{' '}
              <a href="#" className="text-blue-600 hover:text-blue-800 hover:underline">политикой конфиденциальности</a>
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 text-center">
        <p className="text-white/80 text-sm mb-2">
          Все данные защищены шифрованием
        </p>
        <Link
          to="/"
          className="text-white/90 hover:text-white text-sm hover:underline"
        >
          ← Вернуться на главную
        </Link>
      </div>
    </div>
  );
};

export default Register;