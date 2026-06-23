import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import clsx from "clsx";
import { Navbar } from "../components/Navbar";
import { Card } from "../components/Card";
import { api, extractErrorMessage } from "../lib/api";
import type { AnalysisResult, SubScore } from "../lib/types";
import {
  Sparkles,
  Target,
  TrendingUp,
  CheckCircle2,
  AlertTriangle,
  Briefcase,
  FileEdit,
  GraduationCap,
  MessageSquare,
} from "lucide-react";

const COMPONENT_LABELS: Record<string, string> = {
  skill_match: "Skill match",
  keyword_coverage: "Keyword coverage",
  experience_match: "Experience match",
  education_match: "Education match",
  completeness: "Completeness",
};

export function AnalysisResultPage() {
  const { id } = useParams<{ id: string }>();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadingTool, setLoadingTool] = useState<string | null>(null);

  const [roadmap, setRoadmap] = useState<any>(null);
  const [interviewQuestions, setInterviewQuestions] = useState<any>(null);
  const [recruiterSimulation, setRecruiterSimulation] = useState<any>(null);

  useEffect(() => {
    if (!id) return;
    api.analysis
      .get(Number(id))
      .then(setResult)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, [id]);

  const generateRoadmap = async () => {
    if (!result) return;

    setLoadingTool("roadmap");

    try {
      const data = await api.ai.roadmap(
        result.resume_id,
        result.job_description_id
      );

      setRoadmap(data);
    } finally {
      setLoadingTool(null);
    }
  };

  const generateInterviewQuestions = async () => {
    if (!result) return;

    setLoadingTool("interview");

    try {
      const data = await api.ai.interviewQuestions(
        result.resume_id,
        result.job_description_id
      );

      setInterviewQuestions(data);
    } finally {
      setLoadingTool(null);
    }
  };

  const generateRecruiterSimulation = async () => {
    if (!result) return;

    setLoadingTool("recruiter");

    try {
      const data = await api.ai.recruiterSimulation(
        result.resume_id,
        result.job_description_id
      );

      setRecruiterSimulation(data);
    } finally {
      setLoadingTool(null);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="container-page py-12 flex-1 max-w-4xl">
        {isLoading && <p className="text-slate text-sm">Loading analysis…</p>}

        {error && (
          <div role="alert" className="text-sm text-gap bg-gap-dim border border-gap/20 rounded px-4 py-3">
            {error}
          </div>
        )}

        {result && (
          <>
            <ScoreHeader score={result.overall_score} />

            <div className="grid md:grid-cols-2 gap-4 mt-8">
              {Object.entries(result.score_breakdown).map(([key, sub]) => (
                <ScoreComponentCard key={key} label={COMPONENT_LABELS[key] ?? key} sub={sub} />
              ))}
            </div>

            <SkillGapSection result={result} />
            <Card className="p-8 mt-8">
              <h2 className="text-2xl font-bold mb-6">
                AI Career Tools
              </h2>

              <div className="grid md:grid-cols-3 gap-4">
                <button
                  onClick={generateRecruiterSimulation}
                  className="rounded-3xl border p-6 text-left hover:border-blue-500 transition"
                >
                  <Briefcase className="mb-4 text-blue-600" />
                  <h3 className="font-semibold">
                    Recruiter Simulation
                  </h3>
                  <p className="text-sm text-slate-500 mt-2">
                    View hiring manager feedback.
                  </p>
                </button>

                <button
                  onClick={generateInterviewQuestions}
                  className="rounded-3xl border p-6 text-left hover:border-blue-500 transition"
                >
                  <MessageSquare className="mb-4 text-blue-600" />
                  <h3 className="font-semibold">
                    Interview Questions
                  </h3>
                  <p className="text-sm text-slate-500 mt-2">
                    Generate role-specific questions.
                  </p>
                </button>

                <button
                  onClick={generateRoadmap}
                  className="rounded-3xl border p-6 text-left hover:border-blue-500 transition"
                >
                  <GraduationCap className="mb-4 text-blue-600" />
                  <h3 className="font-semibold">
                    30/60/90 Roadmap
                  </h3>
                  <p className="text-sm text-slate-500 mt-2">
                    Personalized improvement plan.
                  </p>
                </button>
              </div>
            </Card>

            {result.ai_review && <AIReviewSection result={result} />}

            {roadmap && (
              <Card className="p-8 mt-8">
                <h2 className="text-2xl font-bold mb-6">
                  30 / 60 / 90 Day Roadmap
                </h2>

                <div className="grid md:grid-cols-3 gap-6">
                  <div>
                    <h3 className="font-semibold text-blue-600 mb-3">
                      30 Days
                    </h3>

                    {roadmap.plan_30_day.weekly_goals.map(
                      (goal: string, i: number) => (
                        <p key={i} className="text-sm mb-2">
                          • {goal}
                        </p>
                      )
                    )}
                  </div>

                  <div>
                    <h3 className="font-semibold text-violet-600 mb-3">
                      60 Days
                    </h3>

                    {roadmap.plan_60_day.weekly_goals.map(
                      (goal: string, i: number) => (
                        <p key={i} className="text-sm mb-2">
                          • {goal}
                        </p>
                      )
                    )}
                  </div>

                  <div>
                    <h3 className="font-semibold text-green-600 mb-3">
                      90 Days
                    </h3>

                    {roadmap.plan_90_day.weekly_goals.map(
                      (goal: string, i: number) => (
                        <p key={i} className="text-sm mb-2">
                          • {goal}
                        </p>
                      )
                    )}
                  </div>
                </div>
              </Card>
            )}
            {interviewQuestions && (
  <Card className="p-8 mt-8">
    <h2 className="text-2xl font-bold mb-6">
      Interview Questions
    </h2>

    <div className="space-y-6">
      {interviewQuestions.questions.map((q: any, index: number) => (
        <div
          key={index}
          className="border border-slate-200 rounded-2xl p-5"
        >
          <div className="flex gap-3 mb-3">
            <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold">
              {q.category}
            </span>

            <span className="px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold">
              {q.difficulty}
            </span>
          </div>

          <h3 className="font-semibold text-slate-900 mb-3">
            {q.question}
          </h3>

          <div>
            <p className="font-medium mb-2">
              Expected Answer Points
            </p>

            <ul className="space-y-1 text-sm text-slate-600">
              {q.expected_answer_points.map(
                (point: string, i: number) => (
                  <li key={i}>• {point}</li>
                )
              )}
            </ul>
          </div>

          <div className="mt-4 text-sm text-slate-500">
            <strong>Follow-up:</strong>{" "}
            {q.follow_up_question}
          </div>
        </div>
      ))}
    </div>
  </Card>
)}

{recruiterSimulation && (
  <Card className="p-8 mt-8">
    <h2 className="text-2xl font-bold mb-6">
      Recruiter Simulation
    </h2>

    <div className="space-y-5">
      <div>
        <span
          className={`px-4 py-2 rounded-full text-sm font-semibold ${
            recruiterSimulation.would_shortlist
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          }`}
        >
          {recruiterSimulation.would_shortlist
            ? "Shortlisted"
            : "Rejected"}
        </span>
      </div>

      <div>
        <h3 className="font-semibold mb-2">
          Confidence
        </h3>

        <p>{recruiterSimulation.shortlist_confidence}</p>
      </div>

      <div>
        <h3 className="font-semibold mb-2">
          Standout Points
        </h3>

        <ul className="space-y-1">
          {recruiterSimulation.standout_points.map(
            (item: string, i: number) => (
              <li key={i}>• {item}</li>
            )
          )}
        </ul>
      </div>

      <div>
        <h3 className="font-semibold mb-2">
          Concerns
        </h3>

        <ul className="space-y-1">
          {recruiterSimulation.concerns.map(
            (item: string, i: number) => (
              <li key={i}>• {item}</li>
            )
          )}
        </ul>
      </div>

      <div>
        <h3 className="font-semibold mb-2">
          Verdict
        </h3>

        <p className="text-slate-600">
          {recruiterSimulation.verdict_summary}
        </p>
      </div>
    </div>
  </Card>
)}
          </>
        )}
      </div>
    </div>
  );
}


function ScoreHeader({ score }: { score: number }) {
  const rounded = Math.round(score);

  return (
    <Card className="p-10">
      <div className="grid lg:grid-cols-[220px_1fr] gap-8 items-center">
        <div className="flex justify-center">
          <div
            className="
            h-44
            w-44
            rounded-full
            bg-gradient-to-r
            from-blue-600
            to-violet-600
            p-1
            shadow-2xl
          "
          >
            <div
              className="
              h-full
              w-full
              rounded-full
              bg-white
              flex
              flex-col
              items-center
              justify-center
            "
            >
              <div className="text-5xl font-bold text-slate-900">
                {rounded}
              </div>

              <div className="text-xs uppercase tracking-wider text-slate-500">
                ATS Score
              </div>
            </div>
          </div>
        </div>

        <div>
          <div className="badge-pill">
            <Sparkles size={16} />
            Recruiter Analysis
          </div>

          <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900">
            ATS Compatibility Report
          </h1>

          <p className="mt-4 text-slate-600 leading-relaxed max-w-xl">
            Comprehensive analysis of resume quality,
            ATS optimization, skill coverage and
            recruiter readiness.
          </p>
        </div>
      </div>
    </Card>
  );
}


function ScoreComponentCard({
  label,
  sub,
}: {
  label: string;
  sub: SubScore;
}) {
  const rounded = Math.round(sub.score);

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-slate-900">
          {label}
        </h3>

        <span
          className="
          rounded-full
          bg-blue-100
          text-blue-700
          px-3
          py-1
          text-sm
          font-semibold
        "
        >
          {rounded}%
        </span>
      </div>

      <div className="h-3 rounded-full bg-slate-100 overflow-hidden">
        <div
          className="
          h-full
          rounded-full
          bg-gradient-to-r
          from-blue-600
          to-violet-600
        "
          style={{
            width: `${Math.min(
              100,
              Math.max(0, rounded)
            )}%`,
          }}
        />
      </div>

      <p className="mt-4 text-sm text-slate-600 leading-relaxed">
        {sub.explanation}
      </p>
    </Card>
  );
}


function SkillGapSection({ result }: { result: AnalysisResult }) {
  const { matched_skills, missing_skills } = result.skill_gap;
  return (
    <Card className="p-8 mt-8">
      <div className="flex items-center gap-3 mb-6">
        <Target size={20} />
        <h2 className="text-2xl font-bold">
          Skill Gap Analysis
        </h2>
      </div>

      {matched_skills.length > 0 && (
        <div className="mb-4">
          <h3 className="text-xs font-medium text-slate uppercase tracking-wide mb-2">Matched</h3>
          <div className="flex flex-wrap gap-2">
            {matched_skills.map((skill) => (
              <span
                key={skill}
                className="font-mono text-xs px-2.5 py-1 rounded bg-match-dim text-match border border-match/20"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {missing_skills.length > 0 && (
        <div>
          <h3 className="text-xs font-medium text-slate uppercase tracking-wide mb-2">Missing</h3>
          <div className="flex flex-col gap-2">
            {missing_skills.map((m) => (
              <div key={m.skill} className="flex items-start gap-3 text-sm">
                <span
                  className={clsx(
                    "font-mono text-xs px-2.5 py-1 rounded shrink-0 border",
                    m.priority === "High" && "bg-gap-dim text-gap border-gap/20",
                    m.priority === "Medium" && "bg-amber-dim text-amber border-amber/20",
                    m.priority === "Low" && "bg-line text-slate border-line"
                  )}
                >
                  {m.skill}
                </span>
                <span className="text-slate text-xs pt-1">{m.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

function AIReviewSection({ result }: { result: AnalysisResult }) {
  const review = result.ai_review;
  if (!review) return null;

  return (
    <Card className="p-8 mt-8">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <TrendingUp size={22} />
          <h2 className="text-2xl font-bold text-slate-900">
            Recruiter Feedback
          </h2>
        </div>

        {review.source === "mock_fallback" && (
          <span className="text-xs text-slate-500">
            Sample Feedback
          </span>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-3xl bg-green-50 border border-green-100 p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2
              size={18}
              className="text-green-600"
            />

            <span className="font-semibold text-green-800">
              Strengths
            </span>
          </div>

          <ul className="space-y-2 text-sm text-slate-700">
            {review.strengths.map((s, i) => (
              <li key={i}>• {s}</li>
            ))}
          </ul>
        </div>

        <div className="rounded-3xl bg-red-50 border border-red-100 p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle
              size={18}
              className="text-red-600"
            />

            <span className="font-semibold text-red-800">
              Weaknesses
            </span>
          </div>

          <ul className="space-y-2 text-sm text-slate-700">
            {review.weaknesses.map((w, i) => (
              <li key={i}>• {w}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-8 pt-8 border-t border-slate-200">
        <h3 className="font-semibold text-slate-900 mb-3">
          Writing Quality
        </h3>

        <p className="text-slate-600 leading-relaxed">
          {review.writing_quality_feedback}
        </p>
      </div>

      <div className="mt-8 pt-8 border-t border-slate-200">
        <h3 className="font-semibold text-slate-900 mb-3">
          ATS Optimization Suggestions
        </h3>

        <ul className="space-y-2 text-slate-600">
          {review.ats_optimization_suggestions.map(
            (suggestion, i) => (
              <li key={i}>
                • {suggestion}
              </li>
            )
          )}
        </ul>
      </div>
    </Card>
  );
}

