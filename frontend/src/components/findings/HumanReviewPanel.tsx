import React, { useState } from 'react';
import { ExaminerReview, ReviewStatus, ChecklistItem } from '../../types/api';
import { api } from '../../services/api';
import { Badge } from '../common/Badge';
import { Modal } from '../common/Modal';
import { UserCheck, CheckSquare, Save, ShieldAlert, Award } from 'lucide-react';

interface HumanReviewPanelProps {
  examinationId: string;
  initialReview: ExaminerReview | null;
  onReviewUpdated: (updated: ExaminerReview) => void;
}

const DEFAULT_STANDARD_CHECKLIST: ChecklistItem[] = [
  {
    id: "chk_source_context",
    label: "Original Source & Acquisition Context",
    description: "Assess image provenance, transmission history, camera model, and device chain of custody.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_raw_file",
    label: "Camera RAW / Original Master Availability",
    description: "Verify whether original uncompressed camera sensor file (RAW, DNG, CR2, NEF) is available for baseline comparison.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_metadata_consistency",
    label: "Metadata Consistency & Provenance",
    description: "Evaluate EXIF/IPTC/XMP timestamps, make, model, software trace tags, and device consistency.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_compression_history",
    label: "Compression & Generation History",
    description: "Examine recompression characteristics, quantization tables, and potential social media stripping.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_ela_analysis",
    label: "Error Level Analysis (ELA) Contextual Review",
    description: "Evaluate high-contrast edges vs genuine compression anomalies; verify alternative explanations.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_spatial_noise",
    label: "Spatial Noise & Geometry Inspection",
    description: "Inspect channel noise variance, pixel gradients, lighting coherence, and geometric perspective consistency.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_corroborating_evidence",
    label: "Corroborating Records & Multi-Shot Series",
    description: "Cross-reference against surrounding scene captures, burst captures, or independent witness records.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_independent_verification",
    label: "Independent Technical Re-Verification",
    description: "Confirm observations across isolated forensic workstations or complementary algorithmic tools.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_chain_of_custody",
    label: "Chain of Custody & Hash Preservation",
    description: "Validate that SHA-256 evidence record remains unbroken since time of acquisition.",
    checked: false,
    notes: "",
  },
  {
    id: "chk_specialist_referral",
    label: "Specialist Forensic Laboratory Referral",
    description: "Determine if full sensor PRNU, physical optical bench, or judicial forensic laboratory certification is required.",
    checked: false,
    notes: "",
  },
];

export const HumanReviewPanel: React.FC<HumanReviewPanelProps> = ({
  examinationId,
  initialReview,
  onReviewUpdated,
}) => {
  const [examinerName, setExaminerName] = useState(initialReview?.examiner_name || 'Dr. K. Swaminathan');
  const [organization, setOrganization] = useState(initialReview?.organization || 'Sure Clue Scientific Solutions (SCSS)');
  const [qualification, setQualification] = useState(initialReview?.qualification || 'Certified Forensic Document Examiner (CFDE)');
  const [credentialStatus] = useState(initialReview?.credential_status || 'UNVERIFIED');
  const [reviewStatus, setReviewStatus] = useState<ReviewStatus>(
    initialReview?.review_status || 'Pending Review'
  );
  const [qualitativeNotes, setQualitativeNotes] = useState(initialReview?.qualitative_notes || '');
  const [examinerOpinion, setExaminerOpinion] = useState(initialReview?.examiner_opinion || '');
  const [checklist, setChecklist] = useState<ChecklistItem[]>(
    initialReview?.checklist_responses && initialReview.checklist_responses.length > 0
      ? initialReview.checklist_responses
      : DEFAULT_STANDARD_CHECKLIST
  );

  const [isSaving, setIsSaving] = useState(false);
  const [showOpinionDisclosureModal, setShowOpinionDisclosureModal] = useState(false);
  const [disclosureConfirmed, setDisclosureConfirmed] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  const handleChecklistToggle = (index: number) => {
    setChecklist(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], checked: !updated[index].checked };
      return updated;
    });
  };

  const handleChecklistNoteChange = (index: number, note: string) => {
    setChecklist(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], notes: note };
      return updated;
    });
  };

  const handleSave = async (forceConfirmed = false) => {
    // If recording an opinion, must accept explicit disclosure
    if (reviewStatus === 'Examiner Opinion Recorded' && !disclosureConfirmed && !forceConfirmed) {
      setShowOpinionDisclosureModal(true);
      return;
    }

    try {
      setIsSaving(true);
      setSaveSuccessMsg(null);
      const res = await api.updateExaminerReview(examinationId, {
        examiner_name: examinerName,
        organization,
        qualification,
        qualitative_notes: qualitativeNotes,
        review_status: reviewStatus,
        examiner_opinion: examinerOpinion,
        checklist_responses: checklist,
        confirm_opinion_disclosure: true,
      });
      onReviewUpdated(res);
      setSaveSuccessMsg('Human forensic review dossier updated successfully.');
      setTimeout(() => setSaveSuccessMsg(null), 4000);
    } catch (err) {
      alert(`Failed to save examiner review: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsSaving(false);
      setShowOpinionDisclosureModal(false);
    }
  };

  return (
    <div className="bg-white dark:bg-[#111C2E] rounded-xl border border-[#DCE2EA] dark:border-[#24344D] overflow-hidden shadow-xs">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[#DCE2EA] dark:border-[#24344D] bg-[#F8FAFC] dark:bg-[#172B47]/50 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <UserCheck className="w-5 h-5 text-[#C5A059]" />
          <div>
            <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
              Layer 4 — Qualified Human Forensic Review & Opinion
            </h3>
            <p className="text-xs text-[#657187] dark:text-[#94A3B8]">
              Forensic screening tools cannot decide authenticity. A qualified human examiner evaluates context.
            </p>
          </div>
        </div>
        <Badge status={reviewStatus} />
      </div>

      <div className="p-6 space-y-6">
        {/* Examiner Credentials */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div>
            <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
              Examiner Name
            </label>
            <input
              type="text"
              value={examinerName}
              onChange={e => setExaminerName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
            />
          </div>

          <div>
            <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
              Laboratory / Institution
            </label>
            <input
              type="text"
              value={organization}
              onChange={e => setOrganization(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
            />
          </div>

          <div>
            <label className="font-semibold text-[#172033] dark:text-slate-200 block mb-1">
              Qualification & Credentials
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={qualification}
                onChange={e => setQualification(e.target.value)}
                className="flex-1 px-3 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
              />
              <span
                className="px-2 py-1 rounded bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 font-mono text-[10px] whitespace-nowrap"
                title="Institutional credentials remain UNVERIFIED in this prototype."
              >
                {credentialStatus}
              </span>
            </div>
          </div>
        </div>

        {/* Review Status Selector */}
        <div>
          <label className="font-semibold text-xs text-[#172033] dark:text-slate-200 block mb-1.5">
            Human Review Status
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
            {(
              [
                'Pending Review',
                'Under Review',
                'Reviewed — No Final Opinion',
                'Examiner Opinion Recorded',
              ] as ReviewStatus[]
            ).map(st => (
              <button
                key={st}
                type="button"
                onClick={() => setReviewStatus(st)}
                className={`px-3 py-2 rounded-lg border text-left font-medium transition-colors ${
                  reviewStatus === st
                    ? 'bg-[#0F1E36] text-white border-[#0F1E36] dark:bg-[#C5A059] dark:text-slate-900 dark:border-[#C5A059]'
                    : 'bg-white dark:bg-[#152238] border-[#DCE2EA] dark:border-[#24344D] text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {/* Mandatory Manual Verification Checklist */}
        <div className="pt-2 border-t border-[#DCE2EA] dark:border-[#24344D]">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#0F1E36] dark:text-[#C5A059] flex items-center gap-1.5">
              <CheckSquare className="w-4 h-4 text-[#C5A059]" />
              <span>Mandatory Manual Verification Checklist (ISO/IEC 27037 Context)</span>
            </h4>
            <span className="text-xs text-[#657187] dark:text-[#94A3B8]">
              {checklist.filter(c => c.checked).length} of {checklist.length} Completed
            </span>
          </div>

          <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
            {checklist.map((item, idx) => (
              <div
                key={item.id}
                className={`p-3 rounded-lg border text-xs transition-colors ${
                  item.checked
                    ? 'bg-emerald-50/40 border-emerald-200 dark:bg-emerald-950/20 dark:border-emerald-800/40'
                    : 'bg-[#F8FAFC] border-[#DCE2EA] dark:bg-[#152238] dark:border-[#24344D]'
                }`}
              >
                <div className="flex items-start gap-2.5">
                  <input
                    type="checkbox"
                    checked={item.checked}
                    onChange={() => handleChecklistToggle(idx)}
                    className="mt-0.5 w-4 h-4 rounded text-[#C5A059] border-slate-300 focus:ring-[#C5A059] cursor-pointer"
                  />
                  <div className="flex-1">
                    <span className="font-semibold text-[#172033] dark:text-white block">
                      {item.label}
                    </span>
                    <span className="text-[#657187] dark:text-[#94A3B8] text-[11px] block mt-0.5">
                      {item.description}
                    </span>
                    <input
                      type="text"
                      placeholder="Add examiner verification notes..."
                      value={item.notes || ''}
                      onChange={e => handleChecklistNoteChange(idx, e.target.value)}
                      className="mt-2 w-full px-2 py-1 text-[11px] rounded border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Qualitative Technical Notes */}
        <div>
          <label className="font-semibold text-xs text-[#172033] dark:text-slate-200 block mb-1">
            Qualitative Observations & Contextual Forensic Notes
          </label>
          <textarea
            rows={3}
            value={qualitativeNotes}
            onChange={e => setQualitativeNotes(e.target.value)}
            placeholder="Record observations regarding physical camera hardware, scene lighting, or transmission channels..."
            className="w-full px-3 py-2 text-xs rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white"
          />
        </div>

        {/* Examiner Opinion */}
        {reviewStatus === 'Examiner Opinion Recorded' && (
          <div className="p-4 rounded-xl border border-[#C5A059]/40 bg-[#FAF7F0] dark:bg-[#172B47]/40 space-y-2">
            <label className="font-bold text-xs text-[#0F1E36] dark:text-[#C5A059] flex items-center gap-1.5">
              <Award className="w-4 h-4 text-[#C5A059]" />
              <span>Qualified Examiner Forensic Opinion (Disclosed in Official Reports)</span>
            </label>
            <p className="text-[11px] text-[#657187] dark:text-[#94A3B8] italic">
              Note: The opinion below is entered by the authorized forensic examiner, NOT generated by automated software.
            </p>
            <textarea
              rows={3}
              value={examinerOpinion}
              onChange={e => setExaminerOpinion(e.target.value)}
              placeholder="State qualified technical conclusions based on multi-layer screening findings and corroborating evidence..."
              className="w-full px-3 py-2 text-xs rounded-lg border border-[#C5A059]/40 bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white font-medium"
            />
          </div>
        )}

        {/* Actions & Feedback */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
          {saveSuccessMsg ? (
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold">
              ✔ {saveSuccessMsg}
            </span>
          ) : (
            <span className="text-[11px] text-[#657187] dark:text-[#94A3B8]">
              All human review updates are recorded in the local SQLite audit log.
            </span>
          )}

          <button
            onClick={() => handleSave()}
            disabled={isSaving}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-[#0F1E36] hover:bg-[#172B47] text-white text-xs font-semibold shadow-xs border border-[#C5A059]/40 transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4 text-[#C5A059]" />
            <span>{isSaving ? 'Persisting Review...' : 'Save Examiner Review'}</span>
          </button>
        </div>
      </div>

      {/* Opinion Disclosure Confirmation Modal */}
      <Modal
        isOpen={showOpinionDisclosureModal}
        onClose={() => setShowOpinionDisclosureModal(false)}
        title="Confirm Examiner Opinion Disclosure"
        footer={
          <>
            <button
              onClick={() => setShowOpinionDisclosureModal(false)}
              className="px-4 py-2 rounded-lg border border-[#DCE2EA] dark:border-[#24344D] text-xs font-medium text-[#657187] dark:text-[#94A3B8]"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                setDisclosureConfirmed(true);
                handleSave(true);
              }}
              className="px-4 py-2 rounded-lg bg-[#0F1E36] text-white text-xs font-semibold border border-[#C5A059]/40"
            >
              Confirm & Save Opinion
            </button>
          </>
        }
      >
        <div className="space-y-3">
          <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-900 dark:text-amber-200 space-y-2">
            <div className="flex items-center gap-2 font-bold text-sm text-amber-800 dark:text-amber-300">
              <ShieldAlert className="w-4 h-4" />
              <span>Statutory and Forensic Disclosure</span>
            </div>
            <p>
              You are recording a formal <b>Qualified Examiner Opinion</b> for case evidence.
            </p>
            <p>
              By proceeding, you explicitly acknowledge that this opinion is formulated by you as a qualified human practitioner, based on physical and technical context. The SCSS SATYA software acts solely as a screening aid and does NOT validate, certify, or endorse the forensic validity of this opinion.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 dark:bg-[#152238] border border-[#DCE2EA] dark:border-[#24344D] text-xs">
            <span className="font-semibold block mb-1">Proposed Opinion:</span>
            <p className="italic font-mono text-slate-700 dark:text-slate-300">
              "{examinerOpinion || 'No opinion text provided'}"
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
};
