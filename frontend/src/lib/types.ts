// Types mirror backend/schemas/*.py exactly. Keep field names and
// optionality in sync with the Pydantic models — these are the
// contract between frontend and backend.

export interface User {
  id: number;
  email: string;
  full_name: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ContactInfo {
  name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
  location: string | null;
}

export interface EducationEntry {
  institution: string | null;
  degree: string | null;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
  gpa: string | null;
}

export interface ExperienceEntry {
  company: string | null;
  title: string | null;
  start_date: string | null;
  end_date: string | null;
  bullets: string[];
}

export interface ProjectEntry {
  name: string | null;
  description: string | null;
  technologies: string[];
}

export interface ParsedResumeData {
  contact_info: ContactInfo;
  education: EducationEntry[];
  skills: string[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
  certifications: string[];
}

export interface Resume {
  id: number;
  original_filename: string;
  file_type: string;
  parsed_data: ParsedResumeData;
  created_at: string;
}

export interface ParsedJobDescriptionData {
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  qualifications: string[];
  tools: string[];
  experience_required_years: number | null;
}

export interface JobDescription {
  id: number;
  title: string | null;
  company: string | null;
  parsed_data: ParsedJobDescriptionData;
  created_at: string;
}

export interface SubScore {
  score: number;
  weight: number;
  explanation: string;
}

export interface SkillMatchDetail extends SubScore {
  matched: string[];
  missing: string[];
}

export interface ScoreBreakdown {
  skill_match: SkillMatchDetail;
  experience_match: SubScore;
  education_match: SubScore;
  completeness: SubScore;
  keyword_coverage: SubScore;
}

export interface MissingSkill {
  skill: string;
  priority: "High" | "Medium" | "Low";
  reason: string;
}

export interface SkillGap {
  matched_skills: string[];
  missing_skills: MissingSkill[];
  recommended_skills: string[];
}

export interface AIReview {
  strengths: string[];
  weaknesses: string[];
  missing_keywords: string[];
  writing_quality_feedback: string;
  ats_optimization_suggestions: string[];
  source: "openai" | "mock_fallback";
}

export interface AnalysisResult {
  id: number;
  resume_id: number;
  job_description_id: number;
  overall_score: number;
  score_breakdown: ScoreBreakdown;
  skill_gap: SkillGap;
  ai_review: AIReview | null;
  created_at: string;
}

export interface RewriteItem {
  original: string;
  improved: string;
  explanation: string;
}

export interface RewriteResponse {
  rewrites: RewriteItem[];
  source: string;
}

export interface RecruiterSimulationResponse {
  would_shortlist: boolean;
  shortlist_confidence: "High" | "Medium" | "Low";
  standout_points: string[];
  concerns: string[];
  missing_elements: string[];
  competitiveness_assessment: string;
  verdict_summary: string;
  source: string;
}

export interface InterviewQuestion {
  category: "Technical" | "Behavioral" | "Project-Based" | "Resume-Based" | "HR";
  question: string;
  difficulty: "Easy" | "Medium" | "Hard";
  expected_answer_points: string[];
  follow_up_question: string;
}

export interface InterviewQuestionResponse {
  questions: InterviewQuestion[];
  source: string;
}

export interface RoadmapPhase {
  focus: string;
  weekly_goals: string[];
}

export interface RoadmapResponse {
  target_role_summary: string;
  plan_30_day: RoadmapPhase;
  plan_60_day: RoadmapPhase;
  plan_90_day: RoadmapPhase;
  source: string;
}

export interface DashboardData {
  resume_count: number;
  job_description_count: number;
  analysis_count: number;
  interview_question_set_count: number;
  career_roadmap_count: number;
  latest_score: number | null;
  score_trend: { date: string; score: number }[];
  skill_coverage: {
    distinct_matched_skills: string[];
    distinct_missing_skills: string[];
  };
  recent_analyses: { id: number; overall_score: number; created_at: string }[];
  recent_interview_sets: { id: number; question_count: number; created_at: string }[];
  recent_roadmaps: { id: number; target_role: string | null; created_at: string }[];
}

export interface ApiErrorBody {
  detail: string;
}
