import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldAlert,
  LayoutDashboard,
  PlusCircle,
  Archive,
  BookOpen,
  Server,
  FlaskConical,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  onCloseMobile?: () => void;
  onGenerateSpecimen?: (type: 'camera-style' | 'spliced-composite' | 'lossless-png') => void;
  isGeneratingSpecimen?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  onCloseMobile,
  onGenerateSpecimen,
  isGeneratingSpecimen,
}) => {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/new', label: 'New Examination', icon: PlusCircle },
    { to: '/vault', label: 'Evidence Vault', icon: Archive },
    { to: '/methodology', label: 'Methodology', icon: BookOpen },
    { to: '/system', label: 'System Information', icon: Server },
  ];

  return (
    <aside className="w-64 bg-[#0F1E36] text-white flex flex-col h-full border-r border-[#172B47] select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#172B47]">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-[#172B47] text-[#C5A059] border border-[#C5A059]/30">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold tracking-tight text-base text-white flex items-center gap-1.5">
              SCSS SATYA
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#C5A059]/20 text-[#C5A059] border border-[#C5A059]/30">
                v1.0
              </span>
            </h1>
            <p className="text-[10px] text-slate-400 font-medium tracking-wide uppercase">
              Forensic Screening Platform
            </p>
          </div>
        </div>

        {/* Guiding Doctrine Notice */}
        <div className="mt-4 p-2.5 rounded bg-[#172B47]/60 border border-[#C5A059]/30">
          <span className="text-[9px] uppercase tracking-wider text-[#C5A059] font-bold block">
            Guiding Doctrine
          </span>
          <p className="text-[11px] font-medium text-slate-200 italic mt-0.5">
            "The tool screens. The expert decides."
          </p>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 px-3 py-1">
          Forensic Workspace
        </div>
        {navItems.map(item => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onCloseMobile}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-[#172B47] text-white border-l-3 border-[#C5A059]'
                    : 'text-slate-300 hover:text-white hover:bg-[#172B47]/50'
                }`
              }
            >
              <Icon className="w-4 h-4 text-[#C5A059]" />
              {item.label}
            </NavLink>
          );
        })}

        {/* Specimen Generators */}
        {onGenerateSpecimen && (
          <div className="pt-6">
            <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400 px-3 py-1 flex items-center justify-between">
              <span>Test Calibration</span>
              <FlaskConical className="w-3.5 h-3.5 text-[#C5A059]" />
            </div>
            <div className="px-2 pt-1.5 space-y-1.5">
              <button
                disabled={isGeneratingSpecimen}
                onClick={() => onGenerateSpecimen('camera-style')}
                className="w-full text-left px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-[#172B47] hover:text-white transition-colors flex items-center gap-2 border border-slate-700/50"
              >
                <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="truncate">Specimen A: Camera Photo</span>
              </button>
              <button
                disabled={isGeneratingSpecimen}
                onClick={() => onGenerateSpecimen('spliced-composite')}
                className="w-full text-left px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-[#172B47] hover:text-white transition-colors flex items-center gap-2 border border-slate-700/50"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                <span className="truncate">Specimen B: Spliced Composite</span>
              </button>
              <button
                disabled={isGeneratingSpecimen}
                onClick={() => onGenerateSpecimen('lossless-png')}
                className="w-full text-left px-2.5 py-1.5 rounded text-xs text-slate-300 hover:bg-[#172B47] hover:text-white transition-colors flex items-center gap-2 border border-slate-700/50"
              >
                <Sparkles className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                <span className="truncate">Specimen C: Lossless PNG</span>
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Institutional Footer */}
      <div className="p-3.5 border-t border-[#172B47] text-[11px] text-slate-400">
        <div className="font-semibold text-slate-200">Sure Clue Scientific Solutions</div>
        <div className="text-[10px] text-slate-500 mt-0.5">SEVA FIRST Innovation Challenge 2026</div>
      </div>
    </aside>
  );
};
