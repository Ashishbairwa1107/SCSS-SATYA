import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Archive,
  Search,
  RefreshCw,
  Download,
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
  SlidersHorizontal,
  FileText,
} from 'lucide-react';
import { api } from '../services/api';
import { Examination } from '../types/api';
import { Badge } from '../components/common/Badge';

export const EvidenceVaultPage: React.FC = () => {
  const [examinations, setExaminations] = useState<Examination[]>([]);
  const [search, setSearch] = useState('');
  const [formatFilter, setFormatFilter] = useState('');
  const [reviewStatusFilter, setReviewStatusFilter] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [verifyingId, setVerifyingId] = useState<string | null>(null);

  const loadVaultData = async () => {
    try {
      setIsLoading(true);
      const data = await api.listExaminations({
        search: search || undefined,
        format_filter: formatFilter || undefined,
        review_status: reviewStatusFilter || undefined,
        limit: 100,
      });
      setExaminations(data);
    } catch (err) {
      console.error('Failed to load evidence vault data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadVaultData();
  }, [formatFilter, reviewStatusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadVaultData();
  };

  const handleVerify = async (evidenceId: string) => {
    try {
      setVerifyingId(evidenceId);
      const res = await api.verifyEvidence(evidenceId);
      // update state
      setExaminations(prev =>
        prev.map(ex =>
          ex.evidence_id === evidenceId ? { ...ex, integrity_status: res.status } : ex
        )
      );
      alert(`Evidence integrity verification: ${res.status}\n${res.message}`);
    } catch (err) {
      alert(`Verification failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setVerifyingId(null);
    }
  };

  const handleQuickReport = async (examinationId: string) => {
    try {
      const rep = await api.generateReport(examinationId, 'PDF');
      const link = document.createElement('a');
      link.href = rep.download_url;
      link.setAttribute('download', `Satya_Report_${examinationId}.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert(`Report generation failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Archive className="w-5 h-5 text-[#C5A059]" />
            <h2 className="text-xl font-bold tracking-tight text-[#172033] dark:text-white">
              Evidence Vault & Case History
            </h2>
          </div>
          <p className="text-xs text-[#657187] dark:text-[#94A3B8] mt-1">
            Protected repository of ingested evidence items, verified SHA-256 hashes, and examination records.
          </p>
        </div>

        <button
          onClick={loadVaultData}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-xs font-semibold text-[#172033] dark:text-white hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shrink-0"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Vault</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white dark:bg-[#111C2E] p-4 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] shadow-xs space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-[#657187] absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by case reference, title, filename, or SHA-256..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white focus:outline-hidden focus:border-[#C5A059]"
            />
          </div>

          <div className="flex items-center gap-2 w-full md:w-auto">
            <select
              value={formatFilter}
              onChange={e => setFormatFilter(e.target.value)}
              className="px-3 py-2 text-xs rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
            >
              <option value="">All Formats</option>
              <option value="JPEG">JPEG / JPG</option>
              <option value="PNG">PNG</option>
              <option value="TIFF">TIFF</option>
              <option value="WEBP">WEBP</option>
              <option value="BMP">BMP</option>
            </select>

            <select
              value={reviewStatusFilter}
              onChange={e => setReviewStatusFilter(e.target.value)}
              className="px-3 py-2 text-xs rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
            >
              <option value="">All Review Statuses</option>
              <option value="Pending Review">Pending Review</option>
              <option value="Under Review">Under Review</option>
              <option value="Reviewed — No Final Opinion">Reviewed — No Final Opinion</option>
              <option value="Examiner Opinion Recorded">Examiner Opinion Recorded</option>
            </select>

            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-[#0F1E36] text-white text-xs font-semibold hover:bg-[#172B47] transition-colors"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Vault Table */}
      <div className="bg-white dark:bg-[#111C2E] rounded-xl border border-[#DCE2EA] dark:border-[#24344D] overflow-hidden shadow-xs">
        {isLoading ? (
          <div className="p-8 text-center text-xs text-[#657187] dark:text-[#94A3B8]">
            Searching evidence repository...
          </div>
        ) : examinations.length === 0 ? (
          <div className="p-12 text-center text-xs text-[#657187] dark:text-[#94A3B8]">
            No evidence records matched your search parameters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-[#DCE2EA] dark:border-[#24344D] text-[#657187] dark:text-[#94A3B8] bg-slate-50/50 dark:bg-slate-800/20">
                  <th className="px-5 py-3 font-semibold">Case Reference</th>
                  <th className="px-5 py-3 font-semibold">Evidence Filename</th>
                  <th className="px-5 py-3 font-semibold">Format</th>
                  <th className="px-5 py-3 font-semibold">SHA-256 Hash</th>
                  <th className="px-5 py-3 font-semibold">Integrity Status</th>
                  <th className="px-5 py-3 font-semibold">Human Review</th>
                  <th className="px-5 py-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {examinations.map(ex => (
                  <tr
                    key={ex.id}
                    className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="px-5 py-3.5 font-semibold text-[#0F1E36] dark:text-white">
                      <Link to={`/examinations/${ex.id}`} className="hover:underline">
                        {ex.case_reference || 'CAS-UNASSIGNED'}
                      </Link>
                      <div className="text-[10px] text-[#657187] dark:text-[#94A3B8] font-normal truncate max-w-xs">
                        {ex.case_title}
                      </div>
                    </td>

                    <td className="px-5 py-3.5 font-mono text-[#172033] dark:text-slate-200">
                      {ex.original_filename}
                    </td>

                    <td className="px-5 py-3.5 font-semibold text-slate-700 dark:text-slate-300">
                      {ex.detected_format}
                    </td>

                    <td className="px-5 py-3.5 font-mono text-[10px] text-[#657187] dark:text-[#94A3B8]">
                      {ex.sha256_hash ? `${ex.sha256_hash.slice(0, 10)}...${ex.sha256_hash.slice(-6)}` : 'N/A'}
                    </td>

                    <td className="px-5 py-3.5">
                      <Badge status={ex.integrity_status || 'VERIFIED'} size="sm" />
                    </td>

                    <td className="px-5 py-3.5">
                      <Badge status={ex.review_status || 'Pending Review'} size="sm" />
                    </td>

                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleVerify(ex.evidence_id)}
                          disabled={verifyingId === ex.evidence_id}
                          className="p-1 rounded text-[#657187] hover:text-[#0F1E36] dark:hover:text-white"
                          title="Re-verify SHA-256 against stored vault bytes"
                        >
                          <RefreshCw className={`w-3.5 h-3.5 text-[#C5A059] ${verifyingId === ex.evidence_id ? 'animate-spin' : ''}`} />
                        </button>

                        <a
                          href={api.getOriginalEvidenceUrl(ex.evidence_id)}
                          download={ex.original_filename}
                          className="p-1 rounded text-[#657187] hover:text-[#0F1E36] dark:hover:text-white"
                          title="Download pristine evidence bytes"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </a>

                        <button
                          onClick={() => handleQuickReport(ex.id)}
                          className="p-1 rounded text-[#657187] hover:text-[#0F1E36] dark:hover:text-white"
                          title="Generate & download official PDF report"
                        >
                          <FileText className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                        </button>

                        <Link
                          to={`/examinations/${ex.id}`}
                          className="inline-flex items-center gap-1 font-semibold text-[#0F1E36] dark:text-[#C5A059] hover:underline ml-1"
                        >
                          <span>Dossier</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
