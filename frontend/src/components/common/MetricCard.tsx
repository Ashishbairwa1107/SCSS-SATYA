import React from 'react';

interface MetricCardProps {
  label: string;
  value: number | string;
  subtext?: string;
  icon: React.ReactNode;
  variant?: 'default' | 'accent' | 'warning' | 'alert';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  icon,
  variant = 'default',
}) => {
  let borderHighlight = 'border-[#DCE2EA] dark:border-[#24344D]';
  if (variant === 'accent') borderHighlight = 'border-l-4 border-l-[#C5A059] border-[#DCE2EA] dark:border-[#24344D]';
  if (variant === 'warning') borderHighlight = 'border-l-4 border-l-amber-500 border-[#DCE2EA] dark:border-[#24344D]';
  if (variant === 'alert') borderHighlight = 'border-l-4 border-l-rose-500 border-[#DCE2EA] dark:border-[#24344D]';

  return (
    <div
      className={`bg-white dark:bg-[#111C2E] p-5 rounded-lg border shadow-xs transition-colors ${borderHighlight}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold tracking-wider uppercase text-[#657187] dark:text-[#94A3B8]">
          {label}
        </span>
        <div className="p-2 rounded-md bg-[#F4F6F9] dark:bg-[#172B47] text-[#0F1E36] dark:text-[#C5A059]">
          {icon}
        </div>
      </div>
      <div className="mt-3">
        <span className="text-2xl font-bold tracking-tight text-[#172033] dark:text-white">
          {value}
        </span>
        {subtext && (
          <p className="mt-1 text-xs text-[#657187] dark:text-[#94A3B8]">
            {subtext}
          </p>
        )}
      </div>
    </div>
  );
};
