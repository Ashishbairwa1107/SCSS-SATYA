import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Sun, Moon, PlusCircle, CheckCircle, AlertTriangle } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { api } from '../../services/api';

interface TopHeaderProps {
  onToggleMobileMenu: () => void;
}

export const TopHeader: React.FC<TopHeaderProps> = ({ onToggleMobileMenu }) => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const [healthStatus, setHealthStatus] = useState<string>('CHECKING');

  useEffect(() => {
    let mounted = true;
    api.getHealth()
      .then(res => {
        if (mounted) setHealthStatus(res.status);
      })
      .catch(() => {
        if (mounted) setHealthStatus('DEGRADED');
      });
    return () => { mounted = false; };
  }, [location.pathname]);

  const getBreadcrumbs = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/new')) return 'New Examination';
    if (path.startsWith('/examinations/')) return 'Examination Dossier';
    if (path.startsWith('/vault')) return 'Evidence Vault';
    if (path.startsWith('/methodology')) return 'Scientific Methodology';
    if (path.startsWith('/system')) return 'System Information';
    return 'Dossier';
  };

  return (
    <header className="h-16 bg-white dark:bg-[#111C2E] border-b border-[#DCE2EA] dark:border-[#24344D] px-4 md:px-8 flex items-center justify-between sticky top-0 z-30 transition-colors">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleMobileMenu}
          className="md:hidden p-2 rounded-lg text-[#657187] hover:text-[#172033] dark:hover:text-white"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <span className="text-xs text-[#657187] dark:text-[#94A3B8] font-medium">
            Forensic Laboratory /
          </span>
          <span className="ml-1 text-sm font-semibold text-[#172033] dark:text-white">
            {getBreadcrumbs()}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* System Health Status */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border border-[#DCE2EA] dark:border-[#24344D] bg-[#F4F6F9] dark:bg-[#172B47]/40">
          {healthStatus === 'HEALTHY' ? (
            <>
              <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-emerald-700 dark:text-emerald-300">System Healthy</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
              <span className="text-amber-700 dark:text-amber-300">Vault Connected</span>
            </>
          )}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] text-[#657187] hover:text-[#172033] dark:text-[#94A3B8] dark:hover:text-white bg-white dark:bg-[#172B47]/60 transition-colors"
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4 text-[#C5A059]" />}
        </button>

        {/* New Examination Primary CTA */}
        <Link
          to="/new"
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-[#0F1E36] hover:bg-[#172B47] text-white text-xs font-semibold shadow-xs border border-[#C5A059]/40 transition-colors"
        >
          <PlusCircle className="w-4 h-4 text-[#C5A059]" />
          <span>New Examination</span>
        </Link>
      </div>
    </header>
  );
};
