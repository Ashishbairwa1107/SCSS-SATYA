import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ShieldCheck,
  ShieldAlert,
  FileText,
  Layers,
  FileCode,
  Download,
  RefreshCw,
  Clock,
  Eye,
  CheckCircle,
  AlertTriangle,
  HelpCircle,
  UserCheck,
  Copy,
  ExternalLink,
  History,
} from 'lucide-react';
import { api } from '../services/api';
import {
  ExaminationDetail,
  ELAResponse,
  ImageStatisticsResponse,
  MetadataResponse,
  ExaminerReview,
  GeneratedReport,
} from '../types/api';
import { Badge } from '../components/common/Badge';
import { Alert } from '../components/common/Alert';
import { ImageCompareViewer } from '../components/exhibits/ImageCompareViewer';
import { RGBDistributionChart } from '../components/exhibits/RGBDistributionChart';
import { MetadataTable } from '../components/exhibits/MetadataTable';
import { FindingCard } from '../components/findings/FindingCard';
import { HumanReviewPanel } from '../components/findings/HumanReviewPanel';

export const ExaminationDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [exam, setExam] = useState<ExaminationDetail | null>(null);
  const [ela, setEla] = useState<ELAResponse | null>(null);
  const [stats, setStats] = useState<ImageStatisticsResponse | null>(null);
  const [metadata, setMetadata] = useState<MetadataResponse | null>(null);
  const [reports, setReports] = useState<GeneratedReport[]>([]);

  const [activeTab, setActiveTab] = useState<'visual' | 'findings' | 'metadata' | 'review' | 'integrity'>('visual');
  const [isLoading, setIsLoading] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState(false);
  const [integrityAlert, setIntegrityAlert] = useState<{ match: boolean; message: string } | null>(null);

  const loadAllData = async (examId: string) => {
    try {
      setIsLoading(true);
      const detail = await api.getExaminationDetail(examId);
      setExam(detail);

      // Load parallel components
      const [elaData, statsData, metaData, reportsData] = await Promise.all([
        api.getELAAnalysis(examId).catch(() => null),
        api.getImageStatistics(examId).catch(() => null),
        api.getEvidenceMetadata(detail.evidence_id).catch(() => null),
        api.listReports(examId).catch(() => []),
      ]);

      setEla(elaData);
      setStats(statsData);
      setMetadata(metaData);
      setReports(reportsData);
    } catch (err) {
      console.error('Failed to load examination detail:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      loadAllData(id);
    }
  }, [id]);

  const handleVerifyIntegrity = async () => {
    if (!exam) return;
    try {
      setIsVerifying(true);
      setIntegrityAlert(null);
      const res = await api.verifyEvidence(exam.evidence_id);
      const isMatch = res.status === 'VERIFIED';
      setIntegrityAlert({ match: isMatch, message: res.message });
      // Update local state
      setExam(prev => (prev ? { ...prev, evidence: { ...prev.evidence, integrity_status: res.status } } : null));
    } catch (err) {
      setIntegrityAlert({
        match: false,
        message: `Verification failed: ${err instanceof Error ? err.message : String(err)}`,
      });
    } finally {
      setIsVerifying(false);
    }
  };

  const handleCopyHash = () => {
    if (!exam?.evidence.sha256_hash) return;
    navigator.clipboard.writeText(exam.evidence.sha256_hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const handleGenerateReport = async (format: 'PDF' | 'JSON') => {
    if (!exam) return;
    try {
      setIsGeneratingReport(format);
      const rep = await api.generateReport(exam.id, format);
      setReports(prev => [rep, ...prev]);
      // Trigger programmatic download
      const link = document.createElement('a');
      link.href = rep.download_url;
      link.setAttribute('download', `Satya_Report_${exam.id}.${format.toLowerCase()}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert(`Report generation failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsGeneratingReport(null);
    }
  };

  if (isLoading || !exam) {
    return (
      <div className="p-12 text-center text-xs text-[#657187] dark:text-[#94A3B8]">
        Loading forensic examination dossier...
      </div>
    );
  }

  const { case: caseData, evidence, findings, findings_summary } = exam;

  return (
    <div className="space-y-6">
      {/* Dossier Header Box */}
      <div className="bg-white dark:bg-[#111C2E] rounded-xl border border-[#DCE2EA] dark:border-[#24344D] p-6 shadow-xs space-y-5">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#C5A059] bg-[#C5A059]/10 px-2 py-0.5 rounded border border-[#C5A059]/30">
                Case Dossier
              </span>
              <span className="text-xs font-mono text-[#657187] dark:text-[#94A3B8]">
                {caseData.case_reference}
              </span>
              <Badge status={exam.status} size="sm" />
            </div>

            <h1 className="text-xl font-bold text-[#172033] dark:text-white mt-1.5">
              {caseData.title}
            </h1>
            <p className="text-xs text-[#657187] dark:text-[#94A3B8] mt-0.5">
              Purpose: {caseData.purpose || 'Digital image authenticity screening'} | Investigator: {caseData.investigator || 'Authorized Examiner'}
            </p>
          </div>

          {/* Action CTAs: Report Generation */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => handleGenerateReport('PDF')}
              disabled={Boolean(isGeneratingReport)}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#0F1E36] hover:bg-[#172B47] text-white text-xs font-semibold shadow-xs border border-[#C5A059]/40 transition-colors disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5 text-[#C5A059]" />
              <span>{isGeneratingReport === 'PDF' ? 'Building PDF...' : 'Download PDF Report'}</span>
            </button>

            <button
              onClick={() => handleGenerateReport('JSON')}
              disabled={Boolean(isGeneratingReport)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] hover:text-[#172033] dark:hover:text-white text-xs font-semibold text-[#657187] transition-colors disabled:opacity-50"
            >
              <FileCode className="w-3.5 h-3.5 text-[#C5A059]" />
              <span>{isGeneratingReport === 'JSON' ? 'Generating...' : 'JSON'}</span>
            </button>
          </div>
        </div>

        {/* Cryptographic Evidence Preservation Strip */}
        <div className="p-4 rounded-lg bg-[#F8FAFC] dark:bg-[#172B47]/40 border border-[#DCE2EA] dark:border-[#24344D] flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-[#172033] dark:text-white">
                Original Evidence File:
              </span>
              <span className="font-mono text-slate-700 dark:text-slate-300">
                {evidence.original_filename}
              </span>
              <span className="text-[#657187] dark:text-[#94A3B8]">
                ({evidence.detected_format}, {evidence.width} × {evidence.height} px, {(evidence.file_size_bytes / 1024).toFixed(1)} KB)
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="font-semibold text-[#172033] dark:text-white">
                SHA-256 Digest:
              </span>
              <span className="font-mono text-[11px] text-[#0F1E36] dark:text-[#C5A059] bg-white dark:bg-[#111C2E] px-2 py-0.5 rounded border border-[#DCE2EA] dark:border-[#24344D]">
                {evidence.sha256_hash}
              </span>
              <button
                onClick={handleCopyHash}
                className="text-[#657187] hover:text-[#172033] dark:hover:text-white"
                title="Copy SHA-256 Hash"
              >
                <Copy className="w-3.5 h-3.5" />
              </button>
              {copiedHash && (
                <span className="text-[10px] text-emerald-600 font-semibold">Copied!</span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <Badge status={evidence.integrity_status || 'VERIFIED'} />
            <button
              onClick={handleVerifyIntegrity}
              disabled={isVerifying}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-xs font-semibold text-[#172033] dark:text-white hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors disabled:opacity-50"
              title="Re-read stored bytes from vault and re-hash"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-[#C5A059] ${isVerifying ? 'animate-spin' : ''}`} />
              <span>{isVerifying ? 'Verifying...' : 'Re-Verify Bytes'}</span>
            </button>
          </div>
        </div>

        {integrityAlert && (
          <Alert
            variant={integrityAlert.match ? 'success' : 'error'}
            title={integrityAlert.match ? 'Layer 2 Integrity Verified' : 'CRITICAL INTEGRITY FAILURE'}
          >
            {integrityAlert.message}
          </Alert>
        )}
      </div>

      {/* Primary Technical Limitation Banner */}
      <Alert variant="doctrine" title="Scientific Screening Boundary">
        These findings represent technical screening observations. The absence of detected indicators does not establish authenticity, and observed anomalies may have legitimate explanations. SCSS SATYA is a screening aid; the qualified human forensic expert decides.
      </Alert>

      {/* Dossier Tabs */}
      <div className="border-b border-[#DCE2EA] dark:border-[#24344D] flex items-center gap-2 overflow-x-auto text-xs">
        <button
          onClick={() => setActiveTab('visual')}
          className={`flex items-center gap-2 px-4 py-3 font-semibold border-b-2 transition-colors shrink-0 ${
            activeTab === 'visual'
              ? 'border-[#C5A059] text-[#0F1E36] dark:text-[#C5A059]'
              : 'border-transparent text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white'
          }`}
        >
          <Eye className="w-4 h-4" />
          <span>Visual Lab & ELA Exhibits</span>
        </button>

        <button
          onClick={() => setActiveTab('findings')}
          className={`flex items-center gap-2 px-4 py-3 font-semibold border-b-2 transition-colors shrink-0 ${
            activeTab === 'findings'
              ? 'border-[#C5A059] text-[#0F1E36] dark:text-[#C5A059]'
              : 'border-transparent text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          <span>Explainable Findings ({findings.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('metadata')}
          className={`flex items-center gap-2 px-4 py-3 font-semibold border-b-2 transition-colors shrink-0 ${
            activeTab === 'metadata'
              ? 'border-[#C5A059] text-[#0F1E36] dark:text-[#C5A059]'
              : 'border-transparent text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Container EXIF Metadata</span>
        </button>

        <button
          onClick={() => setActiveTab('review')}
          className={`flex items-center gap-2 px-4 py-3 font-semibold border-b-2 transition-colors shrink-0 ${
            activeTab === 'review'
              ? 'border-[#C5A059] text-[#0F1E36] dark:text-[#C5A059]'
              : 'border-transparent text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white'
          }`}
        >
          <UserCheck className="w-4 h-4" />
          <span>Qualified Human Review</span>
        </button>

        <button
          onClick={() => setActiveTab('integrity')}
          className={`flex items-center gap-2 px-4 py-3 font-semibold border-b-2 transition-colors shrink-0 ${
            activeTab === 'integrity'
              ? 'border-[#C5A059] text-[#0F1E36] dark:text-[#C5A059]'
              : 'border-transparent text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white'
          }`}
        >
          <History className="w-4 h-4" />
          <span>Chain of Custody & Reports ({reports.length})</span>
        </button>
      </div>

      {/* Tab 1: Visual Lab & ELA */}
      {activeTab === 'visual' && (
        <div className="space-y-6">
          <ImageCompareViewer evidence={evidence} ela={ela} />
          <RGBDistributionChart stats={stats} />
        </div>
      )}

      {/* Tab 2: Explainable Findings */}
      {activeTab === 'findings' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3.5 rounded-lg border border-emerald-200 dark:border-emerald-800 bg-emerald-50/30 dark:bg-emerald-950/20 text-xs">
              <span className="font-semibold text-emerald-800 dark:text-emerald-300 block">
                No Indicator Detected
              </span>
              <span className="text-xl font-bold font-mono text-emerald-900 dark:text-emerald-200 block mt-1">
                {findings_summary.no_indicator_count}
              </span>
              <p className="text-[10px] text-emerald-700 dark:text-emerald-400 mt-0.5">
                Nominal values within expected parameter envelopes.
              </p>
            </div>

            <div className="p-3.5 rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50/30 dark:bg-amber-950/20 text-xs">
              <span className="font-semibold text-amber-800 dark:text-amber-300 block">
                Indicator Observed
              </span>
              <span className="text-xl font-bold font-mono text-amber-900 dark:text-amber-200 block mt-1">
                {findings_summary.indicator_observed_count}
              </span>
              <p className="text-[10px] text-amber-700 dark:text-amber-400 mt-0.5">
                Empirical residual or metadata anomaly detected.
              </p>
            </div>

            <div className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30 text-xs">
              <span className="font-semibold text-slate-700 dark:text-slate-300 block">
                Inconclusive
              </span>
              <span className="text-xl font-bold font-mono text-slate-800 dark:text-slate-200 block mt-1">
                {findings_summary.inconclusive_count}
              </span>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">
                Missing headers or unsupported format prevent automated test.
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {findings.map(f => (
              <FindingCard key={f.id} finding={f} />
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Container Metadata */}
      {activeTab === 'metadata' && (
        <MetadataTable metadata={metadata} />
      )}

      {/* Tab 4: Qualified Human Review */}
      {activeTab === 'review' && (
        <HumanReviewPanel
          examinationId={exam.id}
          initialReview={exam.review}
          onReviewUpdated={updated => {
            setExam(prev => (prev ? { ...prev, review: updated } : null));
          }}
        />
      )}

      {/* Tab 5: Chain of Custody & Reports */}
      {activeTab === 'integrity' && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-[#111C2E] p-6 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] shadow-xs space-y-4 text-xs">
            <h3 className="text-sm font-semibold text-[#172033] dark:text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#C5A059]" />
              <span>Evidence Vault Preservation Record (ISO/IEC 27037:2012)</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div>
                  <span className="font-semibold text-[#657187] dark:text-[#94A3B8] block">
                    Vault Storage Filename:
                  </span>
                  <span className="font-mono text-[#172033] dark:text-white">
                    {evidence.stored_filename}
                  </span>
                </div>
                <div>
                  <span className="font-semibold text-[#657187] dark:text-[#94A3B8] block">
                    Ingestion Timestamp (UTC):
                  </span>
                  <span className="font-mono text-[#172033] dark:text-white">
                    {evidence.ingestion_timestamp}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <div>
                  <span className="font-semibold text-[#657187] dark:text-[#94A3B8] block">
                    Verified Ingestion Digest:
                  </span>
                  <span className="font-mono text-[#0F1E36] dark:text-[#C5A059] font-bold">
                    {evidence.sha256_hash}
                  </span>
                </div>
                <div>
                  <span className="font-semibold text-[#657187] dark:text-[#94A3B8] block">
                    Storage Architecture:
                  </span>
                  <span>
                    Randomized UUID naming with protected isolated filesystem vault. Unaltered original bytes.
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Generated Reports List */}
          <div className="bg-white dark:bg-[#111C2E] rounded-xl border border-[#DCE2EA] dark:border-[#24344D] overflow-hidden shadow-xs">
            <div className="px-5 py-4 border-b border-[#DCE2EA] dark:border-[#24344D] bg-[#F8FAFC] dark:bg-[#172B47]/50 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
                  Generated Forensic Reports Archive
                </h3>
                <p className="text-xs text-[#657187] dark:text-[#94A3B8]">
                  Exported laboratory reports with independent cryptographic hashes.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleGenerateReport('PDF')}
                  className="px-3 py-1.5 rounded-lg bg-[#0F1E36] text-white text-xs font-semibold"
                >
                  + Generate PDF
                </button>
                <button
                  onClick={() => handleGenerateReport('JSON')}
                  className="px-3 py-1.5 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] text-xs font-semibold"
                >
                  + Generate JSON
                </button>
              </div>
            </div>

            {reports.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#657187] dark:text-[#94A3B8]">
                No reports generated yet for this examination. Click "+ Generate PDF" above.
              </div>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
                {reports.map(r => (
                  <div key={r.id} className="p-4 flex flex-wrap items-center justify-between gap-3">
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2 font-semibold text-[#172033] dark:text-white">
                        <span className="px-2 py-0.5 rounded bg-[#C5A059]/20 text-[#C5A059] font-mono text-[10px]">
                          {r.report_format}
                        </span>
                        <span>Official Laboratory Report</span>
                      </div>
                      <div className="font-mono text-[10px] text-[#657187] dark:text-[#94A3B8]">
                        SHA-256: {r.sha256_hash} | {(r.file_size_bytes / 1024).toFixed(1)} KB | {r.generated_at}
                      </div>
                    </div>

                    <a
                      href={r.download_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-xs font-semibold text-[#0F1E36] dark:text-[#C5A059] hover:underline"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download {r.report_format}</span>
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
