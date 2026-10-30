import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  PlusCircle,
  FileSearch,
  CheckCircle2,
  AlertTriangle,
  Layers,
  ArrowRight,
  Sparkles,
  RefreshCw,
  FolderOpen,
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardMetrics, Examination } from '../types/api';
import { MetricCard } from '../components/common/MetricCard';
import { Badge } from '../components/common/Badge';
import { Alert } from '../components/common/Alert';

export const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentExams, setRecentExams] = useState<Examination[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingSpecimen, setIsGeneratingSpecimen] = useState(false);
  const navigate = useNavigate();

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [m, exams] = await Promise.all([
        api.getDashboardMetrics(),
        api.listExaminations({ limit: 8 }),
      ]);
      setMetrics(m);
      setRecentExams(exams);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleSpecimenTrigger = async (type: 'camera-style' | 'spliced-composite' | 'lossless-png') => {
    try {
      setIsGeneratingSpecimen(true);
      const res = await api.generateSpecimen(type);
      navigate(`/examinations/${res.id}`);
    } catch (err) {
      alert(`Specimen generation failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsGeneratingSpecimen(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Guiding Doctrine Callout Banner */}
      <div className="p-5 rounded-xl border border-[#C5A059]/40 bg-[#FAF7F0] dark:bg-[#172B47]/60 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 rounded-lg bg-[#0F1E36] text-[#C5A059] shrink-0 mt-0.5">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#C5A059]">
                Institutional Guiding Doctrine
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 font-semibold text-[10px]">
                Rule-Based Screening
              </span>
            </div>
            <h2 className="text-lg font-bold text-[#0F1E36] dark:text-white mt-0.5">
              "The tool screens. The expert decides."
            </h2>
            <p className="text-xs text-[#657187] dark:text-slate-300 max-w-3xl mt-1 leading-relaxed">
              SCSS SATYA conducts non-invasive passive screening across metadata, JPEG recompression residuals, and image geometry. It never computes arbitrary authenticity percentages. Technical observations assist qualified examiners in reaching legally defensible conclusions.
            </p>
          </div>
        </div>

        <Link
          to="/new"
          className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-[#0F1E36] hover:bg-[#172B47] text-white text-xs font-semibold shadow-xs border border-[#C5A059]/40 transition-colors shrink-0"
        >
          <PlusCircle className="w-4 h-4 text-[#C5A059]" />
          <span>New Examination</span>
        </Link>
      </div>

      {/* Database Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          label="Examinations"
          value={metrics?.total_examinations ?? 0}
          icon={<FileSearch className="w-4 h-4" />}
          variant="accent"
        />
        <MetricCard
          label="Evidence Items"
          value={metrics?.total_evidence_items ?? 0}
          icon={<FolderOpen className="w-4 h-4" />}
        />
        <MetricCard
          label="Total Cases"
          value={metrics?.total_cases ?? 0}
          icon={<Layers className="w-4 h-4" />}
        />
        <MetricCard
          label="Pending Review"
          value={metrics?.pending_human_reviews ?? 0}
          icon={<AlertTriangle className="w-4 h-4 text-amber-500" />}
          variant="warning"
        />
        <MetricCard
          label="Completed"
          value={metrics?.completed_examinations ?? 0}
          icon={<CheckCircle2 className="w-4 h-4 text-emerald-500" />}
        />
        <MetricCard
          label="Integrity Mismatch"
          value={metrics?.integrity_failures ?? 0}
          icon={<ShieldAlert className="w-4 h-4 text-rose-500" />}
          variant={metrics && metrics.integrity_failures > 0 ? 'alert' : 'default'}
        />
      </div>

      {/* Four-Layer Methodology Summary Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
        <div className="p-4 rounded-xl bg-white dark:bg-[#111C2E] border border-[#DCE2EA] dark:border-[#24344D]">
          <span className="font-bold text-[10px] uppercase tracking-wider text-[#C5A059] block">
            Layer 1
          </span>
          <h4 className="font-semibold text-sm text-[#172033] dark:text-white mt-1">
            Passive Screening
          </h4>
          <p className="text-[#657187] dark:text-[#94A3B8] mt-1 text-[11px] leading-relaxed">
            Non-destructive container EXIF inspection, JPEG Error Level Analysis (ELA), and radiometric RGB channel census.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-[#111C2E] border border-[#DCE2EA] dark:border-[#24344D]">
          <span className="font-bold text-[10px] uppercase tracking-wider text-[#C5A059] block">
            Layer 2
          </span>
          <h4 className="font-semibold text-sm text-[#172033] dark:text-white mt-1">
            Tamper-Evident SHA-256
          </h4>
          <p className="text-[#657187] dark:text-[#94A3B8] mt-1 text-[11px] leading-relaxed">
            Original evidence bytes preserved in storage vault. Cryptographic SHA-256 verification directly from stored bytes.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-[#111C2E] border border-[#DCE2EA] dark:border-[#24344D]">
          <span className="font-bold text-[10px] uppercase tracking-wider text-[#C5A059] block">
            Layer 3
          </span>
          <h4 className="font-semibold text-sm text-[#172033] dark:text-white mt-1">
            Explainable Findings
          </h4>
          <p className="text-[#657187] dark:text-[#94A3B8] mt-1 text-[11px] leading-relaxed">
            Deterministic status rules: No Indicator Detected, Indicator Observed, or Inconclusive with transparent limitations.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-[#111C2E] border border-[#DCE2EA] dark:border-[#24344D]">
          <span className="font-bold text-[10px] uppercase tracking-wider text-[#C5A059] block">
            Layer 4
          </span>
          <h4 className="font-semibold text-sm text-[#172033] dark:text-white mt-1">
            Qualified Human Review
          </h4>
          <p className="text-[#657187] dark:text-[#94A3B8] mt-1 text-[11px] leading-relaxed">
            ISO/IEC 27037 checklist verification, qualitative forensic notes, credential status, and examiner opinions.
          </p>
        </div>
      </div>

      {/* One-Click Calibrated Test Specimens Bar */}
      <div className="p-4 rounded-xl border border-slate-200 dark:border-[#24344D] bg-white dark:bg-[#111C2E] shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#C5A059]" />
              <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
                One-Click Calibrated Test Specimens
              </h3>
            </div>
            <p className="text-xs text-[#657187] dark:text-[#94A3B8]">
              Reproducible synthetic demonstration specimens designed to benchmark screening layers. Ground-truth recipes maintained separately.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            disabled={isGeneratingSpecimen}
            onClick={() => handleSpecimenTrigger('camera-style')}
            className="p-3 text-left rounded-lg border border-slate-200 dark:border-[#24344D] hover:border-[#C5A059] bg-[#F8FAFC] dark:bg-[#152238] transition-colors group"
          >
            <div className="font-semibold text-xs text-[#172033] dark:text-white flex items-center justify-between">
              <span>Specimen A: Camera Photo</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#C5A059] group-hover:translate-x-1 transition-transform" />
            </div>
            <p className="text-[11px] text-[#657187] dark:text-[#94A3B8] mt-1">
              Natural landscape with embedded synthetic EXIF tags and nominal ELA residuals.
            </p>
          </button>

          <button
            disabled={isGeneratingSpecimen}
            onClick={() => handleSpecimenTrigger('spliced-composite')}
            className="p-3 text-left rounded-lg border border-slate-200 dark:border-[#24344D] hover:border-[#C5A059] bg-[#F8FAFC] dark:bg-[#152238] transition-colors group"
          >
            <div className="font-semibold text-xs text-[#172033] dark:text-white flex items-center justify-between">
              <span>Specimen B: Spliced Composite</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#C5A059] group-hover:translate-x-1 transition-transform" />
            </div>
            <p className="text-[11px] text-[#657187] dark:text-[#94A3B8] mt-1">
              Structural composite with inserted foreign region, divergent ELA, and GIMP tag.
            </p>
          </button>

          <button
            disabled={isGeneratingSpecimen}
            onClick={() => handleSpecimenTrigger('lossless-png')}
            className="p-3 text-left rounded-lg border border-slate-200 dark:border-[#24344D] hover:border-[#C5A059] bg-[#F8FAFC] dark:bg-[#152238] transition-colors group"
          >
            <div className="font-semibold text-xs text-[#172033] dark:text-white flex items-center justify-between">
              <span>Specimen C: Lossless PNG</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#C5A059] group-hover:translate-x-1 transition-transform" />
            </div>
            <p className="text-[11px] text-[#657187] dark:text-[#94A3B8] mt-1">
              Lossless PNG calibration target demonstrating honest ELA unavailability.
            </p>
          </button>
        </div>
      </div>

      {/* Recent Examinations Table */}
      <div className="bg-white dark:bg-[#111C2E] rounded-xl border border-[#DCE2EA] dark:border-[#24344D] overflow-hidden shadow-xs">
        <div className="px-5 py-4 border-b border-[#DCE2EA] dark:border-[#24344D] flex items-center justify-between bg-[#F8FAFC] dark:bg-[#172B47]/50">
          <div>
            <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
              Recent Forensic Examinations
            </h3>
            <p className="text-xs text-[#657187] dark:text-[#94A3B8]">
              Live database case records and multi-layer screening outcomes.
            </p>
          </div>
          <button
            onClick={loadDashboardData}
            className="p-1.5 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] text-[#657187] hover:text-[#172033] dark:hover:text-white bg-white dark:bg-[#111C2E]"
            title="Refresh Dashboard"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-xs text-[#657187] dark:text-[#94A3B8]">
            Loading forensic records...
          </div>
        ) : recentExams.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FileSearch className="w-8 h-8 text-slate-400 mx-auto" />
            <h4 className="text-sm font-semibold text-[#172033] dark:text-white">
              No Evidence Registered Yet
            </h4>
            <p className="text-xs text-[#657187] dark:text-[#94A3B8] max-w-sm mx-auto">
              Register a new forensic image or click any demonstration specimen above to initiate screening.
            </p>
            <Link
              to="/new"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0F1E36] text-white text-xs font-semibold"
            >
              <PlusCircle className="w-4 h-4 text-[#C5A059]" />
              <span>Start First Examination</span>
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-[#DCE2EA] dark:border-[#24344D] text-[#657187] dark:text-[#94A3B8] bg-slate-50/50 dark:bg-slate-800/20">
                  <th className="px-5 py-3 font-semibold">Case Reference</th>
                  <th className="px-5 py-3 font-semibold">Evidence File</th>
                  <th className="px-5 py-3 font-semibold">Format</th>
                  <th className="px-5 py-3 font-semibold">SHA-256 Digest</th>
                  <th className="px-5 py-3 font-semibold">Screening Findings</th>
                  <th className="px-5 py-3 font-semibold">Human Review</th>
                  <th className="px-5 py-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {recentExams.map(ex => {
                  const summary = ex.findings_summary;
                  return (
                    <tr
                      key={ex.id}
                      className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      <td className="px-5 py-3.5 font-semibold text-[#0F1E36] dark:text-white">
                        <Link to={`/examinations/${ex.id}`} className="hover:underline">
                          {ex.case_reference || 'CAS-UNKNOWN'}
                        </Link>
                        <div className="text-[10px] text-[#657187] dark:text-[#94A3B8] font-normal truncate max-w-xs">
                          {ex.case_title}
                        </div>
                      </td>

                      <td className="px-5 py-3.5 font-mono text-[#172033] dark:text-slate-200 truncate max-w-[160px]">
                        {ex.original_filename}
                      </td>

                      <td className="px-5 py-3.5 font-semibold text-slate-700 dark:text-slate-300">
                        {ex.detected_format}
                      </td>

                      <td className="px-5 py-3.5 font-mono text-[10px] text-[#657187] dark:text-[#94A3B8]">
                        {ex.sha256_hash ? `${ex.sha256_hash.slice(0, 10)}...${ex.sha256_hash.slice(-6)}` : 'N/A'}
                      </td>

                      <td className="px-5 py-3.5">
                        {summary ? (
                          <div className="flex items-center gap-1.5 text-[10px]">
                            {summary.indicator_observed_count > 0 && (
                              <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-semibold">
                                {summary.indicator_observed_count} Anomaly
                              </span>
                            )}
                            {summary.no_indicator_count > 0 && (
                              <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                                {summary.no_indicator_count} Nominal
                              </span>
                            )}
                            {summary.inconclusive_count > 0 && (
                              <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                                {summary.inconclusive_count} Inconcl.
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-400">Processing...</span>
                        )}
                      </td>

                      <td className="px-5 py-3.5">
                        <Badge status={ex.review_status || 'Pending Review'} size="sm" />
                      </td>

                      <td className="px-5 py-3.5 text-right">
                        <Link
                          to={`/examinations/${ex.id}`}
                          className="inline-flex items-center gap-1 text-xs font-semibold text-[#0F1E36] dark:text-[#C5A059] hover:underline"
                        >
                          <span>Open Dossier</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
