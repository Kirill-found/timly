/**
 * Основной layout приложения Timly
 * Боковая панель навигации и header с информацией о пользователе
 */
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  RefreshCw,
  Settings,
  Download,
  User,
  LogOut,
  Menu,
  X,
  Bell,
  CreditCard,
  Shield,
  Brain,
  Loader2,
  Search

} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/store/AuthContext';
import { useApp } from '@/store/AppContext';
import { cn } from '@/lib/utils';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false); // Мобильное меню
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { activeSyncJobs, activeAnalysis } = useApp();

  // Пункты меню
  const menuItems = [
    {
      key: '/dashboard',
      icon: LayoutDashboard,
      label: 'Панель управления',
      href: '/dashboard',
    },
    {
      key: '/analysis',
      icon: BarChart3,
      label: 'Анализ резюме',
      href: '/analysis',
    },
    {
      key: '/candidate-search',
      icon: Search,
      label: 'Поиск кандидатов',
      href: '/candidate-search',
    },
    {
      key: '/sync',
      icon: RefreshCw,
      label: 'Синхронизация',
      href: '/sync',
      badge: activeSyncJobs.length,
    },
    {
      key: '/export',
      icon: Download,
      label: 'Экспорт данных',
      href: '/export',
    },
    {
      key: '/pricing',
      icon: CreditCard,
      label: 'Тарифы',
      href: '/pricing',
    },
    ...(user?.role === 'admin' ? [{
      key: '/admin',
      icon: Shield,
      label: 'Админ-панель',
      href: '/admin',
    }] : []),
    {
      key: '/settings',
      icon: Settings,
      label: 'Настройки',
      href: '/settings',
    },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  // Закрываем мобильное меню при клике на ссылку
  const handleMobileMenuClick = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-green-50">
      {/* Overlay для мобильного меню */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={toggleMobileMenu}
        />
      )}

      {/* Боковая панель */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-50 h-screen bg-white/95 backdrop-blur border-r transition-all duration-300 shadow-lg",
          // Десктоп версия
          "hidden lg:block",
          collapsed ? "lg:w-16" : "lg:w-60",
          // Мобильная версия - выдвижное меню
          "lg:translate-x-0",
          mobileMenuOpen ? "block" : "hidden lg:block"
        )}
        style={{
          // На мобильных всегда полная ширина меню
          width: window.innerWidth < 1024 ? '240px' : undefined
        }}
      >
        {/* Логотип */}
        <div className="flex h-16 items-center border-b px-4 gap-3">
          {collapsed ? (
            <img src="/logo.jpg" alt="Timly" className="h-10 w-10 rounded-full object-cover" />
          ) : (
            <>
              <img src="/logo.jpg" alt="Timly Logo" className="h-10 w-10 rounded-full object-cover shadow-md" />
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
                Timly
              </h1>
            </>
          )}
        </div>

        {/* Навигационное меню */}
        <nav className="p-2 mt-2">
          <ul className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;

              return (
                <li key={item.key}>
                  <Link
                    to={item.href}
                    onClick={handleMobileMenuClick} // Закрываем меню при клике на мобильных
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                      "hover:bg-accent hover:text-accent-foreground",
                      isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground"
                    )}
                  >
                    <div className="relative">
                      <Icon className="h-4 w-4" />
                      {item.badge && item.badge > 0 && (
                        <Badge
                          variant="destructive"
                          className="absolute -top-2 -right-2 h-4 w-4 p-0 text-[10px]"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </div>
                    <span className={cn("lg:inline", collapsed && "lg:hidden")}>
                      {item.label}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Информация о пользователе в свернутом состоянии */}
        {collapsed && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-primary text-primary-foreground">
                <User className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
          </div>
        )}
      </aside>

      {/* Основной контент */}
      <div className={cn(
        "transition-all duration-200",
        // На десктопе отступ зависит от состояния sidebar
        "lg:ml-16 lg:ml-60",
        collapsed ? "lg:ml-16" : "lg:ml-60",
        // На мобильных нет отступа
        "ml-0"
      )}>
        {/* Шапка */}
        <header className="sticky top-0 z-30 flex h-16 items-center border-b bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 shadow-sm">
          <div className="flex items-center justify-between w-full px-4">
            {/* Кнопка меню - разная логика для мобильных и десктопа */}
            <div className="flex items-center gap-3">
              {/* Мобильная кнопка - гамбургер */}
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleMobileMenu}
                className="h-8 w-8 lg:hidden"
              >
                <Menu className="h-5 w-5" />
              </Button>

              {/* Десктопная кнопка - сворачивание */}
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleSidebar}
                className="h-8 w-8 hidden lg:flex"
              >
                {collapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
              </Button>

              {/* Логотип на мобильных */}
              <div className="lg:hidden flex items-center gap-2">
                <img src="/logo.jpg" alt="Timly" className="h-8 w-8 rounded-full object-cover" />
                <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
                  Timly
                </h1>
              </div>
            </div>

            {/* Информация о пользователе и действия */}
            <div className="flex items-center gap-2 md:gap-3">
              {/* Уведомления - скрываем на маленьких экранах */}
              <div className="relative hidden sm:block">
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Bell className="h-4 w-4" />
                </Button>
                {activeSyncJobs.length > 0 && (
                  <Badge
                    variant="destructive"
                    className="absolute -top-1 -right-1 h-4 w-4 p-0 text-[10px]"
                  >
                    {activeSyncJobs.length}
                  </Badge>
                )}
              </div>

              {/* Компания пользователя - скрываем на мобильных */}
              {!collapsed && user?.company_name && (
                <span className="text-sm text-muted-foreground hidden md:inline">
                  {user.company_name}
                </span>
              )}

              {/* Dropdown с профилем пользователя */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-8 gap-2 px-2">
                    <Avatar className="h-6 w-6">
                      <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                        <User className="h-3 w-3" />
                      </AvatarFallback>
                    </Avatar>
                    {/* Информация о пользователе - скрываем на мобильных */}
                    <div className="text-left hidden md:block lg:block">
                      <div className="text-sm font-medium">
                        {user?.email?.split('@')[0] || 'Пользователь'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {user?.has_hh_token ? 'HH.ru подключен' : 'Настроить HH.ru'}
                      </div>
                    </div>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem onClick={() => navigate('/settings')}>
                    <User className="mr-2 h-4 w-4" />
                    Профиль
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Выйти
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        {/* Контент страниц */}
        <main className="bg-muted/30 min-h-[calc(100vh-4rem)]">
          {children}
        </main>
      </div>

      {/* Глобальный индикатор активного анализа */}
      {activeAnalysis && (
        <div className="fixed bottom-4 right-4 left-4 sm:left-auto sm:bottom-6 sm:right-6 z-50">
          <div className="bg-white rounded-lg shadow-2xl border-2 border-blue-500 p-3 sm:p-4 sm:min-w-[320px] max-w-full sm:max-w-none animate-in slide-in-from-bottom-5">
            <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
              <div className="relative flex-shrink-0">
                <Brain className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
                <Loader2 className="h-3 w-3 text-blue-600 animate-spin absolute -top-1 -right-1" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-xs sm:text-sm truncate">Анализ резюме</h3>
                <p className="text-[10px] sm:text-xs text-muted-foreground">
                  {activeAnalysis.analyzed} из {activeAnalysis.total}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 sm:h-8 px-2 text-[10px] sm:text-xs flex-shrink-0"
                onClick={() => navigate('/analysis')}
              >
                Открыть
              </Button>
            </div>

            {/* Прогресс-бар */}
            <div className="space-y-1">
              <div className="w-full bg-gray-200 rounded-full h-1.5 sm:h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-green-500 h-1.5 sm:h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${activeAnalysis.total > 0 ? (activeAnalysis.analyzed / activeAnalysis.total) * 100 : 0}%`
                  }}
                />
              </div>
              <div className="flex justify-between text-[10px] sm:text-xs text-muted-foreground">
                <span>
                  {activeAnalysis.total > 0
                    ? Math.round((activeAnalysis.analyzed / activeAnalysis.total) * 100)
                    : 0}%
                </span>
                <span className="truncate">Осталось: {activeAnalysis.total - activeAnalysis.analyzed}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AppLayout;