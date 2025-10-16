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
  Shield
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
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { activeSyncJobs } = useApp();

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-green-50">
      {/* Боковая панель */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen bg-white/95 backdrop-blur border-r transition-all duration-200 shadow-lg",
          collapsed ? "w-16" : "w-60"
        )}
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
                    {!collapsed && <span>{item.label}</span>}
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
      <div className={cn("transition-all duration-200", collapsed ? "ml-16" : "ml-60")}>
        {/* Шапка */}
        <header className="sticky top-0 z-30 flex h-16 items-center border-b bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 shadow-sm">
          <div className="flex items-center justify-between w-full px-4">
            {/* Кнопка сворачивания меню */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleSidebar}
              className="h-8 w-8"
            >
              {collapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
            </Button>

            {/* Информация о пользователе и действия */}
            <div className="flex items-center gap-3">
              {/* Уведомления */}
              <div className="relative">
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

              {/* Компания пользователя */}
              {!collapsed && user?.company_name && (
                <span className="text-sm text-muted-foreground">
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
                    {!collapsed && (
                      <div className="text-left">
                        <div className="text-sm font-medium">
                          {user?.email?.split('@')[0] || 'Пользователь'}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {user?.has_hh_token ? 'HH.ru подключен' : 'Настроить HH.ru'}
                        </div>
                      </div>
                    )}
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
    </div>
  );
};

export default AppLayout;