/**
 * AppLayout - Soft UI Light Theme
 */
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, BarChart3, Settings, LogOut, Menu, Loader2, Search, Users, Clock, FileText, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useAuth } from '@/store/AuthContext';
import { useApp } from '@/store/AppContext';
import { cn } from '@/lib/utils';

interface AppLayoutProps { children: React.ReactNode; }

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { activeAnalysis } = useApp();

  const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/analysis', icon: BarChart3, label: 'Вакансии' },
    { href: '/sync', icon: Clock, label: 'История' },
    { href: '/manual-analysis', icon: Users, label: 'Кандидаты' },
  ];
  const secondaryItems = [
    { href: '/export', icon: FileText, label: 'Шаблоны' },
    { href: '/settings', icon: Settings, label: 'Настройки' },
  ];
  const bottomItems = [{ href: '/pricing', icon: MessageSquare, label: 'Поддержка' }];

  const handleLogout = async () => { await logout(); navigate('/login'); };

  const getPageTitle = () => {
    const titles: Record<string, string> = {
      '/dashboard': 'Dashboard', '/analysis': 'Вакансии', '/manual-analysis': 'Кандидаты',
      '/sync': 'История', '/settings': 'Настройки', '/export': 'Экспорт', '/pricing': 'Тарифы'
    };
    return titles[location.pathname] || 'Timly';
  };

  const NavLink = ({ item }: { item: { href: string; icon: any; label: string } }) => {
    const Icon = item.icon;
    const isActive = location.pathname === item.href;
    return (
      <Link to={item.href} onClick={() => setMobileMenuOpen(false)}
        className={cn('flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-colors',
          isActive ? 'bg-foreground text-background' : 'text-muted-foreground hover:bg-muted hover:text-foreground')}>
        <Icon className="w-[18px] h-[18px]" strokeWidth={1.5} />
        <span>{item.label}</span>
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      {mobileMenuOpen && <div className="fixed inset-0 bg-black/20 z-40 lg:hidden" onClick={() => setMobileMenuOpen(false)} />}
      <aside className={cn('fixed left-0 top-0 z-50 h-screen w-[200px] bg-card border-r border-border flex flex-col transform transition-transform duration-200 ease-out lg:translate-x-0', mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0')}>
        <div className="h-14 px-4 flex items-center">
          <span className="text-lg font-bold text-foreground tracking-tight">timly</span>
          <sup className="text-[8px] font-medium text-muted-foreground ml-0.5">HR</sup>
        </div>
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => <NavLink key={item.href} item={item} />)}
          <div className="h-px bg-border my-3" />
          {secondaryItems.map((item) => <NavLink key={item.href} item={item} />)}
        </nav>
        <div className="px-3 py-3 border-t border-border">
          {bottomItems.map((item) => <NavLink key={item.href} item={item} />)}
        </div>
      </aside>
      <div className="lg:ml-[200px]">
        <header className="sticky top-0 z-30 h-14 bg-background flex items-center justify-between px-5 lg:px-8">
          <div className="flex items-center gap-4">
            <button onClick={() => setMobileMenuOpen(true)} className="lg:hidden p-1.5 -ml-1.5 text-muted-foreground hover:text-foreground"><Menu className="w-5 h-5" /></button>
            <div className="w-8 h-8 flex items-center justify-center rounded-md hover:bg-muted cursor-pointer">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-muted-foreground"><polyline points="15 18 9 12 15 6" /></svg>
            </div>
            <h1 className="text-xl font-semibold text-foreground tracking-tight">{getPageTitle()}</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3.5 py-2 bg-card border border-border rounded-lg w-[180px]">
              <Search className="w-4 h-4 text-muted-foreground" />
              <input type="text" placeholder="Search..." className="bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground w-full" />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="w-9 h-9 rounded-full bg-gradient-to-br from-orange-200 to-orange-300 flex items-center justify-center"><Users className="w-4 h-4 text-muted-foreground" /></button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={() => navigate('/settings')}><Settings className="mr-2 h-4 w-4" />Настройки</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}><LogOut className="mr-2 h-4 w-4" />Выйти</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
        <main className="min-h-[calc(100vh-56px)]">{children}</main>
      </div>
      {activeAnalysis && (
        <div className="fixed bottom-4 right-4 z-50 max-w-xs">
          <div className="bg-card border border-border rounded-xl p-4 shadow-lg">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center"><Loader2 className="w-4 h-4 text-muted-foreground animate-spin" /></div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-foreground">Анализ</div>
                <div className="text-xs text-muted-foreground">{activeAnalysis.analyzed} / {activeAnalysis.total}</div>
              </div>
              <Button variant="ghost" size="sm" className="h-7 px-2 text-xs" onClick={() => navigate('/analysis')}>Открыть</Button>
            </div>
            <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-foreground rounded-full transition-all" style={{ width: activeAnalysis.total > 0 ? (activeAnalysis.analyzed / activeAnalysis.total) * 100 + '%' : '0%' }} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AppLayout;
