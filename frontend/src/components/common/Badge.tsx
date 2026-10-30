import React from 'react';
import { FindingStatus, IntegrityStatus, ReviewStatus } from '../../types/api';

interface BadgeProps {
  status: FindingStatus | IntegrityStatus | ReviewStatus | string;
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({ status, size = 'md' }) => {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  let colorClasses = 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700';

  switch (status) {
    case 'No Indicator Detected':
    case 'VERIFIED':
    case 'COMPLETED':
      colorClasses = 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/50';
      break;

    case 'Indicator Observed':
    case 'MISMATCH':
    case 'FAILED':
      colorClasses = 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/50';
      break;

    case 'Inconclusive':
    case 'UNVERIFIED':
    case 'PENDING':
    case 'PROCESSING':
      colorClasses = 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800/60 dark:text-slate-300 dark:border-slate-700';
      break;

    case 'Examiner Opinion Recorded':
      colorClasses = 'bg-[#C5A059]/10 text-[#C5A059] border-[#C5A059]/30 dark:bg-[#C5A059]/20 dark:text-[#E0BE78] dark:border-[#C5A059]/40';
      break;

    case 'Under Review':
      colorClasses = 'bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800/50';
      break;

    case 'Pending Review':
      colorClasses = 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/50';
      break;

    default:
      break;
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${sizeClasses} ${colorClasses}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {status}
    </span>
  );
};
