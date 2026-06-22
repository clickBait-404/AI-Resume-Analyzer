import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import clsx from "clsx";
import { Navbar } from "../components/Navbar";
import { Card } from "../components/Card";
import { api, extractErrorMessage } from "../lib/api";
import type { AnalysisResult, SubScore } from "../lib/types";

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

  useEffect(() => {
    if (!id) return;
    api.analysis
      .get(Number(id))
      .then(setResult)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, [id]);

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

            {result.ai_review && <AIReviewSection result={result} />}
          </>
        )}
      </div>
    </div>
  );
}

function ScoreHeader({ score }: { score: number }) {
  const rounded = Math.round(score);
  const tone = rounded >= 75 ? "match" : rounded >= 50 ? "amber" : "gap";
  return (
    <Card className="p-8 flex items-center gap-6">
      <div
        className={clsx(
          "h-24 w-24 shrink-0 rounded-full flex items-center justify-center font-mono text-3xl font-semibold border-4",
          tone === "match" && "border-match text-match",
          tone === "amber" && "border-amber text-amber",
          tone === "gap" && "border-gap text-gap"
        )}
      >
        {rounded}
      </div>
      <div>
        <h1 className="font-display text-2xl font-medium text-ink">ATS Compatibility Score</h1>
        <p className="mt-1 text-sm text-slate">
          Out of 100, weighted across five explainable components below.
        </p>
      </div>
    </Card>
  );
}

function ScoreComponentCard({ label, sub }: { label: string; sub: SubScore }) {
  const rounded = Math.round(sub.score);
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-medium text-ink text-sm">{label}</h3>
        <span className="font-mono text-sm font-semibold text-ink">{rounded}</span>
      </div>
      <div className="h-1.5 rounded-full bg-line overflow-hidden">
        <div
          className="h-full rounded-full bg-accent"
          style={{ width: `${Math.min(100, Math.max(0, rounded))}%` }}
        />
      </div>
      <p className="mt-2.5 text-xs text-slate leading-relaxed">{sub.explanation}</p>
    </Card>
  );
}

function SkillGapSection({ result }: { result: AnalysisResult }) {
  const { matched_skills, missing_skills } = result.skill_gap;
  return (
    <Card className="p-6 mt-4">
      <h2 className="font-semibold text-ink mb-4">Skill gap</h2>

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
    <Card className="p-6 mt-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-ink">Recruiter feedback</h2>
        {review.source === "mock_fallback" && (
          <span className="text-xs text-slate-light">Sample feedback — connect an OpenAI key for live review</span>
        )}
      </div>

      <div className="grid sm:grid-cols-2 gap-6">
        <div>
          <h3 className="text-xs font-medium text-match uppercase tracking-wide mb-2">Strengths</h3>
          <ul className="text-sm text-slate space-y-1.5 list-disc list-inside">
            {review.strengths.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-xs font-medium text-gap uppercase tracking-wide mb-2">Weaknesses</h3>
          <ul className="text-sm text-slate space-y-1.5 list-disc list-inside">
            {review.weaknesses.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-5 pt-5 border-t border-line">
        <h3 className="text-xs font-medium text-slate uppercase tracking-wide mb-2">Writing quality</h3>
        <p className="text-sm text-slate leading-relaxed">{review.writing_quality_feedback}</p>
      </div>

      <div className="mt-5 pt-5 border-t border-line">
        <h3 className="text-xs font-medium text-slate uppercase tracking-wide mb-2">
          ATS optimization suggestions
        </h3>
        <ul className="text-sm text-slate space-y-1.5 list-disc list-inside">
          {review.ats_optimization_suggestions.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
