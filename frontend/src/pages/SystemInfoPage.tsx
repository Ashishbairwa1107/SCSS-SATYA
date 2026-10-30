import React, { useEffect, useState } from 'react';
import { Server, Shield, Cpu, HardDrive, CheckCircle2, AlertTriangle, Scale } from 'lucide-react';
import { api } from '../services/api';
import { SystemInfo } from '../types/api';
import { Alert } from '../components/common/Alert';

export const SystemInfoPage: React.FC = () => {
  const [info, setInfo] = useState<SystemInfo | null>(null);
  const [health, setHealth] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getSystemInfo(), api.getHealth()])
      .then(([infoData, healthData]) => {
        setInfo(infoData);
        setHealth(healthData);
      })
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading || !info) {
    return (
      <div className="p-8 text-center text-xs text-[#657187] dark:text-[#94A3B8]">
        Loading system specifications...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <Server className="w-5 h-5 text-[#C5A059]" />
          <h2 className="text-xl font-bold tracking-tight text-[#172033] dark:text-white">
            System Specifications & Forensic Environment
          </h2>
        </div>
        <p className="text-xs text-[#657187] dark:text-[#94A3B8] mt-1">
          Technical runtime parameters, security constraints, and institutional development metadata.
        </p>
      </div>

      {/* System Health Summary */}
      <div className="p-5 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-[#172033] dark:text-white">
              Screening Backend Operational
            </h3>
            <p className="text-xs text-[#657187] dark:text-[#94A3B8]">
              Database connected: {health?.database_connected ? 'True (SQLite)' : 'False'} | Vault accessible: {health?.vault_accessible ? 'True' : 'False'}
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
          {health?.status || 'HEALTHY'}
        </span>
      </div>

      {/* Technical Specifications Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        {/* Project Metadata */}
        <div className="p-5 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] space-y-2.5">
          <h4 className="font-bold text-xs uppercase tracking-wider text-[#0F1E36] dark:text-[#C5A059] flex items-center gap-2">
            <Shield className="w-4 h-4 text-[#C5A059]" />
            <span>Institutional Provenance</span>
          </h4>
          <div className="space-y-1.5 pt-1 text-[#657187] dark:text-[#94A3B8]">
            <div><b className="text-[#172033] dark:text-white">Application: </b>{info.full_title}</div>
            <div><b className="text-[#172033] dark:text-white">Version: </b>{info.version}</div>
            <div><b className="text-[#172033] dark:text-white">Organization: </b>{info.organization}</div>
            <div><b className="text-[#172033] dark:text-white">Challenge: </b>{info.challenge}</div>
            <div><b className="text-[#172033] dark:text-white">Sector: </b>{info.sector}</div>
            <div><b className="text-[#172033] dark:text-white">Sub-Theme: </b>{info.sub_theme}</div>
          </div>
        </div>

        {/* Runtime & Security Parameters */}
        <div className="p-5 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] space-y-2.5">
          <h4 className="font-bold text-xs uppercase tracking-wider text-[#0F1E36] dark:text-[#C5A059] flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-[#C5A059]" />
            <span>Runtime Constraints & Vault</span>
          </h4>
          <div className="space-y-1.5 pt-1 text-[#657187] dark:text-[#94A3B8]">
            <div><b className="text-[#172033] dark:text-white">Python Engine: </b>Python {info.python_version}</div>
            <div><b className="text-[#172033] dark:text-white">Storage Vault: </b>{info.storage_vault_path}</div>
            <div><b className="text-[#172033] dark:text-white">Max File Size: </b>{info.max_file_size_mb} MB per upload</div>
            <div><b className="text-[#172033] dark:text-white">Max Image Pixels: </b>{(info.max_pixels / 1000000).toFixed(0)} Megapixels (Decompression Bomb Protection)</div>
            <div><b className="text-[#172033] dark:text-white">Supported Formats: </b>{info.supported_formats.join(', ')}</div>
            <div><b className="text-[#172033] dark:text-white">Report Engines: </b>ReportLab (PDF, 2-Pass), JSON Schema v1.0.0</div>
          </div>
        </div>
      </div>

      {/* Statutory Disclaimers */}
      <div className="p-5 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] space-y-3 text-xs leading-relaxed">
        <h4 className="font-bold text-xs uppercase tracking-wider text-[#0F1E36] dark:text-[#C5A059] flex items-center gap-2">
          <Scale className="w-4 h-4 text-[#C5A059]" />
          <span>Statutory Disclaimers & Limitations</span>
        </h4>
        <p className="text-[#657187] dark:text-[#94A3B8]">
          {info.disclaimer}
        </p>
        <p className="text-[#657187] dark:text-[#94A3B8]">
          <b>Digital Evidence Framework:</b> Conforms to ISO/IEC 27037:2012 guidelines regarding non-destructive evidence acquisition and SHA-256 integrity verification. For judicial proceedings in India, certification under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 is required by the authorized electronic device custodian.
        </p>
      </div>
    </div>
  );
};
