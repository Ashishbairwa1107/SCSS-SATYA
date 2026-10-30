import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';

interface AlertProps {
  title?: string;
  children: React.ReactNode;
  variant?: 'info' | 'doctrine' | 'warning' | 'error' | 'success';
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  title,
  children,
  variant = 'info',
  className = '',
}) => {
  let styleClasses = 'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-950/30 dark:border-blue-800/40 dark:text-blue-200';
  let Icon = Info;

  if (variant === 'doctrine') {
    styleClasses = 'bg-[#FAF7F0] border-[#C5A059]/40 text-[#172033] dark:bg-[#1A2536] dark:border-[#C5A059]/50 dark:text-[#F1F5F9]';
    Icon = Info;
  } else if (variant === 'warning') {
    styleClasses = 'bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-950/30 dark:border-amber-800/40 dark:text-amber-200';
    Icon = AlertTriangle;
  } else if (variant === 'error') {
    styleClasses = 'bg-rose-50 border-rose-200 text-rose-900 dark:bg-rose-950/30 dark:border-rose-800/40 dark:text-rose-200';
    Icon = AlertCircle;
  } else if (variant === 'success') {
    styleClasses = 'bg-emerald-50 border-emerald-200 text-emerald-900 dark:bg-emerald-950/30 dark:border-emerald-800/40 dark:text-emerald-200';
    Icon = CheckCircle2;
  }

  return (
    <div className={`p-4 rounded-lg border flex items-start gap-3 text-sm ${styleClasses} ${className}`}>
      <Icon className="w-5 h-5 shrink-0 mt-0.5" />
      <div className="flex-1">
        {title && <h4 className="font-semibold text-sm mb-1">{title}</h4>}
        <div className="text-xs leading-relaxed opacity-90">{children}</div>
      </div>
    </div>
  );
};
