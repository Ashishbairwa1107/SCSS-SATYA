import React from 'react';
import { BookOpen, ShieldCheck, Scale, Cpu, FileSpreadsheet, AlertTriangle, Layers } from 'lucide-react';
import { Alert } from '../components/common/Alert';

export const MethodologyPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-[#C5A059]" />
          <h2 className="text-xl font-bold tracking-tight text-[#172033] dark:text-white">
            Forensic Screening Methodology & Institutional Doctrine
          </h2>
        </div>
        <p className="text-xs text-[#657187] dark:text-[#94A3B8] mt-1">
          Technical specifications, mathematical principles, and statutory boundaries of SCSS SATYA.
        </p>
      </div>

      {/* Doctrine Banner */}
      <Alert variant="doctrine" title="Core Operating Principle">
        <b>"The tool screens. The expert decides."</b><br />
        SCSS SATYA is an institutional forensic screening and documentation prototype, not an accredited testing instrument. It implements transparent, explainable, rule-based heuristics rather than black-box probability scores.
      </Alert>

      {/* Layer 1: Passive Screening */}
      <div className="bg-white dark:bg-[#111C2E] p-6 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] shadow-xs space-y-4 text-xs leading-relaxed">
        <div className="flex items-center gap-2 border-b border-[#DCE2EA] dark:border-[#24344D] pb-3">
          <Layers className="w-4 h-4 text-[#C5A059]" />
          <h3 className="text-sm font-bold text-[#172033] dark:text-white">
            Layer 1 — Passive, Non-Invasive Image Screening
          </h3>
        </div>

        <div className="space-y-3 text-[#172033] dark:text-slate-300">
          <h4 className="font-bold text-xs text-[#0F1E36] dark:text-[#C5A059]">
            A. Ingestion & Resource Protection
          </h4>
          <p>
            Evidence files are ingested through a strict validation gateway. MIME signatures and file magic bytes are verified independently of client-provided headers. To protect forensic workstations from decompression bombs and resource starvation attacks, decoding enforces a hard ceiling of 100,000,000 pixels (100 Megapixels) and 50 MB byte payload.
          </p>

          <h4 className="font-bold text-xs text-[#0F1E36] dark:text-[#C5A059]">
            B. EXIF / IPTC / TIFF Metadata Inspection
          </h4>
          <p>
            Metadata fields are extracted and categorized into Hardware Provenance, Chronological Timestamps, Software Traces, Optical Parameters, and Geolocation. For every tag, the system distinguishes between <b>Present</b>, <b>Missing</b>, <b>Unreadable</b>, and <b>Unsupported</b>.
          </p>
          <div className="p-3 rounded-lg bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/50 text-[11px] text-amber-900 dark:text-amber-200">
            <b>Critical Forensic Principle:</b> Metadata can be stripped by messaging apps, social platforms, and privacy scrubbing tools. Missing EXIF must never be treated as an indicator of manipulation. Software tags (e.g., Adobe Photoshop, GIMP) are logged as technical observations, not proof of tampering.
          </div>

          <h4 className="font-bold text-xs text-[#0F1E36] dark:text-[#C5A059]">
            C. JPEG Error Level Analysis (ELA)
          </h4>
          <p>
            For JPEG files, Error Level Analysis is performed by re-encoding a working copy in memory at Quality=90, computing the absolute pixel difference <code className="font-mono bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">|original - recompressed|</code>, and amplifying residuals by a factor of 15. The residual is rendered as both an amplified grayscale exhibit and a thermal Inferno heatmap.
          </p>
          <p>
            <b>Lossless Rejection:</b> ELA relies on 8×8 Discrete Cosine Transform (DCT) lossy quantization variance. Applying JPEG ELA to lossless PNG or TIFF images is scientifically invalid. The platform explicitly marks lossless files as Inconclusive for ELA with transparent documentation.
          </p>

          <h4 className="font-bold text-xs text-[#0F1E36] dark:text-[#C5A059]">
            D. Color Radiometry & Spatial Noise Statistics
          </h4>
          <p>
            Deterministic measurements across all image pixels calculate channel means, standard deviations, dynamic range, and a 32-bin intensity histogram. Spatial sharpness and focus depth are measured using Laplacian variance, while high-frequency noise is estimated using median-filter residuals.
          </p>
        </div>
      </div>

      {/* Layer 2: Evidence Integrity */}
      <div className="bg-white dark:bg-[#111C2E] p-6 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] shadow-xs space-y-4 text-xs leading-relaxed">
        <div className="flex items-center gap-2 border-b border-[#DCE2EA] dark:border-[#24344D] pb-3">
          <ShieldCheck className="w-4 h-4 text-[#C5A059]" />
          <h3 className="text-sm font-bold text-[#172033] dark:text-white">
            Layer 2 — Tamper-Evident Evidence Integrity Record
          </h3>
        </div>

        <div className="space-y-3 text-[#172033] dark:text-slate-300">
          <p>
            The SHA-256 cryptographic digest is calculated <b>strictly from original uploaded file bytes</b> prior to any decoding or preview generation. The original evidence bytes are written into an isolated storage vault under non-overwriting randomized filenames.
          </p>
          <p>
            The <b>Integrity Verification Endpoint</b> re-reads the stored bytes directly from disk and recomputes the SHA-256 hash. Any byte-level alteration (whether from bit rot or unauthorized disk modification) produces an immediate <b>MISMATCH</b> alert.
          </p>
          <div className="p-3 rounded-lg bg-blue-50/50 dark:bg-blue-950/20 border border-blue-200/50 text-[11px] text-blue-900 dark:text-blue-200">
            <b>Integrity vs Authenticity:</b> A matching SHA-256 digest proves byte consistency against the recorded ingestion reference. It does not prove that the depicted scene is real or unaltered prior to acquisition.
          </div>
        </div>
      </div>

      {/* Layer 3: Explainable Findings */}
      <div className="bg-white dark:bg-[#111C2E] p-6 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] shadow-xs space-y-4 text-xs leading-relaxed">
        <div className="flex items-center gap-2 border-b border-[#DCE2EA] dark:border-[#24344D] pb-3">
          <Cpu className="w-4 h-4 text-[#C5A059]" />
          <h3 className="text-sm font-bold text-[#172033] dark:text-white">
            Layer 3 — Explainable Technical Findings Engine
          </h3>
        </div>

        <div className="space-y-3 text-[#172033] dark:text-slate-300">
          <p>
            Every finding strictly conforms to one of three primary statuses:
          </p>
          <ul className="list-disc list-inside space-y-1 pl-2">
            <li><b>No Indicator Detected:</b> Nominal measurements within standard photographic baselines.</li>
            <li><b>Indicator Observed:</b> Empirical anomaly, software signature, or recompression divergence observed.</li>
            <li><b>Inconclusive:</b> Container metadata absent, or file format unsupported for specific test.</li>
          </ul>
          <p>
            Each finding provides the observed measurement, technical explanation, forensic significance, known limitations, and recommended manual verification steps. Global percentage scores (such as "98% fake") are strictly prohibited.
          </p>
        </div>
      </div>

      {/* Layer 4: Qualified Human Review & Legal Context */}
      <div className="bg-white dark:bg-[#111C2E] p-6 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] shadow-xs space-y-4 text-xs leading-relaxed">
        <div className="flex items-center gap-2 border-b border-[#DCE2EA] dark:border-[#24344D] pb-3">
          <Scale className="w-4 h-4 text-[#C5A059]" />
          <h3 className="text-sm font-bold text-[#172033] dark:text-white">
            Layer 4 — Qualified Human Review & Statutory Framework
          </h3>
        </div>

        <div className="space-y-3 text-[#172033] dark:text-slate-300">
          <p>
            Human review facilitates compliance with <b>ISO/IEC 27037:2012 (Guidelines for identification, collection, acquisition, and preservation of digital evidence)</b>. Examiners record credential descriptions, qualitative context, checklist verification responses, and opinions with explicit confirmation disclosure.
          </p>
          <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-[#172B47]/40 border border-[#DCE2EA] dark:border-[#24344D] text-[11px] space-y-2">
            <h5 className="font-bold text-[#0F1E36] dark:text-[#C5A059]">
              Indian Statutory Context: Section 63 Bharatiya Sakshya Adhiniyam, 2023 (BSA)
            </h5>
            <p className="text-[#657187] dark:text-slate-300 leading-relaxed">
              Under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 (which supersedes the former Section 65B framework of the Indian Evidence Act, 1872), electronic records require certification by the person in lawful control of the device or an authorized expert. Software reports generated by SCSS SATYA provide supporting technical documentation but do not replace an official Section 63 certificate signed by an authorized custodian.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
