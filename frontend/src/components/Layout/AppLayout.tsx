/**
 * AppLayout - Dark Industrial Theme
 * Минималистичный сайдбар в стиле терминала
 */
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  RefreshCw,
  Settings,
  Download,
  LogOut,
  Menu,
  CreditCard,
  Shield,
  Loader2,
  Search,
  Upload,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

import { Button } from '@/components/ui/button';
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { activeSyncJobs, activeAnalysis } = useApp();

  // Навигация
  const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Дашборд' },
    { href: '/analysis', icon: BarChart3, label: 'Анализ' },
    { href: '/candidate-search', icon: Search, label: 'Кандидаты' },
    { href: '/manual-analysis', icon: Upload, label: 'Ручной анализ' },
  ];

  const secondaryItems = [
    { href: '/sync', icon: RefreshCw, label: 'Синхронизация', badge: activeSyncJobs.length },
    { href: '/export', icon: Download, label: 'Экспорт' },
  ];

  const bottomItems = [
    { href: '/pricing', icon: CreditCard, label: 'Тарифы' },
    ...(user?.role === 'admin' ? [{ href: '/admin', icon: Shield, label: 'Админ-панель' }] : []),
    { href: '/settings', icon: Settings, label: 'Настройки' },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getUserInitial = () => {
    if (user?.company_name) return user.company_name[0].toUpperCase();
    if (user?.email) return user.email[0].toUpperCase();
    return 'U';
  };

  const NavLink = ({ item }: { item: { href: string; icon: any; label: string; badge?: number } }) => {
    const Icon = item.icon;
    const isActive = location.pathname === item.href;

    return (
      <Link
        to={item.href}
        onClick={() => setMobileMenuOpen(false)}
        className={cn(
          "flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] font-medium transition-colors",
          isActive
            ? "bg-zinc-800 text-zinc-100"
            : "text-zinc-500 hover:bg-zinc-900 hover:text-zinc-300"
        )}
      >
        <Icon className={cn("w-4 h-4", isActive ? "opacity-100" : "opacity-60")} strokeWidth={1.5} />
        <span>{item.label}</span>
        {item.badge && item.badge > 0 && (
          <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">
            {item.badge}
          </span>
        )}
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-50 h-screen w-[220px] bg-background border-r border-zinc-800 flex flex-col",
          "transform transition-transform duration-200 ease-out",
          "lg:translate-x-0",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Logo */}
        <div className="h-[52px] px-4 flex items-center gap-2 border-b border-zinc-800">
          <span className="text-[15px] font-semibold text-zinc-100">Timly</span>
          <span className="text-[10px] font-medium px-1.5 py-0.5 bg-zinc-800 border border-zinc-700 rounded text-zinc-500">
            beta
          </span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
          {/* Main nav */}
          {navItems.map((item) => (
            <NavLink key={item.href} item={item} />
          ))}

          {/* Divider */}
          <div className="h-px bg-zinc-800 my-3" />

          {/* Secondary nav */}
          {secondaryItems.map((item) => (
            <NavLink key={item.href} item={item} />
          ))}

          {/* Divider */}
          <div className="h-px bg-zinc-800 my-3" />

          {/* Bottom nav */}
          {bottomItems.map((item) => (
            <NavLink key={item.href} item={item} />
          ))}
        </nav>

        {/* User block */}
        <div className="p-3 border-t border-zinc-800">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="w-full flex items-center gap-2.5 p-2 rounded-md hover:bg-zinc-900 transition-colors">
                <div className="w-7 h-7 rounded-md bg-zinc-800 border border-zinc-700 flex items-center justify-center text-[11px] font-medium text-zinc-400">
                  {getUserInitial()}
                </div>
                <div className="flex-1 text-left min-w-0">
                  <div className="text-[13px] font-medium text-zinc-200 truncate">
                    {user?.email?.split('@')[0] || 'user'}
                  </div>
                </div>
                <ChevronUp className="w-3.5 h-3.5 text-zinc-600" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="start"
              side="top"
              className="w-[196px] bg-zinc-900 border-zinc-800"
            >
              <DropdownMenuItem
                onClick={() => navigate('/settings')}
                className="text-zinc-300 focus:bg-zinc-800 focus:text-zinc-100"
              >
                <Settings className="mr-2 h-4 w-4 opacity-60" />
                Настройки
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-zinc-800" />
              <DropdownMenuItem
                onClick={handleLogout}
                className="text-zinc-300 focus:bg-zinc-800 focus:text-zinc-100"
              >
                <LogOut className="mr-2 h-4 w-4 opacity-60" />
                Выйти
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>

      {/* Main area */}
      <div className="lg:ml-[220px]">
        {/* Header */}
        <header className="sticky top-0 z-30 h-[52px] border-b border-zinc-800 bg-background flex items-center justify-between px-4 lg:px-6">
          <div className="flex items-center gap-4">
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden p-1.5 -ml-1.5 text-zinc-400 hover:text-zinc-200"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* Page title - можно добавить динамически */}
            <span className="text-sm font-medium text-zinc-300 hidden sm:block">
              {location.pathname === '/dashboard' && 'Панель управления'}
              {location.pathname === '/analysis' && 'Анализ резюме'}
              {location.pathname === '/candidate-search' && 'Поиск кандидатов'}
              {location.pathname === '/sync' && 'Синхронизация'}
              {location.pathname === '/settings' && 'Настройки'}
            </span>

            {/* HH.ru status */}
            {user?.has_hh_token && (
              <div className="flex items-center gap-1.5 text-xs text-green-500">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                <span className="hidden sm:inline">HH.ru</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Sync button */}
            <Button
              variant="ghost"
              size="sm"
              asChild
              className="h-8 px-3 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 border border-zinc-800"
            >
              <Link to="/sync">
                <RefreshCw className={cn("w-3.5 h-3.5 mr-2", activeSyncJobs.length > 0 && "animate-spin")} />
                <span className="text-xs">Синхронизация</span>
                {activeSyncJobs.length > 0 && (
                  <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500">
                    {activeSyncJobs.length}
                  </span>
                )}
              </Link>
            </Button>

            {/* Analysis button */}
            <Button
              size="sm"
              asChild
              className="h-8 px-3 bg-zinc-100 text-zinc-900 hover:bg-zinc-200"
            >
              <Link to="/analysis">
                <span className="text-xs font-medium">Запустить анализ</span>
              </Link>
            </Button>
          </div>
        </header>

        {/* Content */}
        <main className="min-h-[calc(100vh-52px)]">
          {children}
        </main>
      </div>

      {/* Active analysis indicator */}
      {activeAnalysis && (
        <div className="fixed bottom-4 right-4 z-50 max-w-xs">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 shadow-2xl">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center">
                <Loader2 className="w-4 h-4 text-zinc-400 animate-spin" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-zinc-200">Анализ</div>
                <div className="text-xs text-zinc-500">
                  {activeAnalysis.analyzed} / {activeAnalysis.total}
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs text-zinc-400 hover:text-zinc-200"
                onClick={() => navigate('/analysis')}
              >
                Открыть
              </Button>
            </div>

            {/* Progress */}
            <div className="space-y-1.5">
              <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-zinc-400 rounded-full transition-all duration-300"
                  style={{
                    width: `${activeAnalysis.total > 0 ? (activeAnalysis.analyzed / activeAnalysis.total) * 100 : 0}%`
                  }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-zinc-600">
                <span>
                  {activeAnalysis.total > 0
                    ? Math.round((activeAnalysis.analyzed / activeAnalysis.total) * 100)
                    : 0}%
                </span>
                <span>Осталось: {activeAnalysis.total - activeAnalysis.analyzed}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AppLayout;
