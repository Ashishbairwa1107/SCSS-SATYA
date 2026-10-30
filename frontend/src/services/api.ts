import {
  Case,
  Evidence,
  Examination,
  ExaminationDetail,
  Finding,
  ExaminerReview,
  ELAResponse,
  ImageStatisticsResponse,
  MetadataResponse,
  DashboardMetrics,
  SystemInfo,
  IntegrityVerificationResult,
  GeneratedReport,
} from '../types/api';

/**
 * Robust API Base URL resolution supporting:
 * - Vite environment variables (VITE_API_URL or VITE_API_BASE)
 * - Graceful fallback to relative '/api' (for Vite proxy or unified backend serving)
 * - Automatic prevention of duplicate or missing '/api' paths
 */
export function resolveApiBase(): string {
  const metaEnv = typeof import.meta !== 'undefined' ? (import.meta as any).env : undefined;
  const envUrl = (
    (metaEnv && (metaEnv.VITE_API_URL || metaEnv.VITE_API_BASE)) ||
    ''
  ).trim();

  if (!envUrl) {
    return '/api';
  }

  const clean = envUrl.replace(/\/+$/, '');
  return clean.endsWith('/api') ? clean : `${clean}/api`;
}

export const API_BASE = resolveApiBase();

/**
 * Structured API Error containing HTTP status, status text,
 * endpoint URL, and useful backend diagnostics.
 */
export class ApiError extends Error {
  status?: number;
  statusText?: string;
  detail?: string;
  url?: string;
  isNetworkError: boolean;

  constructor(options: {
    message: string;
    status?: number;
    statusText?: string;
    detail?: string;
    url?: string;
    isNetworkError?: boolean;
  }) {
    super(options.message);
    this.name = 'ApiError';
    this.status = options.status;
    this.statusText = options.statusText;
    this.detail = options.detail;
    this.url = options.url;
    this.isNetworkError = Boolean(options.isNetworkError);
  }
}

/**
 * Safe fetch wrapper that intercepts low-level browser network errors
 * (e.g. backend offline, CORS preflight blocked) and provides human-readable context.
 */
async function safeFetch(url: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, init);
  } catch (err: any) {
    const isNetworkErr =
      err instanceof TypeError &&
      (err.message.includes('fetch') ||
        err.message.includes('NetworkError') ||
        err.message.includes('Failed to fetch') ||
        err.message.includes('Load failed'));

    if (isNetworkErr) {
      throw new ApiError({
        message: `Network Connection Failure — Failed to reach screening backend at ${url}.`,
        detail: `The application was unable to establish a connection to the backend server. Please verify that the SCSS SATYA backend server is running on http://127.0.0.1:8000 and that local CORS or firewall rules are not blocking requests.`,
        url,
        isNetworkError: true,
      });
    }
    throw err;
  }
}

async function handleResponse<T>(res: Response, requestUrl?: string): Promise<T> {
  if (!res.ok) {
    let errorDetail = res.statusText || 'Request failed';
    try {
      const errJson = await res.json();
      if (Array.isArray(errJson.detail)) {
        // Formatted FastAPI validation error array
        errorDetail = errJson.detail
          .map((d: any) => {
            const loc = Array.isArray(d.loc)
              ? d.loc.filter((x: any) => x !== 'body').join('.')
              : 'field';
            return `${loc}: ${d.msg}`;
          })
          .join('; ');
      } else if (typeof errJson.detail === 'string') {
        errorDetail = errJson.detail;
      } else if (typeof errJson.message === 'string') {
        errorDetail = errJson.message;
      } else if (typeof errJson.error === 'string') {
        errorDetail = errJson.error;
      } else if (errJson) {
        errorDetail = JSON.stringify(errJson);
      }
    } catch {
      try {
        const text = await res.text();
        if (text) errorDetail = text;
      } catch {
        // Fallback to HTTP statusText
      }
    }

    const fullMsg = `HTTP ${res.status} (${res.statusText || 'Error'}): ${errorDetail}`;
    throw new ApiError({
      message: fullMsg,
      status: res.status,
      statusText: res.statusText,
      detail: errorDetail,
      url: requestUrl || res.url,
      isNetworkError: false,
    });
  }
  return res.json();
}

export const api = {
  // Utility for resolving relative asset URLs against API host
  resolveAssetUrl(path: string | null | undefined): string {
    if (!path) return '';
    if (
      path.startsWith('http://') ||
      path.startsWith('https://') ||
      path.startsWith('blob:') ||
      path.startsWith('data:')
    ) {
      return path;
    }
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    if (API_BASE.startsWith('http://') || API_BASE.startsWith('https://')) {
      try {
        const urlObj = new URL(API_BASE);
        return `${urlObj.origin}${cleanPath}`;
      } catch {
        // fallback to relative path
      }
    }
    return cleanPath;
  },

  // System
  async getHealth() {
    const url = `${API_BASE}/health`;
    const res = await safeFetch(url);
    return handleResponse<{
      status: string;
      version: string;
      timestamp: string;
      doctrine: string;
      database_connected: boolean;
      vault_accessible: boolean;
    }>(res, url);
  },

  async getSystemInfo() {
    const url = `${API_BASE}/system/info`;
    const res = await safeFetch(url);
    return handleResponse<SystemInfo>(res, url);
  },

  async getDashboardMetrics() {
    const url = `${API_BASE}/system/metrics`;
    const res = await safeFetch(url);
    return handleResponse<DashboardMetrics>(res, url);
  },

  // Cases
  async listCases(search?: string, skip = 0, limit = 50) {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    const url = `${API_BASE}/cases?${params.toString()}`;
    const res = await safeFetch(url);
    return handleResponse<Case[]>(res, url);
  },

  async getCase(id: string) {
    const url = `${API_BASE}/cases/${id}`;
    const res = await safeFetch(url);
    return handleResponse<Case>(res, url);
  },

  async createCase(data: Partial<Case>) {
    const url = `${API_BASE}/cases`;
    const res = await safeFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<Case>(res, url);
  },

  // Examinations & Evidence Ingestion
  async createExamination(formData: FormData) {
    const url = `${API_BASE}/examinations`;
    // NOTE: For multipart/form-data with FormData, let browser set boundary automatically!
    const res = await safeFetch(url, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<Examination>(res, url);
  },

  // Alias for evidence registration
  async registerEvidence(formData: FormData) {
    return this.createExamination(formData);
  },

  async listExaminations(params?: {
    search?: string;
    format_filter?: string;
    review_status?: string;
    skip?: number;
    limit?: number;
  }) {
    const query = new URLSearchParams();
    if (params?.search) query.append('search', params.search);
    if (params?.format_filter) query.append('format_filter', params.format_filter);
    if (params?.review_status) query.append('review_status', params.review_status);
    query.append('skip', (params?.skip || 0).toString());
    query.append('limit', (params?.limit || 50).toString());
    const url = `${API_BASE}/examinations?${query.toString()}`;
    const res = await safeFetch(url);
    return handleResponse<Examination[]>(res, url);
  },

  async getExaminationDetail(id: string) {
    const url = `${API_BASE}/examinations/${id}`;
    const res = await safeFetch(url);
    return handleResponse<ExaminationDetail>(res, url);
  },

  async getExaminationFindings(id: string) {
    const url = `${API_BASE}/examinations/${id}/findings`;
    const res = await safeFetch(url);
    return handleResponse<Finding[]>(res, url);
  },

  // Analysis
  async getELAAnalysis(examinationId: string) {
    const url = `${API_BASE}/examinations/${examinationId}/ela`;
    const res = await safeFetch(url);
    return handleResponse<ELAResponse>(res, url);
  },

  async getImageStatistics(examinationId: string) {
    const url = `${API_BASE}/examinations/${examinationId}/statistics`;
    const res = await safeFetch(url);
    return handleResponse<ImageStatisticsResponse>(res, url);
  },

  // Evidence
  async getEvidence(evidenceId: string) {
    const url = `${API_BASE}/evidence/${evidenceId}`;
    const res = await safeFetch(url);
    return handleResponse<Evidence>(res, url);
  },

  async verifyEvidence(evidenceId: string) {
    const url = `${API_BASE}/evidence/${evidenceId}/verify`;
    const res = await safeFetch(url, {
      method: 'POST',
    });
    return handleResponse<IntegrityVerificationResult>(res, url);
  },

  async getEvidenceMetadata(evidenceId: string) {
    const url = `${API_BASE}/evidence/${evidenceId}/metadata`;
    const res = await safeFetch(url);
    return handleResponse<MetadataResponse>(res, url);
  },

  getOriginalEvidenceUrl(evidenceId: string) {
    return `${API_BASE}/evidence/${evidenceId}/original`;
  },

  // Reviews
  async getExaminerReview(examinationId: string) {
    const url = `${API_BASE}/examinations/${examinationId}/review`;
    const res = await safeFetch(url);
    return handleResponse<ExaminerReview>(res, url);
  },

  async updateExaminerReview(
    examinationId: string,
    data: Partial<ExaminerReview> & { confirm_opinion_disclosure?: boolean }
  ) {
    const url = `${API_BASE}/examinations/${examinationId}/review`;
    const res = await safeFetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<ExaminerReview>(res, url);
  },

  // Reports
  async generateReport(examinationId: string, format: 'PDF' | 'JSON') {
    const url = `${API_BASE}/examinations/${examinationId}/reports`;
    const res = await safeFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ report_format: format }),
    });
    return handleResponse<GeneratedReport>(res, url);
  },

  async listReports(examinationId: string) {
    const url = `${API_BASE}/examinations/${examinationId}/reports`;
    const res = await safeFetch(url);
    return handleResponse<GeneratedReport[]>(res, url);
  },

  // Specimens
  async generateSpecimen(type: 'camera-style' | 'spliced-composite' | 'lossless-png') {
    const url = `${API_BASE}/specimens/${type}`;
    const res = await safeFetch(url, {
      method: 'POST',
    });
    return handleResponse<Examination>(res, url);
  },
};
