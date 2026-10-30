import React from 'react';
import { Finding } from '../../types/api';
import { Badge } from '../common/Badge';
import { ShieldCheck, AlertTriangle, HelpCircle, ArrowRight } from 'lucide-react';

interface FindingCardProps {
  finding: Finding;
}

export const FindingCard: React.FC<FindingCardProps> = ({ finding }) => {
  let Icon = HelpCircle;
  let borderClass = 'border-[#DCE2EA] dark:border-[#24344D]';

  if (finding.status === 'No Indicator Detected') {
    Icon = ShieldCheck;
    borderClass = 'border-l-4 border-l-emerald-500 border-[#DCE2EA] dark:border-[#24344D]';
  } else if (finding.status === 'Indicator Observed') {
    Icon = AlertTriangle;
    borderClass = 'border-l-4 border-l-amber-500 border-[#DCE2EA] dark:border-[#24344D]';
  } else {
    borderClass = 'border-l-4 border-l-slate-400 border-[#DCE2EA] dark:border-[#24344D]';
  }

  return (
    <div
      className={`bg-white dark:bg-[#111C2E] rounded-xl border p-5 shadow-xs transition-colors space-y-4 ${borderClass}`}
    >
      {/* Finding Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-md bg-slate-100 dark:bg-[#172B47] text-[#0F1E36] dark:text-[#C5A059]">
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-[#172033] dark:text-white">
              {finding.indicator_name}
            </h4>
            <span className="text-[10px] font-mono text-[#657187] dark:text-[#94A3B8]">
              {finding.finding_key}
            </span>
          </div>
        </div>
        <Badge status={finding.status} />
      </div>

      {/* Observed Evidence */}
      <div className="p-3 rounded-lg bg-[#F8FAFC] dark:bg-[#172B47]/40 border border-[#DCE2EA] dark:border-[#24344D] text-xs">
        <span className="font-semibold text-[#0F1E36] dark:text-[#C5A059] block mb-1">
          Observed Measurement / Evidence:
        </span>
        <p className="font-mono text-[#172033] dark:text-slate-200 leading-relaxed">
          {finding.observed_evidence}
        </p>
      </div>

      {/* Explanation & Potential Significance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div className="space-y-1">
          <span className="font-semibold text-[#657187] dark:text-[#94A3B8] uppercase tracking-wider text-[10px]">
            Technical Explanation:
          </span>
          <p className="text-[#172033] dark:text-slate-300 leading-relaxed">
            {finding.explanation}
          </p>
        </div>

        <div className="space-y-1">
          <span className="font-semibold text-[#657187] dark:text-[#94A3B8] uppercase tracking-wider text-[10px]">
            Forensic Significance:
          </span>
          <p className="text-[#172033] dark:text-slate-300 leading-relaxed">
            {finding.significance}
          </p>
        </div>
      </div>

      {/* Limitations & Recommended Action */}
      <div className="pt-3 border-t border-[#DCE2EA] dark:border-[#24344D] grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div className="space-y-1">
          <span className="font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wider text-[10px] flex items-center gap-1">
            <span>Known Limitation:</span>
          </span>
          <p className="text-[#657187] dark:text-[#94A3B8] leading-relaxed italic">
            {finding.limitations}
          </p>
        </div>

        <div className="space-y-1">
          <span className="font-semibold text-[#0D9488] dark:text-emerald-400 uppercase tracking-wider text-[10px] flex items-center gap-1">
            <ArrowRight className="w-3 h-3" />
            <span>Recommended Human Action:</span>
          </span>
          <p className="text-[#172033] dark:text-slate-300 leading-relaxed">
            {finding.recommended_action}
          </p>
        </div>
      </div>
    </div>
  );
};
