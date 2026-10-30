import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileImage,
  CheckCircle,
  AlertCircle,
  Loader2,
  X,
  Shield,
  FileText,
  User,
  Info,
} from 'lucide-react';
import { api, ApiError } from '../services/api';
import { Alert } from '../components/common/Alert';

export const NewExaminationPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [imageMeta, setImageMeta] = useState<{ width: number; height: number } | null>(null);

  // Form Fields
  const [caseTitle, setCaseTitle] = useState('');
  const [caseReference, setCaseReference] = useState('');
  const [purpose, setPurpose] = useState('Digital image authenticity and integrity screening');
  const [evidenceSource, setEvidenceSource] = useState('Physical storage drive / Direct evidence upload');
  const [investigator, setInvestigator] = useState('Authorized Digital Forensic Examiner');
  const [notes, setNotes] = useState('');

  // Execution state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [errorDetail, setErrorDetail] = useState<string | null>(null);
  const [errorTroubleshoot, setErrorTroubleshoot] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileSelection = (selectedFile: File) => {
    setErrorMessage(null);
    setErrorDetail(null);
    setErrorTroubleshoot(null);

    // Validate size limit (50 MB)
    if (selectedFile.size > 50 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 50 MB screening limit.');
      return;
    }

    // Validate extension
    const allowed = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp', '.bmp'];
    const lowerName = selectedFile.name.toLowerCase();
    const hasValidExt = allowed.some(ext => lowerName.endsWith(ext));
    if (!hasValidExt) {
      setErrorMessage(`Unsupported format. Supported extensions: ${allowed.join(', ')}`);
      return;
    }

    setFile(selectedFile);
    if (!caseTitle) {
      setCaseTitle(`Examination of ${selectedFile.name}`);
    }

    // Generate local preview & measure dimensions
    const url = URL.createObjectURL(selectedFile);
    setPreviewUrl(url);

    const img = new Image();
    img.onload = () => {
      setImageMeta({ width: img.naturalWidth, height: img.naturalHeight });
    };
    img.src = url;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleClearFile = () => {
    setFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setImageMeta(null);
    setErrorMessage(null);
    setErrorDetail(null);
    setErrorTroubleshoot(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage('Please select or drop an evidence image file to proceed.');
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      setErrorDetail(null);
      setErrorTroubleshoot(null);

      const formData = new FormData();
      formData.append('file', file);
      if (caseTitle) formData.append('case_title', caseTitle);
      if (caseReference) formData.append('case_reference', caseReference);
      if (purpose) formData.append('purpose', purpose);
      if (evidenceSource) formData.append('evidence_source', evidenceSource);
      if (investigator) formData.append('investigator', investigator);
      if (notes) formData.append('notes', notes);

      const exam = await api.createExamination(formData);
      navigate(`/examinations/${exam.id}`);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
        if (err.isNetworkError) {
          setErrorTroubleshoot(
            'Ensure the backend server is running on http://127.0.0.1:8000. Start it with: backend\\.venv\\Scripts\\python.exe scripts\\run_backend.py (or run.bat)'
          );
        } else if (err.status) {
          setErrorDetail(err.detail ? `Backend response: ${err.detail}` : `HTTP Status: ${err.status} ${err.statusText}`);
        }
      } else {
        setErrorMessage(err instanceof Error ? err.message : String(err));
      }
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-[#172033] dark:text-white">
          New Forensic Evidence Examination
        </h2>
        <p className="text-xs text-[#657187] dark:text-[#94A3B8] mt-1">
          Ingest digital image evidence, calculate cryptographic SHA-256 ingestion hash, and initiate the multi-layer screening pipeline.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Case Metadata */}
        <div className="bg-white dark:bg-[#111C2E] p-6 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-[#DCE2EA] dark:border-[#24344D] pb-3">
            <FileText className="w-4 h-4 text-[#C5A059]" />
            <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
              Step 1 — Case Information & Context
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
                Case Title *
              </label>
              <input
                type="text"
                required
                value={caseTitle}
                onChange={e => setCaseTitle(e.target.value)}
                placeholder="e.g. Disputed Land Registry Stamp Analysis"
                className="w-full px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
              />
            </div>

            <div>
              <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
                Case Reference ID (Auto-generated if empty)
              </label>
              <input
                type="text"
                value={caseReference}
                onChange={e => setCaseReference(e.target.value)}
                placeholder="e.g. CAS-20261029-XXXX"
                className="w-full px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white font-mono"
              />
            </div>

            <div>
              <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
                Examination Purpose
              </label>
              <input
                type="text"
                value={purpose}
                onChange={e => setPurpose(e.target.value)}
                placeholder="e.g. Digital authenticity screening, recompression analysis"
                className="w-full px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
              />
            </div>

            <div>
              <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
                Evidence Source & Chain of Custody
              </label>
              <input
                type="text"
                value={evidenceSource}
                onChange={e => setEvidenceSource(e.target.value)}
                placeholder="e.g. SD Card acquisition by Inspector Sharma"
                className="w-full px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
              />
            </div>

            <div>
              <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
                Submitting Operator / Investigator
              </label>
              <input
                type="text"
                value={investigator}
                onChange={e => setInvestigator(e.target.value)}
                placeholder="e.g. Dr. A. Sen, Senior Forensic Analyst"
                className="w-full px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
              />
            </div>

            <div>
              <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
                Case Notes (Optional)
              </label>
              <input
                type="text"
                value={notes}
                onChange={e => setNotes(e.target.value)}
                placeholder="Non-sensitive case identifiers..."
                className="w-full px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
              />
            </div>
          </div>
        </div>

        {/* Step 2: Evidence Upload Zone */}
        <div className="bg-white dark:bg-[#111C2E] p-6 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-[#DCE2EA] dark:border-[#24344D] pb-3">
            <FileImage className="w-4 h-4 text-[#C5A059]" />
            <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
              Step 2 — Evidence File Registration
            </h3>
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={e => {
              if (e.target.files && e.target.files[0]) {
                handleFileSelection(e.target.files[0]);
              }
            }}
            accept=".jpg,.jpeg,.png,.tif,.tiff,.webp,.bmp"
            className="hidden"
          />

          {!file ? (
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`p-10 border-2 border-dashed rounded-xl text-center cursor-pointer transition-colors ${
                isDragOver
                  ? 'border-[#C5A059] bg-[#FAF7F0] dark:bg-[#172B47]'
                  : 'border-[#DCE2EA] dark:border-[#24344D] hover:border-[#C5A059] bg-[#F8FAFC] dark:bg-[#152238]'
              }`}
            >
              <UploadCloud className="w-10 h-10 text-[#C5A059] mx-auto mb-3" />
              <h4 className="text-sm font-bold text-[#172033] dark:text-white">
                Drag and drop original evidence image here
              </h4>
              <p className="text-xs text-[#657187] dark:text-[#94A3B8] mt-1">
                or click to browse local files (JPEG, PNG, TIFF, WEBP, BMP — up to 50 MB)
              </p>
              <div className="mt-3 inline-flex items-center gap-1.5 text-[10px] text-slate-500 font-mono">
                <Shield className="w-3 h-3 text-[#C5A059]" />
                <span>Pristine bytes preserved in isolated storage vault. Never overwritten.</span>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl border border-emerald-300 dark:border-emerald-800 bg-emerald-50/20 dark:bg-emerald-950/20 flex flex-col md:flex-row items-center gap-5">
              {previewUrl && (
                <div className="relative shrink-0">
                  <img
                    src={previewUrl}
                    alt="Evidence Preview"
                    className="w-32 h-32 object-cover rounded-lg border border-[#DCE2EA] dark:border-[#24344D] shadow-xs"
                  />
                  <button
                    type="button"
                    onClick={handleClearFile}
                    className="absolute -top-2 -right-2 p-1 rounded-full bg-rose-600 text-white shadow-xs hover:bg-rose-700"
                    title="Remove File"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              <div className="flex-1 space-y-1.5 text-xs">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                  <span className="font-bold text-sm text-[#172033] dark:text-white">
                    {file.name}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-600 dark:text-slate-300 font-mono text-[11px] pt-1">
                  <div>
                    <span className="text-[#657187] dark:text-[#94A3B8]">Size: </span>
                    {(file.size / 1024).toFixed(1)} KB ({file.size.toLocaleString()} bytes)
                  </div>
                  <div>
                    <span className="text-[#657187] dark:text-[#94A3B8]">MIME: </span>
                    {file.type || 'image/jpeg'}
                  </div>
                  {imageMeta && (
                    <>
                      <div>
                        <span className="text-[#657187] dark:text-[#94A3B8]">Dimensions: </span>
                        {imageMeta.width} × {imageMeta.height} px
                      </div>
                      <div>
                        <span className="text-[#657187] dark:text-[#94A3B8]">Megapixels: </span>
                        {((imageMeta.width * imageMeta.height) / 1000000).toFixed(2)} MP
                      </div>
                    </>
                  )}
                </div>
                <p className="text-[10px] text-emerald-700 dark:text-emerald-300 italic pt-1">
                  Ready for cryptographic SHA-256 ingestion hashing and multi-layer passive screening.
                </p>
              </div>
            </div>
          )}
        </div>

        {errorMessage && (
          <Alert variant="error" title="Ingestion Validation Alert">
            <div className="space-y-2">
              <p className="font-semibold">{errorMessage}</p>
              {errorDetail && (
                <div className="text-[11px] font-mono bg-rose-100/70 dark:bg-rose-950/40 text-rose-900 dark:text-rose-200 p-2.5 rounded border border-rose-200 dark:border-rose-900/50">
                  {errorDetail}
                </div>
              )}
              {errorTroubleshoot && (
                <div className="text-[11px] bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 p-2.5 rounded border border-amber-200 dark:border-amber-900/50 space-y-1">
                  <span className="font-bold block uppercase tracking-wider text-[10px]">
                    Backend Connection Troubleshooting:
                  </span>
                  <span>{errorTroubleshoot}</span>
                </div>
              )}
            </div>
          </Alert>
        )}

        {/* Action Button */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-4 py-2 text-xs font-semibold rounded-lg border border-[#DCE2EA] dark:border-[#24344D] text-[#657187] hover:text-[#172033] dark:hover:text-white"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={!file || isSubmitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-[#0F1E36] hover:bg-[#172B47] text-white text-xs font-semibold shadow-xs border border-[#C5A059]/40 disabled:opacity-50 transition-colors"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-[#C5A059]" />
                <span>Hashing & Screening Evidence...</span>
              </>
            ) : (
              <>
                <Shield className="w-4 h-4 text-[#C5A059]" />
                <span>Register & Run Screening Pipeline</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
