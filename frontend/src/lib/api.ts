import axios, { type AxiosInstance } from "axios";
import type {
  AnalysisResult,
  DashboardData,
  InterviewQuestionResponse,
  JobDescription,
  RecruiterSimulationResponse,
  Resume,
  RewriteResponse,
  RoadmapResponse,
  TokenResponse,
} from "./types";

const TOKEN_KEY = "ats_access_token";

// sessionStorage (not localStorage) so the token is cleared automatically
// when the browser/tab is closed — requiring a fresh login on next launch.
export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

const client: AxiosInstance = axios.create({
  baseURL: "/api",
});

client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Extracts a readable message from a FastAPI error response, falling
// back to a generic message if the shape is unexpected.
export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (error.response?.status === 401) return "Your session has expired. Please sign in again.";
    if (!error.response) return "Could not reach the server. Check your connection and try again.";
  }
  return "Something went wrong. Please try again.";
}

export const api = {
  auth: {
    register: (email: string, password: string, fullName?: string) =>
      client
        .post<TokenResponse>("/auth/register", { email, password, full_name: fullName || null })
        .then((r) => r.data),
    login: (email: string, password: string) =>
      client.post<TokenResponse>("/auth/login", { email, password }).then((r) => r.data),
  },

  resume: {
    upload: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return client
        .post<Resume>("/resume/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
        .then((r) => r.data);
    },
    list: () => client.get<Resume[]>("/resume").then((r) => r.data),
    get: (id: number) => client.get<Resume>(`/resume/${id}`).then((r) => r.data),
  },

  jobDescription: {
    create: (raw_text: string, title?: string, company?: string) =>
      client
        .post<JobDescription>("/job-description", {
          raw_text,
          title: title || null,
          company: company || null,
        })
        .then((r) => r.data),
    list: () => client.get<JobDescription[]>("/job-description").then((r) => r.data),
    get: (id: number) => client.get<JobDescription>(`/job-description/${id}`).then((r) => r.data),
  },

  analysis: {
    run: (resumeId: number, jobDescriptionId: number, includeAiReview = true) =>
      client
        .post<AnalysisResult>("/analysis/run", {
          resume_id: resumeId,
          job_description_id: jobDescriptionId,
          include_ai_review: includeAiReview,
        })
        .then((r) => r.data),
    get: (id: number) => client.get<AnalysisResult>(`/analysis/${id}`).then((r) => r.data),
    list: () => client.get<AnalysisResult[]>("/analysis").then((r) => r.data),
  },

  ai: {
    rewrite: (contentItems: string[], jobDescriptionId?: number) =>
      client
        .post<RewriteResponse>("/ai/rewrite", {
          content_items: contentItems,
          job_description_id: jobDescriptionId || null,
        })
        .then((r) => r.data),
    recruiterSimulation: (resumeId: number, jobDescriptionId: number) =>
      client
        .post<RecruiterSimulationResponse>("/ai/recruiter", {
          resume_id: resumeId,
          job_description_id: jobDescriptionId,
        })
        .then((r) => r.data),
    interviewQuestions: (resumeId: number, jobDescriptionId: number) =>
      client
        .post<InterviewQuestionResponse>("/ai/interview", {
          resume_id: resumeId,
          job_description_id: jobDescriptionId,
        })
        .then((r) => r.data),
    roadmap: (resumeId: number, jobDescriptionId: number, targetRole?: string) =>
      client
        .post<RoadmapResponse>("/ai/roadmap", {
          resume_id: resumeId,
          job_description_id: jobDescriptionId,
          target_role: targetRole || null,
        })
        .then((r) => r.data),
  },

  dashboard: {
    get: () => client.get<DashboardData>("/dashboard").then((r) => r.data),
  },
};

export default client;
