export type FindingStatus = 'No Indicator Detected' | 'Indicator Observed' | 'Inconclusive';
export type ReviewStatus = 'Pending Review' | 'Under Review' | 'Reviewed — No Final Opinion' | 'Examiner Opinion Recorded';
export type IntegrityStatus = 'VERIFIED' | 'MISMATCH' | 'UNVERIFIED';

export interface Case {
  id: string;
  case_reference: string;
  title: string;
  purpose?: string | null;
  evidence_source?: string | null;
  investigator?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  evidence_count?: number;
  examination_count?: number;
}

export interface Evidence {
  id: string;
  case_id: string;
  original_filename: string;
  stored_filename: string;
  file_size_bytes: number;
  mime_type: string;
  detected_format: string;
  width?: number | null;
  height?: number | null;
  color_mode?: string | null;
  sha256_hash: string;
  ingestion_timestamp: string;
  is_specimen: boolean;
  specimen_type?: string | null;
  integrity_status?: IntegrityStatus | string;
}

export interface FindingsSummary {
  no_indicator_count: number;
  indicator_observed_count: number;
  inconclusive_count: number;
  total_findings: number;
}

export interface Finding {
  id: string;
  finding_key: string;
  indicator_name: string;
  status: FindingStatus;
  observed_evidence: string;
  explanation: string;
  significance: string;
  limitations: string;
  recommended_action: string;
  order_index: number;
}

export interface ChecklistItem {
  id: string;
  label: string;
  description: string;
  checked: boolean;
  notes?: string | null;
}

export interface ExaminerReview {
  id: string;
  examination_id: string;
  examiner_name: string;
  organization?: string | null;
  qualification?: string | null;
  credential_status: string;
  qualitative_notes?: string | null;
  checklist_responses: ChecklistItem[];
  review_status: ReviewStatus;
  examiner_opinion?: string | null;
  reviewed_at: string;
  updated_at: string;
}

export interface Examination {
  id: string;
  case_id: string;
  evidence_id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  failure_reason?: string | null;
  started_at: string;
  completed_at?: string | null;
  case_reference?: string;
  case_title?: string;
  original_filename?: string;
  detected_format?: string;
  sha256_hash?: string;
  review_status?: ReviewStatus;
  integrity_status?: IntegrityStatus;
  findings_summary?: FindingsSummary;
}

export interface ExaminationDetail extends Examination {
  case: Case;
  evidence: Evidence;
  findings: Finding[];
  review: ExaminerReview | null;
  findings_summary: FindingsSummary;
  has_ela: boolean;
  has_statistics: boolean;
}

export interface ELAResponse {
  format_supported: boolean;
  quality?: number | null;
  scale?: number | null;
  artifact_id?: string | null;
  artifact_url?: string | null;
  grayscale_artifact_url?: string | null;
  notes: string;
  mean_difference?: number | null;
  max_difference?: number | null;
  residual_std?: number | null;
  limitation_statement: string;
}

export interface RGBChannelStat {
  mean: number;
  std_dev: number;
  min: number;
  max: number;
  median: number;
}

export interface HistogramBin {
  bin: number;
  range: string;
  r: number;
  g: number;
  b: number;
}

export interface RGBStatistics {
  red: RGBChannelStat;
  green: RGBChannelStat;
  blue: RGBChannelStat;
  histogram: HistogramBin[];
  total_pixels_sampled: number;
  sampling_method: string;
  interpretation: string;
}

export interface SpatialNoise {
  laplacian_variance: number;
  sobel_gradient_mean: number;
  high_freq_noise_sigma: number;
  method_name: string;
  interpretation: string;
  limitations: string;
}

export interface ImageStatisticsResponse {
  rgb_statistics: RGBStatistics;
  spatial_noise: SpatialNoise;
  dimensions: {
    width: number;
    height: number;
    color_mode: string;
    detected_format: string;
  };
}

export interface MetadataField {
  tag: string;
  label: string;
  value?: string | null;
  status: 'Present' | 'Missing' | 'Unreadable' | 'Unsupported';
  is_software_trace: boolean;
  is_sensitive: boolean;
  notes?: string | null;
}

export interface MetadataCategory {
  name: string;
  fields: MetadataField[];
}

export interface MetadataResponse {
  categories: MetadataCategory[];
  summary: {
    has_exif: boolean;
    software_trace_detected: boolean;
    software_name?: string | null;
    has_gps: boolean;
    gps_coords?: string | null;
    camera_make?: string | null;
    camera_model?: string | null;
    capture_timestamp?: string | null;
  };
  raw_tag_count: number;
  is_unreadable: boolean;
  doctrine_note: string;
}

export interface DashboardMetrics {
  total_examinations: number;
  total_evidence_items: number;
  pending_human_reviews: number;
  completed_examinations: number;
  integrity_failures: number;
  total_cases: number;
}

export interface SystemInfo {
  platform_name: string;
  full_title: string;
  version: string;
  organization: string;
  challenge: string;
  sector: string;
  sub_theme: string;
  doctrine: string;
  python_version: string;
  storage_vault_path: string;
  max_file_size_mb: number;
  max_pixels: number;
  supported_formats: string[];
  disclaimer: string;
}

export interface IntegrityVerificationResult {
  evidence_id: string;
  expected_hash: string;
  recomputed_hash: string;
  status: IntegrityStatus;
  verified_at: string;
  details: string;
  message: string;
}

export interface GeneratedReport {
  id: string;
  examination_id: string;
  report_format: 'PDF' | 'JSON';
  file_size_bytes: number;
  sha256_hash: string;
  download_url: string;
  generated_at: string;
}
